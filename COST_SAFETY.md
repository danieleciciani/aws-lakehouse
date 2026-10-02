# Cost Safety & Budget Analysis

**Date:** 2026-10-02  
**Account ID:** 134051030901  
**Region:** us-east-1  
**Environment:** dev  
**Budget:** $100 max (trial), target $0  

---

## Services Used

### ✅ Free or Near-Zero Cost

| Service | Usage | Cost | Notes |
|---------|-------|------|-------|
| **S3** | <1 GB storage, <10k PUTs | <$0.01/month | Storage only; no data transfer costs within region |
| **IAM** | Roles, policies, identity | Free | No charges for role creation |
| **CloudFormation / Terraform** | State management | Free | Local state file; no S3 backend |
| **Glue Catalog** | Table metadata | Free tier | First 1M objects free |
| **AWS Budgets** | Cost alerts | Free | Alerting only |
| **CloudWatch** | Logs, metrics | Free tier | <5GB logs/month free; we log minimally |

### ⚠️ Pay-per-Use (Controlled)

| Service | Usage | Cost Model | Expected Cost | Mitigation |
|---------|-------|-----------|----------------|-----------|
| **AWS Glue Jobs** | Bronze/Silver/Gold ETL (3 jobs, ~5 min each) | $0.48/DPU-hour | ~$0.12 | Use smallest worker config (G.1X, 2 DPU, 5 min = $0.04/run) |
| **Athena** | Example queries on small dataset | $5.00 / TB scanned | $0–$0.05 | Small dataset (10k rides), partition pruning, SELECT only columns needed |

### 🚫 Services NOT Deployed

| Service | Reason |
|---------|--------|
| **NAT Gateway** | No bastion/jumphost needed; no internet egress required |
| **ALB / NLB** | No APIs or services exposed; pipeline is batch |
| **RDS / Aurora** | Use S3 + Iceberg instead of relational database |
| **Redshift** | Iceberg via Athena is sufficient for demo scale |
| **OpenSearch** | No full-text search; Athena for SQL queries |
| **MSK** | No streaming; batch ingestion only |
| **Kinesis** | No real-time; batch ingestion only |
| **EMR** | Glue Jobs sufficient; EMR would be overkill |
| **EC2** | No always-on compute; Glue Jobs are serverless |
| **ECS / Fargate** | Glue Jobs + Lambda (if needed) for batch work |
| **EKS** | Over-engineered for this scale |
| **SageMaker** | No ML/model training; data pipeline only |
| **QuickSight** | No dashboards; Athena for ad-hoc queries |

---

## Cost Breakdown

### Month 1 (Setup & Initial Run)

```
S3 Storage              $0.02    (10 CSV files, <100MB total)
Glue Catalog            $0.00    (free tier)
Glue Jobs (3 runs)      $0.12    (3 jobs × $0.04/run)
Athena (10 queries)     $0.05    (50GB scanned max)
IAM                     $0.00    (free)
CloudWatch              $0.00    (within free tier)
Budget Alerts           $0.00    (free)
─────────────────────────────
TOTAL                   $0.19
```

### Ongoing (Monthly)

```
S3 Storage              $0.01    (versioning, minimal overhead)
Glue Catalog            $0.00    (free tier)
Glue Jobs (1 run/month) $0.04    (single batch job)
Athena (5 queries/month) $0.03   (25GB scanned)
─────────────────────────────
TOTAL                   $0.08/month
```

### 12-Month Projection

```
Initial setup (month 1):  $0.19
Ongoing (months 2–12):    $0.96
─────────────────────────────
Annual total:             ~$1.15
```

---

## Detailed Cost Analysis

### AWS Glue Jobs

**Configuration:**
- Worker type: G.1X (1 DPU = 4GB RAM, 2 vCPU)
- Workers: 2 (default minimum)
- Timeout: 10 minutes per job

**Calculation:**
```
Price = $0.48 / DPU-hour
Cost per run = 2 DPU × (5 min / 60) × $0.48
            = 2 × 0.0833 × $0.48
            = $0.04 per job
```

**Frequency:**
- Initial ingestion: 3 jobs (bronze, silver, gold) = $0.12
- Weekly replay: 3 jobs × 4 weeks = $0.48/month
- Total: ~$0.50/month

### Amazon Athena

**Configuration:**
- Data scanned: 10k ride records + metadata
- Query complexity: Simple SELECT with WHERE/GROUP BY
- Estimated data per query: 5–50 MB

**Calculation:**
```
Price = $5.00 / TB scanned
Query cost = (50 MB / 1,000,000 MB) × $5.00
           = $0.00025 per query
```

**Frequency:**
- Development/testing: 10 queries/month = $0.0025
- Total: ~$0.003/month

### Amazon S3

**Configuration:**
- Versioning: Enabled (minimal overhead)
- Encryption: SSE-S3 (no extra cost)
- Lifecycle rules: Glacier after 90 days (saves storage)

**Calculation:**
```
Storage cost = (1 GB × 12 months) × $0.023/GB/month
             = $0.276/year
             = $0.023/month
```

### AWS Glue Data Catalog

**Free Tier:** 1M objects free  
**Our usage:** ~20 tables = free

---

## Potential Cost Risks & Mitigations

### Risk 1: Uncontrolled Athena Scans
**Mitigation:**
- Small dataset (10k records max)
- Always use LIMIT in exploratory queries
- Partition pruning on time columns
- Never run SELECT * on large tables

### Risk 2: S3 Requests Exceed Free Tier
**Mitigation:**
- One-time bulk upload, not streaming
- Batch jobs run weekly or on-demand
- No logging to S3 (use CloudWatch)

