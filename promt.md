You are a Senior AWS Solution Architect, Data Architect and DevOps Engineer.

Your task is to design and implement a production-ready AWS data ingestion pipeline for a simple Uber-like domain, using Amazon S3 as the data lake storage layer and Apache Iceberg as the table format.

IMPORTANT:
This project is being developed in an AWS trial account.

The absolute priority is COST SAFETY.

The AWS environment has a maximum theoretical budget of $100, but the target cost is effectively $0.

You MUST NOT deploy or enable infrastructure that can generate unexpected, recurring or high AWS costs.

Before implementing anything, explicitly identify the AWS services you intend to use and explain why they are safe for this trial environment.

Do not use:
- NAT Gateway
- Application Load Balancer
- Network Load Balancer
- RDS
- Aurora
- Redshift
- OpenSearch
- MSK
- Kinesis Data Streams
- EMR
- EC2 instances unless absolutely necessary
- ECS/Fargate
- EKS
- SageMaker
- paid third-party services
- commercial SaaS services
- services requiring a long-running compute resource

Prefer:
- Amazon S3
- AWS Glue Data Catalog
- AWS Glue Jobs only when necessary and with minimal execution time
- Amazon Athena with extremely small datasets and controlled queries
- AWS IAM
- AWS CloudFormation or Terraform
- AWS CloudWatch where appropriate, while avoiding unnecessary log retention/cost
- local Python for mock-data generation
- Apache Iceberg
- PyIceberg or Spark only if required
- AWS CLI
- boto3

The implementation must be production-ready from an architectural, security, IaC, data-quality and operational perspective, while remaining deliberately small and cheap.

Do NOT optimize for massive scale.
Optimize for:
1. correctness
2. security
3. reproducibility
4. maintainability
5. zero/near-zero AWS cost
6. clear separation of environments
7. easy teardown

==================================================
GLOBAL REQUIREMENTS
==================================================

Region:

Use one AWS region consistently.

Before deployment:
- detect the current AWS region
- if no region is configured, use a configurable default
- never deploy resources across multiple regions

Account:
- detect the AWS account ID
- never hard-code account IDs
- never hard-code credentials

Authentication:
- use the AWS CLI credential chain
- never store AWS credentials in source code
- never create IAM users or access keys unless absolutely required
- prefer IAM roles where possible

Infrastructure as Code:
- all AWS infrastructure must be reproducible
- do not manually create AWS resources through the console
- use Terraform OR CloudFormation
- choose one and use it consistently

Naming:
Use a configurable project prefix:

lakehouse-uber-demo

All resources must have deterministic names where AWS allows it.

Tags:
Every supported AWS resource must include:

Project=lakehouse-uber-demo
Environment=dev
ManagedBy=terraform
CostCenter=demo
Owner=data-platform

==================================================
PHASE 0 — COST AND ACCOUNT SAFETY
==================================================

Before creating any infrastructure:

1. Inspect the AWS account configuration.
2. Check:
   - current region
   - account ID
   - available AWS services
   - existing resources relevant to this project
3. Check whether a billing budget exists.
4. If the required permissions allow it, create a $10 AWS Budget alert.

The budget must:
- alert at 50%
- alert at 80%
- alert at 100%

The budget is an alerting mechanism only.

DO NOT deploy anything expensive simply to satisfy the budget requirement.

Create a COST_SAFETY.md document containing:
- services used
- services explicitly avoided
- potential cost sources
- expected cost profile
- cleanup procedure
- commands to destroy the environment

==================================================
PHASE 1 — DOMAIN MODEL
==================================================

Create a minimal Uber-like domain.

Do NOT over-engineer the domain.

Use these entities:

1. passenger
2. driver
3. vehicle
4. ride
5. payment

Relationships:

passenger
    |
    | 1:N
    v
ride <---- driver
  |
  +---- vehicle
  |
  +---- payment

Minimal schemas:

PASSENGER

passenger_id
first_name
last_name
email
phone
signup_timestamp
city
country
status


DRIVER

driver_id
first_name
last_name
signup_timestamp
rating
city
country
status


VEHICLE

vehicle_id
driver_id
make
model
year
vehicle_type
license_plate


RIDE

ride_id
passenger_id
driver_id
vehicle_id
request_timestamp
pickup_timestamp
dropoff_timestamp
pickup_latitude
pickup_longitude
dropoff_latitude
dropoff_longitude
pickup_city
dropoff_city
distance_km
duration_minutes
fare_amount
currency
ride_status


