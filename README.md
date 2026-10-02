# AWS Lakehouse POC — Uber-like Domain

A production-ready AWS data ingestion pipeline for a simple Uber-like domain, using Amazon S3, Apache Iceberg, and AWS Glue.

**Status:** Work in Progress  
**Cost Target:** ~$0 (trial account)  
**Region:** us-east-1 (configurable)

## Quick Start

```bash
# Generate mock data locally
python scripts/generate_data.py --passengers 1000 --drivers 200 --vehicles 200 --rides 10000

# Deploy infrastructure (Phase 4)
cd infra
terraform plan
terraform apply

# Upload raw data to S3
python scripts/upload_raw.py

# Run ingestion pipeline
bash scripts/run_ingestion.sh
```

## Architecture Overview

```
LOCAL MOCK DATA
        ↓
    S3 RAW
        ↓
ICEBERG BRONZE (AWS Glue)
        ↓
ICEBERG SILVER (AWS Glue)
        ↓
ICEBERG GOLD (AWS Glue)
        ↓
   ATHENA QUERIES
```

## Key Features

- **Production-ready IaC** — Terraform-based infrastructure
- **Cost-safe** — No always-on compute, controlled AWS spend
- **Secure** — Least-privilege IAM, encrypted S3, no public access
- **Data Quality** — Validation checks, quarantine for bad records
- **Reproducible** — Deterministic mock data, idempotent ingestion
- **Observable** — Structured logging, CloudWatch integration
- **Tested** — Unit tests, integration tests, schema validation

## Project Structure

```
.
├── infra/                    # Terraform infrastructure as code
├── scripts/                  # Operational scripts (data gen, upload, queries)
├── python/                   # ETL code, schema, validation, transformations
├── tests/                    # Unit and integration tests
├── data/                     # Generated mock data (git-ignored)
├── reports/                  # Data quality reports
├── README.md
├── COST_SAFETY.md           # Cost analysis and avoidance strategy
├── RUNBOOK.md               # Operational runbook
└── ARCHITECTURE_REVIEW.md   # Final architecture review
```

## Domain Model

**Entities:** Passenger, Driver, Vehicle, Ride, Payment

**Relationships:**
```
Passenger —— 1:N —— Ride
                      ├── Driver
                      ├── Vehicle
                      └── Payment
```

## Data Layers

| Layer | Format | Purpose |
|-------|--------|---------|
| **RAW** | CSV/JSON in S3 | Immutable source data |
| **BRONZE** | Iceberg tables | Minimal transformations, 1:1 with source |
| **SILVER** | Iceberg tables | Cleaned, normalized, validated data |
| **GOLD** | Iceberg tables | Business-oriented analytics tables |

## Development Phases

1. ✅ Architecture & cost analysis
2. ⏳ Repository structure
3. ⏳ Mock data generator
4. ⏳ Infrastructure as Code (S3, Glue Catalog, IAM)
5. ⏳ Deploy infrastructure
6. ⏳ Upload raw data
7. ⏳ Bronze ingestion
8. ⏳ Silver transformations
9. ⏳ Gold transformations
10. ⏳ Athena queries
11. ⏳ Data quality checks
12. ⏳ Tests
13. ⏳ Operational documentation
14. ⏳ Security & cost review
15. ⏳ Final end-to-end validation

## Cost & Safety

- **Target Cost:** $0–$5 (mostly Athena query scans)
- **Budget Alert:** AWS Budget configured for $10 (50%, 80%, 100% alerts)
- **Always-on Resources:** None
- **Data Size:** Small (mock data only)
- **Cleanup:** Single `terraform destroy` command

See [COST_SAFETY.md](COST_SAFETY.md) for detailed cost analysis.

## Configuration

Edit `infra/terraform.tfvars.example` and rename to `terraform.tfvars`:

```hcl
project_prefix = "lakehouse-uber-demo"
aws_region     = "us-east-1"
environment    = "dev"

# Mock data generation
passenger_count = 1000
driver_count    = 200
vehicle_count   = 200
ride_count      = 10000
random_seed     = 42
```

## Commands

```bash
# Generate mock data
python scripts/generate_data.py --passengers 1000 --drivers 200 --vehicles 200 --rides 10000 --seed 42

# Deploy
cd infra && terraform plan && terraform apply

# Upload raw data
python scripts/upload_raw.py

# Run ingestion
bash scripts/run_ingestion.sh

# Query Athena
python scripts/query_athena.py --query "SELECT COUNT(*) FROM silver.ride"

# Destroy (cleanup)
cd infra && terraform destroy
```

## Documentation

- [COST_SAFETY.md](COST_SAFETY.md) — Detailed cost analysis, services avoided, cleanup procedures
- [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) — Architecture overview, security model, data flow
- [RUNBOOK.md](RUNBOOK.md) — Operational procedures, troubleshooting, disaster recovery

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_data_generation.py -v

# Run integration test
pytest tests/test_integration.py -v
```

## Next Steps

1. Generate mock data locally
2. Deploy infrastructure
3. Upload data and run ingestion pipeline
4. Query results with Athena

See [RUNBOOK.md](RUNBOOK.md) for detailed operational procedures.