### Risk 3: Glue Job Worker Count Misconfiguration
**Mitigation:**
- Set G.1X with 2 workers (minimum)
- Timeout: 10 minutes (auto-kill runaway jobs)
- Monitor job execution time
- Use Glue Catalog crawler only if necessary (can be expensive)

### Risk 4: Versioning Overhead
**Mitigation:**
- Enable versioning for safety
- Use lifecycle rule to age out old versions
- S3 storage cost still minimal (<$0.01/month)

### Risk 5: CloudWatch Log Retention
**Mitigation:**
- Log retention: 7 days (default)
- Structured logs only (no verbose application logs)
- Pipeline logs go to S3 quarantine/ prefix (not CloudWatch)

### Risk 6: Accidental EC2/RDS Deployment
**Mitigation:**
- IaC only (Terraform)
- No manual console deployments
- IAM policy restricts EC2/RDS creation
- Pre-deployment review of terraform plan

---

## Data Size Expectations

### Raw Data Volume

```
Passengers:    1,000 records × 200 bytes  = 200 KB
Drivers:       200 records   × 180 bytes  = 36 KB
Vehicles:      200 records   × 150 bytes  = 30 KB
Rides:         10,000 records × 400 bytes = 4 MB
Payments:      8,000 records × 200 bytes  = 1.6 MB
─────────────────────────────────────────────
TOTAL RAW                                  ≈ 5.9 MB
```

### Iceberg Metadata Overhead

```
Bronze layer (1:1 with raw):               6 MB
Silver layer (normalized):                 6 MB
Gold layer (aggregated):                   0.1 MB
─────────────────────────────────────────────
TOTAL STORED                               ≈ 18 MB
```

### S3 Versioning Overhead

```
Max versions per table: 10
Storage with versioning: 18 MB × 1.1 = 20 MB
```

---

## Budget Alerts

**AWS Budget Configured:**
- Threshold 1: Alert at 50% ($5.00)
- Threshold 2: Alert at 80% ($8.00)
- Threshold 3: Alert at 100% ($10.00)
- Notification: Email to data-platform team

**Procedure on Alert:**
1. Check Glue Job CloudWatch metrics
2. Verify Athena query scans
3. Review S3 request counts
4. Investigate any unplanned resources
5. If needed, pause ingestion and investigate

---

## Safe Practices

✅ **DO:**
- Run Glue Jobs manually (on-demand)
- Test Athena queries on small partitions first
- Review terraform plan before apply
- Use time-based S3 lifecycle rules
- Enable S3 versioning for rollback capability
- Log all ingestion to S3 quarantine/ prefix
- Tag all resources with Project/Environment/CostCenter

❌ **DO NOT:**
- Create always-on EC2/RDS instances
- Enable CloudTrail (unless needed for audit)
- Store logs in CloudWatch with high retention
- Deploy to multiple regions
- Create NAT Gateways or Load Balancers
- Enable Glue Data Catalog crawlers (run manually only)
- Run Athena queries on full tables without LIMIT
- Store real customer data in S3

---

## Cleanup Procedure

### Full Environment Teardown

```bash
# 1. Delete S3 data (if any exists)
aws s3 rm s3://lakehouse-uber-demo-134051030901-us-east-1/ --recursive

# 2. Destroy Terraform infrastructure
cd infra
terraform destroy

# 3. Verify deletion
aws s3 ls | grep lakehouse-uber-demo
aws glue get-databases

# 4. Check CloudWatch Logs (should be empty)
aws logs describe-log-groups | grep lakehouse-uber-demo
```

### Terraform Destroy

```bash
cd infra
terraform plan -destroy
terraform destroy
```

This will remove:
- S3 bucket (including all versions)
- Glue database and catalog entries
- IAM roles and policies
- CloudWatch log groups
- CloudFormation stacks (if any)

**Important:** `terraform destroy` will **permanently delete** the S3 bucket and all data. Ensure you have backups if needed.

---

## Cost Monitoring Commands

```bash
# Check Glue Job execution history
aws glue list-jobs --query 'JobNames[]'
aws glue get-job-runs --job-name bronze_ingestion \
  --query 'JobRuns[].{Name:JobName,Status:JobRunState,StartTime:StartedOn}' \
  --output table

# Check Athena query costs (scanned data)
aws athena list-query-executions \
  --query 'QueryExecutionIds[]' | head -5

# Check S3 bucket size
aws s3api head-bucket --bucket lakehouse-uber-demo-134051030901-us-east-1
aws s3 ls s3://lakehouse-uber-demo-134051030901-us-east-1/ \
  --recursive --summarize

# Check CloudWatch Logs volume
aws logs describe-log-groups \
  --query 'logGroups[?contains(logGroupName, `lakehouse`)]'
```

---

## Monthly Cost Review Checklist

- [ ] AWS Budgets: No alerts triggered
- [ ] Glue Jobs: Completed within expected runtime
- [ ] Athena: Queries scanned <100 GB total
- [ ] S3: No unexpected object count increase
- [ ] IAM: No new principals created
- [ ] CloudWatch: Log groups within retention policy
- [ ] EC2/RDS: No instances running
- [ ] Networking: No NAT Gateway/ALB charges

---

## Conclusion

This architecture is explicitly designed to minimize AWS costs while maintaining production-readiness. The total monthly cost should remain under **$0.10**, and the annual cost under **$2.00**.

The primary cost drivers are:
1. **Glue Jobs** (~$0.04–$0.50/month depending on frequency)
2. **Athena** (~$0.001–$0.05/month depending on query volume)
3. **S3** (~$0.02/month for storage)

All other services are free within the scope of this project.

**If at any point a cost alert is triggered, immediately stop all pipelines and investigate.**
