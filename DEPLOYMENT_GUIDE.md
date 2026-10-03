# Deployment Guide

## ⚠️ Trial Account Limitation

This trial AWS account has **organization-level Service Control Policies (SCPs)** that block S3 bucket creation and other infrastructure operations.

**Blocking Policy:** `arn:aws:organizations::389425627895:policy/o-o2cp9k5vsl/service_control_policy/p-a2msublm`

**Error:** `User is not authorized to perform: s3:CreateBucket on resource`

---

## How to Deploy

### Option 1: Full AWS Account (Recommended)

If you have a normal AWS account with full IAM permissions:

#### Using Terraform (Recommended)

```bash
cd infra

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan -out=tfplan

# Review the plan (shows exact resources to create)
cat tfplan

# Apply infrastructure
terraform apply tfplan

# Get outputs
terraform output -json
```

**Terraform creates:**
- ✅ S3 bucket (with versioning, encryption, lifecycle rules, public access block)
- ✅ Glue Database (lakehouse_dev)
- ✅ Athena Workgroup (with 1GB query limit)
- ✅ IAM roles for Glue and Athena
- ✅ AWS Budgets with cost alerts
- ✅ CloudWatch Log Groups

**Cost:** ~$0.10/month expected

#### Using Python boto3

```bash
python scripts/deploy_infrastructure.py
```

This does the same thing as Terraform but via Python SDK.

#### Using AWS CLI

```bash
# Create S3 bucket
aws s3 mb s3://lakehouse-uber-demo-ACCOUNT_ID-us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket lakehouse-uber-demo-ACCOUNT_ID-us-east-1 \
  --versioning-configuration Status=Enabled

# Block public access
aws s3api put-public-access-block \
  --bucket lakehouse-uber-demo-ACCOUNT_ID-us-east-1 \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Create Glue database
aws glue create-database \
  --database-input Name=lakehouse_dev,Description="Lakehouse database"

# Create Athena workgroup
aws athena create-work-group \
  --name lakehouse-uber-demo-workgroup \
  --configuration ResultConfigurationaw
Since this trial account has SCP restrictions, you can still:

1. ✅ **Generate mock data locally** (no AWS)
2. ✅ **Run all unit/integration tests locally** (no AWS)
3. ✅ **Develop ETL code locally** (no AWS)
4. ✅ **Create Iceberg tables locally** (using PyIceberg)

**Then migrate everything to a real AWS account for production testing.**

```bash
# Generate mock data (works locally)
python scripts/generate_data.py --passengers 1000 --drivers 200 --vehicles 200 --rides 10000

# Run tests (works locally)
pytest tests/ -v