PAYMENT

payment_id
ride_id
payment_timestamp
payment_method
amount
currency
payment_status

Use realistic but completely synthetic data.

Never use real personal data.

==================================================
PHASE 2 — DATA GENERATION
==================================================

Create a Python-based mock data generator.

The generator must run locally.

Do NOT run a continuously running AWS compute service just to generate data.

Use deterministic random generation where possible.

Support:

python generate_data.py --passengers 1000 --drivers 200 --vehicles 200 --rides 10000

The generator must produce:

data/
  passenger/
  driver/
  vehicle/
  ride/
  payment/

Use CSV or JSON as the raw ingestion format.

Prefer JSON Lines or CSV depending on which makes ingestion simpler.

The generator must:
- generate valid foreign keys
- generate realistic timestamps
- generate realistic ride status values
- generate realistic geographic coordinates
- generate realistic fares
- generate payment records only for appropriate rides
- avoid impossible relationships
- support a configurable random seed

Include a README explaining the generated dataset.

==================================================
PHASE 3 — RAW S3 DATA LAKE
==================================================

Create an S3 bucket for the raw layer.

Bucket naming must be deterministic but globally unique.

Example:

lakehouse-uber-demo-<account-id>-<region>

Enable:

- S3 Block Public Access
- S3 Bucket Versioning
- server-side encryption
- lifecycle rules where useful
- deny public access

Use a structure similar to:

s3://bucket/raw/passenger/
s3://bucket/raw/driver/
s3://bucket/raw/vehicle/
s3://bucket/raw/ride/
s3://bucket/raw/payment/

Add ingestion metadata to object paths where appropriate.

Example:

raw/ride/ingestion_date=2026-10-02/

Do not create excessive partitions.

==================================================
PHASE 4 — DATA LAKEHOUSE LAYERS
==================================================

Implement:

RAW
BRONZE
SILVER
GOLD

RAW:
Original immutable files.

BRONZE:
Data represented as Iceberg tables with minimal transformations.

SILVER:
Cleaned and standardized data.

GOLD:
Business-oriented analytical tables.

S3 layout:

s3://bucket/
    raw/
    bronze/
    silver/
    gold/

Iceberg tables should use:

s3://bucket/bronze/<table>/
s3://bucket/silver/<table>/
s3://bucket/gold/<table>/

Use AWS Glue Data Catalog as the catalog.

==================================================
PHASE 5 — ICEBERG
==================================================

Use Apache Iceberg.

Tables:

bronze.passenger
bronze.driver
bronze.vehicle
bronze.ride
bronze.payment

silver.passenger
silver.driver
silver.vehicle
silver.ride
silver.payment

gold.ride_daily_metrics
gold.driver_metrics
gold.city_metrics

Use Iceberg features where appropriate:

- schema evolution
- partition evolution if useful
- ACID transactions
- snapshots
- MERGE/upsert where appropriate

Do not add complexity unless it provides a clear benefit.

Partition strategy:

Do NOT partition by high-cardinality IDs.

For ride-related tables, prefer time-based partitioning such as:

days(request_timestamp)

For aggregate tables use low-cardinality dimensions where appropriate.

Document the partition strategy and explain why.

==================================================
PHASE 6 — INGESTION
==================================================

Implement a simple batch ingestion pattern.

Flow:

LOCAL MOCK DATA
        |
        v
AWS CLI / boto3
        |
        v
S3 RAW
        |
        v
ETL
        |
        v
ICEBERG BRONZE
        |
        v
ICEBERG SILVER
        |
        v
ICEBERG GOLD

The pipeline must be idempotent.

Running the ingestion twice with the same input must not create duplicate records.

Implement ingestion metadata such as:

batch_id
source_file
ingestion_timestamp
record_count
processing_status

Create a simple ingestion manifest or control mechanism.

==================================================
PHASE 7 — ETL
==================================================

Choose the cheapest AWS-native processing mechanism that can reliably create Iceberg tables.

Prefer AWS Glue only when necessary.

If Glue is used:

- use the smallest practical worker configuration
- minimize job runtime
- avoid unnecessary crawlers
- avoid always-on infrastructure
- avoid Glue development endpoints
- avoid unnecessary job retries

The ETL must perform:

1. schema validation
2. null checks
3. type normalization
4. timestamp normalization
5. foreign-key validation
6. duplicate detection
7. basic business-rule validation
8. write to Iceberg

Example ride rules:

