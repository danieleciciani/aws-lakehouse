# AWS Glue Data Catalog

# Glue database for Iceberg tables
resource "aws_glue_catalog_database" "lakehouse" {
  name = "lakehouse_${replace(var.environment, \"-\", \"_\")}"

  description = "Data lakehouse database for ${var.project_prefix} - ${var.environment}"

  properties = {
    "classification" = "iceberg"
    "iceberg_version" = "1.0"
  }
}

# Outputs
output "glue_database_name" {
  description = "Glue catalog database name"
  value       = aws_glue_catalog_database.lakehouse.name
}

output "glue_database_arn" {
  description = "Glue catalog database ARN"
  value       = "arn:aws:glue:${local.region}:${local.account_id}:catalog/database/${aws_glue_catalog_database.lakehouse.name}"
}
