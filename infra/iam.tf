# IAM Roles and Policies

# Glue job execution role
resource "aws_iam_role" "glue_job_role" {
  name = "${var.project_prefix}-glue-job-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.tags
}

# Glue job policy: S3 access to data lake
resource "aws_iam_role_policy" "glue_s3_access" {
  name   = "${var.project_prefix}-glue-s3-access"
  role   = aws_iam_role.glue_job_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3DataLakeAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# Glue job policy: Glue Catalog access
resource "aws_iam_role_policy" "glue_catalog_access" {
  name   = "${var.project_prefix}-glue-catalog-access"
  role   = aws_iam_role.glue_job_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "GlueCatalogAccess"
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetTables",
          "glue:CreateTable",
          "glue:UpdateTable",
          "glue:DeleteTable",
          "glue:BatchDeleteTable",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:CreatePartition",
          "glue:DeletePartition",
          "glue:BatchDeletePartition",
          "glue:UpdatePartition"
        ]
        Resource = "*"
      }
    ]
  })
}

# Glue job policy: CloudWatch Logs
resource "aws_iam_role_policy" "glue_logs_access" {
  name   = "${var.project_prefix}-glue-logs-access"
  role   = aws_iam_role.glue_job_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws-glue/*"
      }
    ]
  })
}

# Athena execution role (optional, for queries)
resource "aws_iam_role" "athena_role" {
  name = "${var.project_prefix}-athena-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.tags
}

# Athena policy: S3 and Glue Catalog access
resource "aws_iam_role_policy" "athena_access" {
  name   = "${var.project_prefix}-athena-access"
  role   = aws_iam_role.athena_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3QueryResults"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      },
      {
        Sid    = "GlueCatalogRead"
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions"
        ]
        Resource = "*"
      }
    ]
  })
}

# Outputs
output "glue_job_role_arn" {
  description = "Glue job execution role ARN"
  value       = aws_iam_role.glue_job_role.arn
}

output "athena_role_arn" {
  description = "Athena execution role ARN"
  value       = aws_iam_role.athena_role.arn
}
