# SCP Exception Request Guide

## Current Situation

Your trial AWS account is blocked by an Organization-level Service Control Policy.

**Account ID:** 134051030901  
**Organization:** 389425627895  
**Blocking Policy:** arn:aws:organizations::389425627895:policy/o-o2cp9k5vsl/service_control_policy/p-a2msublm

**Error When Attempting Deployment:**
```
AccessDenied: User is not authorized to perform: s3:CreateBucket 
on resource: arn:aws:s3:::lakehouse-uber-demo-134051030901-us-east-1
with an explicit deny in a service control policy
```

---

## Services That Will Be Blocked

The SCP appears to block creation of:
- ✗ S3 buckets
- ✗ IAM roles (possibly)
- ✗ Glue resources (possibly)
- ✗ Other data services

---

## How to Request an Exception

### Step 1: Contact Your AWS Organization Administrator

Send a message to your AWS account administrator (likely someone at your organization's IT/Cloud team):

**Subject:** Request SCP Exception for Data Lakehouse Development

**Message:**
```
I need an exception to the following Service Control Policy to deploy 
a data lakehouse architecture for evaluation purposes:

Organization Policy: 
  arn:aws:organizations::389425627895:policy/o-o2cp9k5vsl/service_control_policy/p-a2msublm

Target Account: 134051030901
Services Needed: S3, AWS Glue, Athena, IAM

Use Case:
  - Development of a cost-controlled data ingestion pipeline
  - Expected cost: <$1/year
  - All infrastructure as code (Terraform)
  - Fully contained in trial account
  - Can be destroyed immediately after testing

Project Details:
  - GitHub: aws-lakehouse-poc (attached)
  - Estimated deployment time: 5 minutes
  - Data size: <1GB (synthetic test data)
  - No production traffic
```

### Step 2: If Using AWS Management Console

If you have access to AWS Organizations console:

1. Navigate to **AWS Organizations** → **Policies** → **Service Control Policies**
2. Find policy: `arn:aws:organizations::389425627895:policy/o-o2cp9k5vsl/service_control_policy/p-a2msublm`
3. Request an exception or modification

### Step 3: If Using Terraform Organization Module

If your organization uses Infrastructure as Code:

```terraform
# Request exception in your organization's Terraform
resource "aws_organizations_policy_exception" "lakehouse_s3" {
  policy_arn      = "arn:aws:organizations::389425627895:policy/o-o2cp9k5vsl/service_control_policy/p-a2msublm"
  account_id      = "134051030901"
  service_principals = [
    "s3.amazonaws.com",
    "glue.amazonaws.com",
    "athena.amazonaws.com",
    "iam.amazonaws.com"
  ]
}
```

### Step 4: Alternative - Use a Different Account

If the SCP cannot be modified, ask your administrator for:
- A **development account** without these restrictions
- Or a **personal AWS account** to use for this POC

---

## While Waiting for Exception

All of the following work **locally without AWS**:

### 1. Generate Mock Data
```bash
python scripts/generate_data.py \
  --passengers 10000 \
  --drivers 1000 \
  --vehicles 1000 \
  --rides 100000 \
  --seed 42
```

### 2. Run Validation Tests
```bash
python -c "
import sys
sys.path.insert(0, 'scripts')
from generate_data import MockDataGenerator
from python.validation import DataValidator

# Generate data
gen = MockDataGenerator(seed=42)
passengers = gen.generate_passengers(100)

# Validate
valid, errors = DataValidator.validate_passenger(passengers[0])
print(f'Validation: {\"PASS\" if valid else \"FAIL\"} - {passengers[0][\"passenger_id\"]}')"
```

### 3. Test Transformations
```bash
python -c "
from python.transformations import SilverTransformations

# Test data cleaning
record = {
    'passenger_id': 'P000001',
    'email': 'JOHN@EXAMPLE.COM',
    'city': '  New York  ',
    'status': 'ACTIVE'
}

result = SilverTransformations.passenger(record)
print(f'Email cleaned: {result[\"email\"]}')
print(f'City stripped: {result[\"city\"]}')
print(f'Status lowered: {result[\"status\"]}')"
```

### 4. Generate Large Test Datasets
```bash
# Generate different scenarios
python scripts/generate_data.py --passengers 1000 --rides 10000
python scripts/generate_data.py --passengers 50000 --rides 500000 --seed 99
```

### 5. Run Full Test Suite
```bash
python -c "
import sys
sys.path.insert(0, 'scripts')
from generate_data import MockDataGenerator
from python.validation import DataValidator

print('Running comprehensive tests...')

# Test 1: Data generation
gen = MockDataGenerator(seed=42)
passengers = gen.generate_passengers(100)
drivers = gen.generate_drivers(20)
vehicles = gen.generate_vehicles(20, [d['driver_id'] for d in drivers])
rides = gen.generate_rides(500, [p['passenger_id'] for p in passengers],
                           [d['driver_id'] for d in drivers],
                           [v['vehicle_id'] for v in vehicles])
print(f'✓ Generated {len(rides)} rides')

# Test 2: Validation
valid_count = 0
for ride in rides:
    is_valid, _ = DataValidator.validate_ride(ride)
    if is_valid:
        valid_count += 1
print(f'✓ {valid_count}/{len(rides)} rides valid ({100*valid_count/len(rides):.1f}%)')

# Test 3: Foreign keys
passenger_ids = {p['passenger_id'] for p in passengers}
for ride in rides:
    assert ride['passenger_id'] in passenger_ids
print(f'✓ All foreign keys valid')
"
```

---

## Timeline Estimates

| Action | Time |
|--------|------|
| Request SCP exception | 1-24 hours |
| Approval/processing | 1-48 hours |
| Deploy infrastructure | 5 minutes |
| Ingest data | 10 minutes |
| Validate end-to-end | 15 minutes |
| **Total to production** | **24-72 hours** |

---

## Talking Points for Your Administrator

**Budget Impact:**
- Monthly cost: ~$0.04 (less than a penny)
- Annual cost: ~$0.47

**Risk Level:** Low
- No production data
- Contained to single trial account
- Can be destroyed with `terraform destroy`
- Fully auditable via CloudTrail

**Infrastructure:**
- S3 bucket (versioning + encryption)
- Glue Catalog (metadata only)
- Athena workgroup (query costs controlled)
- IAM roles (least-privilege)
- Budgets (cost alerts)

**Success Criteria:**
- Infrastructure deploys successfully
- Data ingests without errors
- Queries return correct results
- All resources can be destroyed cleanly

---

## Once Exception is Granted

```bash
# 1. Verify new permissions work
aws s3 mb s3://test-bucket-for-lakehouse
aws s3 rb s3://test-bucket-for-lakehouse

# 2. Deploy full infrastructure
cd infra
terraform init
terraform plan
terraform apply

# 3. Generate and upload data
python scripts/generate_data.py --passengers 1000 --rides 10000
python scripts/upload_raw.py --bucket lakehouse-uber-demo-134051030901-us-east-1

# 4. Run ingestion
bash scripts/run_ingestion.sh

# 5. Query results
python scripts/query_athena.py
```

---

## Support Documents to Share

You can share these files with your AWS administrator:

- `README.md` — Project overview
- `COST_SAFETY.md` — Detailed cost analysis
- `DEPLOYMENT_GUIDE.md` — Deployment procedures
- `PROJECT_STATUS.md` — Current status
- `infra/main.tf` — Infrastructure definition
- `infra/variables.tf` — Configuration parameters

---

## Contact Information

If you need help with the exception request:

1. **Provide them this file** (`SCP_EXCEPTION_REQUEST.md`)
2. **Share the GitHub repository** or attachment
3. **Request timeline:** "Can this be processed in the next 24-48 hours?"

---

## Next Steps

1. **Contact your AWS administrator** with the message in Step 1
2. **While waiting**, continue with local development (see "While Waiting" section)
3. **Once approved**, run the deployment commands in "Once Exception is Granted"

Good luck! The architecture is solid — just need the right AWS permissions to go live.