- pickup_timestamp >= request_timestamp
- dropoff_timestamp >= pickup_timestamp
- distance_km >= 0
- duration_minutes >= 0
- fare_amount >= 0
- passenger_id must exist
- driver_id must exist
- vehicle_id must exist

Invalid records must be isolated.

Use:

s3://bucket/quarantine/

with:

quarantine/<entity>/...

Do not silently discard invalid data.

==================================================
PHASE 8 — GOLD DATA MODEL
==================================================

Create a small number of analytical tables.

GOLD 1:

ride_daily_metrics

Columns:

date
city
total_rides
completed_rides
cancelled_rides
total_distance_km
total_revenue
avg_fare
avg_distance_km
avg_duration_minutes


GOLD 2:

driver_metrics

Columns:

driver_id
date
completed_rides
total_distance_km
total_revenue
avg_rating


GOLD 3:

city_metrics

Columns:

city
date
total_rides
completed_rides
total_revenue
avg_fare
avg_distance_km

==================================================
PHASE 9 — ATHENA
==================================================

Expose the Iceberg tables through AWS Glue Data Catalog.

Use Athena for SQL analytics.

Create example queries:

1. daily ride volume
2. revenue by city
3. top drivers
4. average fare by city
5. cancellation rate
6. average ride duration
7. distance distribution

IMPORTANT COST RULE:

Do not run large Athena scans.

Use:
- small synthetic datasets
- partition pruning
- SELECT only required columns
- LIMIT when appropriate

Do not create dashboards or continuously running queries.

==================================================
PHASE 10 — SECURITY
==================================================

Implement least privilege.

Create IAM roles/policies for:

- Glue execution
- Athena access if necessary
- deployment

Avoid:

AdministratorAccess
PowerUserAccess

unless temporarily required during initial experimentation.

S3 policy must restrict access to the project bucket.

Enable:

S3 Block Public Access
SSE-S3 encryption
bucket versioning

Do not expose any bucket publicly.

Do not store credentials in Git.

Create:

.gitignore

containing:

.env
.aws/
credentials
*.pem
*.key
terraform.tfstate
terraform.tfstate.*
.terraform/

==================================================
PHASE 11 — DATA QUALITY
==================================================

Implement lightweight data quality checks.

Checks:

PASSENGER
- passenger_id unique
- email format valid
- required fields not null

DRIVER
- driver_id unique
- rating between 0 and 5

VEHICLE
- vehicle_id unique
- driver_id exists

RIDE
- ride_id unique
- passenger exists
- driver exists
- vehicle exists
- timestamps valid
- distance >= 0
- fare >= 0

PAYMENT
- payment_id unique
- ride_id exists
- amount >= 0

Produce a data quality report:

reports/
    data_quality_report.json

Example:

{
  "dataset": "ride",
  "records": 10000,
  "valid_records": 9975,
  "invalid_records": 25,
  "checks": {
    "duplicate_ids": 0,
    "missing_passenger": 0,
    "missing_driver": 0,
    "invalid_timestamps": 10,
    "negative_fares": 0
  }
}

==================================================
PHASE 12 — OBSERVABILITY
==================================================

Implement lightweight observability.

Track:

- pipeline execution status
- records processed
- records rejected
- execution duration
- input files
- output tables

Use CloudWatch only where justified.

Avoid high-volume logging.

Never log:
- credentials
- secrets
- full PII
- complete customer records

Use structured logs.

==================================================
PHASE 13 — INFRASTRUCTURE AS CODE
==================================================

Create:

infra/

with:

Terraform OR CloudFormation.

Recommended structure:

infra/
    main.tf
    variables.tf
    outputs.tf
    iam.tf
    s3.tf
    glue.tf
    athena.tf
    budgets.tf

If Terraform is used:

- remote state is NOT required for this demo
- local state is acceptable
- never commit terraform.tfstate
- provide terraform destroy instructions

Outputs must include:

- S3 bucket name
- Glue database
- Athena workgroup
- AWS region

==================================================
PHASE 14 — CI/CD
==================================================

Create a lightweight CI pipeline configuration.

The pipeline should perform:

1. Python linting
2. Python tests
3. Terraform formatting
4. Terraform validation
5. Terraform plan

Do NOT automatically deploy to production.

Deployment must require an explicit manual step.

==================================================
PHASE 15 — TESTING
==================================================

Create unit tests for:

- data generation
- schema validation
- business rules
- transformations
- aggregation logic

Create an integration test that validates:

S3 RAW
    ->
Iceberg BRONZE
    ->
