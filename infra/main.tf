terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Local state is acceptable for demo/dev
  # For production, consider S3 backend with state locking
  # backend "s3" {
  #   bucket         = "terraform-state-bucket"
  #   key            = "lakehouse-uber-demo/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project      = var.project_prefix
      Environment  = var.environment
      ManagedBy    = "terraform"
      CostCenter   = var.cost_center
      Owner        = var.owner
      CreatedDate  = timestamp()
    }
  }
}

# Get current AWS account and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  # Deterministic bucket naming
  bucket_name = "${var.project_prefix}-${local.account_id}-${local.region}"

  # Common tags
  tags = {
    Project      = var.project_prefix
    Environment  = var.environment
    ManagedBy    = "terraform"
    CostCenter   = var.cost_center
    Owner        = var.owner
  }
}

output "account_id" {
  description = "AWS Account ID"
  value       = local.account_id
}

output "region" {
  description = "AWS Region"
  value       = local.region
}

output "bucket_name" {
  description = "S3 bucket name"
  value       = local.bucket_name
}

output "glue_database" {
  description = "Glue catalog database name"
  value       = "lakehouse_dev"
}
