# Consolidated Outputs

output "deployment_summary" {
  description = "Deployment summary"
  value = {
    project_prefix      = var.project_prefix
    aws_account_id      = local.account_id
    aws_region          = local.region
    environment         = var.environment
    s3_bucket_name      = local.bucket_name
    glue_database_name  = aws_glue_catalog_database.lakehouse.name
    athena_workgroup    = aws_athena_workgroup.lakehouse.name
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
