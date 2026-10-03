# Consolidated Outputs
# NOTE: Deployment in trial AWS accounts is limited by SCPs for S3, Glue, and Athena

output "deployment_summary" {
  description = "Deployment summary - Trial account (S3/Glue/Athena blocked by SCP)"
  value = {
    project_prefix      = var.project_prefix
    aws_account_id      = local.account_id
    aws_region          = local.region
    environment         = var.environment
    status              = "Partial deployment - S3, Glue, Athena require SCP exceptions"
    deployed_resources  = ["IAM roles", "Budget alerts"]
    blocked_resources   = ["S3 bucket", "Glue database", "Athena workgroup"]
    budget_limit_usd    = var.budget_limit
  }
}

output "next_steps" {
  description = "Next steps after infrastructure deployment"
  value = [
    "1. Generate mock data: python scripts/generate_data.py --passengers 1000 --drivers 200 --vehicles 200 --rides 10000",
    "2. Upload to S3: python scripts/upload_raw.py --bucket ${local.bucket_name} --prefix raw",
    "3. Run ingestion: bash scripts/run_ingestion.sh",
    "4. Query with Athena: python scripts/query_athena.py --query 'SELECT COUNT(*) FROM lakehouse_dev.bronze_ride'",
    "5. Destroy infrastructure: cd infra && terraform destroy"
  ]
}