Iceberg SILVER
    ->
Iceberg GOLD

The integration test must use a very small dataset.

==================================================
PHASE 16 — DISASTER RECOVERY / OPERATIONS
==================================================

Document:

- how to deploy
- how to ingest
- how to query
- how to inspect Iceberg snapshots
- how to recover from a failed ingestion
- how to replay a batch
- how to quarantine invalid data
- how to rollback an Iceberg table
- how to destroy the entire environment

Create:

RUNBOOK.md

==================================================
PHASE 17 — COST CONTROL
==================================================

Create:

COST_CONTROL.md

Include:

1. Services deployed
2. Services intentionally not deployed
3. Expected cost drivers
4. Maximum expected usage
5. Cost-saving configuration
6. Cleanup instructions

The system must be designed so that no service remains continuously running.

The following must NOT exist:

- NAT Gateway
- EC2 instance running 24/7
- RDS
- Redshift cluster
- OpenSearch domain
- MSK cluster
- ECS service
- EKS cluster
- Load Balancer

If any AWS service has a potentially significant cost, explicitly explain it before deployment.

==================================================
PHASE 18 — DEPLOYMENT
==================================================

Before deployment:

1. Run static validation.
2. Run unit tests.
3. Run Terraform/CloudFormation validation.
4. Show the infrastructure plan.
5. Identify any resource that can incur cost.
6. Ask for explicit confirmation before deploying if the plan contains anything that may create non-trivial costs.

Then deploy.

After deployment:

1. Verify S3 bucket.
2. Upload mock data.
3. Run ingestion.
4. Verify Iceberg tables.
5. Run Athena queries.
6. Verify data quality.
7. Verify IAM access.
8. Verify no public S3 access.
9. Verify no unintended running compute resources.

==================================================
PHASE 19 — FINAL VALIDATION
==================================================

Perform an architecture review as a Senior AWS Solution Architect.

Check:

ARCHITECTURE
- Is the architecture coherent?
- Is S3 the correct storage layer?
- Is Iceberg correctly implemented?
- Is Glue Catalog correctly used?

SECURITY
- Is S3 private?
- Is encryption enabled?
- Is IAM least privilege?
- Are credentials protected?

DATA ENGINEERING
- Is ingestion idempotent?
- Is schema evolution supported?
- Are bad records quarantined?
- Are transformations deterministic?

OPERATIONS
- Can the pipeline be replayed?
- Can failures be diagnosed?
- Can the entire environment be destroyed?

COST
- Can any deployed resource unexpectedly generate significant cost?
- Are there any always-on resources?
- Are Athena queries controlled?
- Is Glue usage minimized?

PRODUCTION READINESS
- IaC
- testing
- monitoring
- logging
- data quality
- security
- documentation
- reproducibility

At the end produce:

ARCHITECTURE_REVIEW.md

with:

- architecture overview
- component diagram
- data flow
- security model
- data model
- operational model
- cost model
- known limitations
- production evolution path

==================================================
IMPORTANT ARCHITECTURAL PRINCIPLE
==================================================

Do not over-engineer this solution.

This is a small reference architecture.

The target is:

"Production-ready engineering practices on a very small and inexpensive AWS footprint."

It is NOT:

"Production-scale infrastructure."

The solution should be easy for a Data Architect to understand, deploy, demonstrate and extend.

==================================================
EXECUTION METHOD
==================================================

Execute this project incrementally.

Do NOT implement everything in one step.

Use the following workflow:

STEP 1
Architecture and cost analysis only.

STEP 2
Create repository structure.

STEP 3
Implement mock data generator.

STEP 4
Implement IaC for S3, IAM, Glue Catalog and other strictly necessary resources.

STEP 5
Deploy infrastructure.

STEP 6
Upload raw mock data.

STEP 7
Implement Bronze Iceberg ingestion.

STEP 8
Implement Silver transformations.

STEP 9
Implement Gold transformations.

STEP 10
Implement Athena queries.

STEP 11
Implement data-quality checks.

STEP 12
Implement tests.

STEP 13
Implement operational documentation.

STEP 14
Perform security and cost review.

STEP 15
Perform final end-to-end test.

After every step:

- show what was created
- show files changed
- explain important architectural decisions
- run relevant tests
- identify potential AWS costs
- do not proceed to the next AWS deployment step if a cost risk is identified

Never silently deploy infrastructure.

Never create resources outside Infrastructure as Code.

Never use real customer data.

Never commit credentials or secrets.