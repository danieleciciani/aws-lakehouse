# S3 Data Lake Bucket
# NOTE: Requires SCP exception - blocked in trial accounts
# See SCP exception request in ../docs/scp-exception-request.md

/*
resource "aws_s3_bucket" "data_lake" {
  bucket = local.bucket_name

  tags = merge(local.tags, {
    Name = "Data Lake - ${var.project_prefix}"
  })

  lifecycle {
    ignore_changes = [tags_all]
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning for safety
resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bucket policy: deny unencrypted uploads
resource "aws_s3_bucket_policy" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyUnencryptedObjectUploads"
        Effect = "Deny"
        Principal = {
          AWS = "*"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.data_lake.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption" = "AES256"
          }
        }
      },
      {
        Sid    = "DenyIncorrectKmsKey"
        Effect = "Deny"
        Principal = {
          AWS = "*"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.data_lake.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption-aws-kms-key-id" = "*"
          }
        }
      }
    ]
  })
}

# Lifecycle rule: archive old versions
resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }

  rule {
    id     = "delete-old-quarantine"
    status = "Enabled"

    filter {
      prefix = "quarantine/"
    }

    expiration {
      days = 30
    }
  }
}

# Output bucket info
output "s3_bucket_name" {
  description = "S3 data lake bucket name"
  value       = aws_s3_bucket.data_lake.id
}

output "s3_bucket_arn" {
  description = "S3 data lake bucket ARN"
  value       = aws_s3_bucket.data_lake.arn
}
*/