# Develop transformations (works locally)
python -c "from python.transformations import BronzeTransformations; print('Transformations OK')"
```

---

## Infrastructure Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      AWS Account                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Amazon S3 Data Lake Bucket                  │   │
│  │  (versioning, encryption, lifecycle rules, private)  │   │
│  │                                                        │   │
│  │  ├── raw/                                            │   │
│  │  │   ├── passenger/                                  │   │
│  │  │   ├── driver/                                     │   │
│  │  │   ├── vehicle/                                    │   │
│  │  │   ├── ride/                                       │   │
│  │  │   └── payment/                                    │   │
│  │  │                                                    │   │
│  │  ├── bronze/                                         │   │
│  │  ├── silver/                                         │   │
│  │  ├── gold/                                           │   │
│  │  ├── quarantine/                                     │   │
│  │  └── athena-results/                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌────────────────────────────────────┐                      │
│  │   AWS Glue Data Catalog            │                      │
│  │   (lakehouse_dev database)          │                      │
│  │   - bronze.* Iceberg tables        │                      │
│  │   - silver.* Iceberg tables        │                      │
│  │   - gold.* Iceberg tables          │                      │
│  └────────────────────────────────────┘                      │
│                            ↓                                  │
│  ┌────────────────────────────────────┐                      │
│  │   AWS Glue Jobs (ETL)              │                      │
│  │   - bronze-ingestion               │                      │
│  │   - silver-transformation          │                      │
│  │   - gold-aggregation               │                      │
│  │   (runs on-demand, ~5 min each)    │                      │
│  └────────────────────────────────────┘                      │
│                            ↓                                  │
│  ┌────────────────────────────────────┐                      │
│  │   Amazon Athena                    │                      │
│  │   (SQL queries, 1GB limit per query)│                      │
│  └────────────────────────────────────┘                      │
│                            ↓                                  │
│  ┌────────────────────────────────────┐                      │
│  │   AWS CloudWatch Logs              │                      │
│  │   (minimal logging, 7-day retention)│                      │
│  └────────────────────────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Resource Summary

| Resource | Type | Cost | Status |
|----------|------|------|--------|
| S3 Bucket | Storage | <$0.01/mo | ✅ Defined (Terraform) |
| Glue Catalog | Metadata | Free (1M objects) | ✅ Defined (Terraform) |
| Glue Jobs (3x) | ETL | $0.04-0.50/mo | ✅ Defined (Python) |
| Athena Workgroup | Query | $0.001-0.05/mo | ✅ Defined (Terraform) |
| IAM Roles | Identity | Free | ✅ Defined (Terraform) |
| CloudWatch Logs | Observability | <$0.01/mo | ✅ Defined (Terraform) |
| Budget Alerts | Monitoring | Free | ✅ Defined (Terraform) |

---

## Deployment Checklist

### Before Deployment (Pre-flight)

- [ ] AWS account with S3 permissions (no SCPs blocking)
- [ ] AWS CLI configured with credentials
- [ ] Terraform or boto3 installed
- [ ] Mock data generated locally
- [ ] Tests passing locally

### Deployment Steps

- [ ] Step 1: `terraform init`
- [ ] Step 2: `terraform plan` (review resources)
- [ ] Step 3: Review terraform plan (identify costs)
- [ ] Step 4: `terraform apply` (create resources)
- [ ] Step 5: Verify S3 bucket created and configured
- [ ] Step 6: Verify Glue database created
- [ ] Step 7: Verify Athena workgroup created
- [ ] Step 8: Upload mock data to S3
- [ ] Step 9: Run Glue ETL jobs
- [ ] Step 10: Query results with Athena

### Post-Deployment (Validation)

- [ ] Check S3 bucket exists and is private
- [ ] Check Glue catalog has lakehouse_dev database
- [ ] Check Athena workgroup has query limit
- [ ] Check CloudWatch logs are being written
- [ ] Check no unexpected AWS resources created
- [ ] Monitor AWS Budgets dashboard

---

## Cost Monitoring

### Monthly Cost Estimate

```
S3 Storage:           ~$0.02  (small dataset, ~18MB)
Glue Catalog:         ~$0.00  (free tier)
Glue Jobs:            ~$0.04  (if run once/month)
Athena:               ~$0.01  (if run 5 queries/month)
IAM:                  ~$0.00  (free)
CloudWatch:           ~$0.00  (within free tier)
─────────────────────────────
Total:                ~$0.07/month
```

### Cost Safety

- ✅ No always-on compute (EC2, RDS, etc.)
- ✅ No data transfer charges (in-region only)
- ✅ No additional storage services
- ✅ Glue jobs timeout at 10 minutes
- ✅ Athena has 1GB query limit
- ✅ Budget alerts at $10

---

## Cleanup

### Destroy All Resources

```bash
# Using Terraform
cd infra
terraform destroy

# Using AWS CLI
aws s3 rm s3://lakehouse-uber-demo-ACCOUNT_ID-us-east-1/ --recursive
aws s3 rb s3://lakehouse-uber-demo-ACCOUNT_ID-us-east-1/
aws glue delete-database --name lakehouse_dev
aws athena delete-work-group --work-group lakehouse-uber-demo-workgroup
```

**Terraform is recommended** — it handles all dependencies and cleanup safely.

---

## Troubleshooting

### Issue: "AccessDenied" on S3 bucket creation

**Cause:** Organization-level SCP blocking S3 operations (like in this trial account)

**Solution:**
1. Use a normal AWS account without SCPs
2. Contact AWS support to request SCP exception
3. Deploy to a different organization

### Issue: "AlreadyExistsException" for Glue database

**Cause:** Database already exists from previous run

**Solution:**
```bash
# Delete old database
aws glue delete-database --name lakehouse_dev

# Or: keep it (reuse is fine)
# Just re-run deployment
```

### Issue: Terraform state conflict

**Cause:** Multiple people running `terraform apply`

**Solution:**
```bash
# Use S3 backend (see comments in main.tf)
# Or: use local state with git (single developer)
```

---

## Next Steps

1. **Deploy to a normal AWS account** with full permissions
2. **Upload mock data** to S3 RAW layer
3. **Run Glue ETL jobs** to populate BRONZE/SILVER/GOLD
4. **Query with Athena** to validate results
5. **Monitor costs** via AWS Budgets

All infrastructure code is ready. Just need the right AWS account!
