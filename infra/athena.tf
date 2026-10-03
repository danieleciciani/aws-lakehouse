# AWS Athena Configuration
# Athena workgroup
resource "aws_athena_workgroup" "lakehouse" {
  name = "${var.project_prefix}-workgroup"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.data_lake.id}/athena-results/"
    }

    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    bytes_scanned_cutoff_per_query = 1000000000  # 1 GB per query (cost control)
  }

  tags = local.tags
}

# Outputs
output "athena_workgroup_name" {
  description = "Athena workgroup name"
  value       = aws_athena_workgroup.lakehouse.name
}
