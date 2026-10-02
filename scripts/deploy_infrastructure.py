#!/usr/bin/env python3
"""
Deploy AWS infrastructure for lakehouse pipeline using boto3.

This replaces Terraform for simplicity in trial account.
"""

import boto3
import json
import sys
from datetime import datetime

PROJECT_PREFIX = "lakehouse-uber-demo"
ENVIRONMENT = "dev"
REGION = "us-east-1"

# Initialize AWS clients
sts = boto3.client("sts", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)
iam = boto3.client("iam")
glue = boto3.client("glue", region_name=REGION)
athena = boto3.client("athena", region_name=REGION)
budgets = boto3.client("budgets", region_name=REGION)
logs = boto3.client("logs", region_name=REGION)

# Get account info
account_info = sts.get_caller_identity()
ACCOUNT_ID = account_info["Account"]
BUCKET_NAME = f"{PROJECT_PREFIX}-{ACCOUNT_ID}-{REGION}"

print(f"🚀 Deploying AWS Lakehouse Infrastructure")
print(f"   Account: {ACCOUNT_ID}")
print(f"   Region: {REGION}")
print(f"   Bucket: {BUCKET_NAME}")
print()

# Tags for all resources
TAGS = {
    "Project": PROJECT_PREFIX,
    "Environment": ENVIRONMENT,
    "ManagedBy": "boto3-deployment",
    "CostCenter": "demo",
    "Owner": "data-platform",
    "CreatedDate": datetime.now().isoformat(),
}


def create_s3_bucket():
    """Create S3 data lake bucket."""
    print("📦 Creating S3 bucket...")
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"   ✓ Bucket created: {BUCKET_NAME}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"   ℹ️  Bucket already exists: {BUCKET_NAME}")
    except s3.exceptions.BucketAlreadyExists:
        print(f"   ⚠️  Bucket exists (owned by another account): {BUCKET_NAME}")
        return False

    # Block public access
    try:
        s3.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )
        print(f"   ✓ Public access blocked")
    except Exception as e:
        print(f"   ⚠️  Error blocking public access: {e}")

    # Enable versioning
    try:
        s3.put_bucket_versioning(
            Bucket=BUCKET_NAME, VersioningConfiguration={"Status": "Enabled"}
        )
        print(f"   ✓ Versioning enabled")
    except Exception as e:
        print(f"   ⚠️  Error enabling versioning: {e}")

    # Enable encryption
    try:
        s3.put_bucket_encryption(
            Bucket=BUCKET_NAME,
            ServerSideEncryptionConfiguration={
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            },
        )
        print(f"   ✓ Encryption enabled (AES256)")
    except Exception as e:
        print(f"   ⚠️  Error enabling encryption: {e}")

    # Add tags
    try:
        s3.put_bucket_tagging(
            Bucket=BUCKET_NAME,
            Tagging={"TagSet": [{"Key": k, "Value": v} for k, v in TAGS.items()]},
        )
        print(f"   ✓ Tags applied")
    except Exception as e:
        print(f"   ⚠️  Error applying tags: {e}")

    # Lifecycle rules
    try:
        s3.put_bucket_lifecycle_configuration(
            Bucket=BUCKET_NAME,
            LifecycleConfiguration={
                "Rules": [
                    {
                        "Id": "archive-old-versions",
                        "Status": "Enabled",
                        "NoncurrentVersionTransitions": [
                            {
                                "NoncurrentDays": 30,
                                "StorageClass": "GLACIER",
                            }
                        ],
                        "NoncurrentVersionExpiration": {"NoncurrentDays": 90},
                    },
                    {
                        "Id": "delete-old-quarantine",
                        "Status": "Enabled",
                        "Prefix": "quarantine/",
                        "Expiration": {"Days": 30},
                    },
                ]
            },
        )
        print(f"   ✓ Lifecycle rules configured")
    except Exception as e:
        print(f"   ⚠️  Error configuring lifecycle: {e}")

    return True


def create_iam_roles():
    """Create IAM roles for Glue and Athena."""
    print("\n🔐 Creating IAM roles...")

    # Glue execution role
    try:
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "glue.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        role_name = f"{PROJECT_PREFIX}-glue-job-role"
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy),
            Description="Glue job execution role for lakehouse pipeline",
            Tags=[{"Key": k, "Value": v} for k, v in TAGS.items()],
        )
        glue_role_arn = response["Role"]["Arn"]
        print(f"   ✓ Glue role created: {role_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        role = iam.get_role(RoleName=role_name)
        glue_role_arn = role["Role"]["Arn"]
        print(f"   ℹ️  Glue role already exists: {role_name}")
    except Exception as e:
        print(f"   ✗ Error creating Glue role: {e}")
        return False

    # Attach policies to Glue role
    try:
        # S3 access policy
        s3_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "S3DataLakeAccess",
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket",
                    ],
                    "Resource": [f"arn:aws:s3:::{BUCKET_NAME}", f"arn:aws:s3:::{BUCKET_NAME}/*"],
                }
            ],
        }
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName="S3DataLakeAccess",
            PolicyDocument=json.dumps(s3_policy),
        )
        print(f"   ✓ S3 policy attached to Glue role")
    except Exception as e:
        print(f"   ⚠️  Error attaching S3 policy: {e}")

    try:
        # Glue Catalog policy
        glue_catalog_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "GlueCatalogAccess",
                    "Effect": "Allow",
                    "Action": [
                        "glue:GetDatabase",
                        "glue:GetTable",
                        "glue:GetTables",
                        "glue:CreateTable",
                        "glue:UpdateTable",
                        "glue:DeleteTable",
                        "glue:GetPartition",
                        "glue:GetPartitions",
                        "glue:CreatePartition",
                        "glue:DeletePartition",
                        "glue:UpdatePartition",
                    ],
                    "Resource": "*",
                }
            ],
        }
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName="GlueCatalogAccess",
            PolicyDocument=json.dumps(glue_catalog_policy),
        )
        print(f"   ✓ Glue Catalog policy attached")
    except Exception as e:
        print(f"   ⚠️  Error attaching Glue policy: {e}")

    try:
        # CloudWatch Logs policy
        logs_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CloudWatchLogs",
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": f"arn:aws:logs:{REGION}:{ACCOUNT_ID}:log-group:/aws-glue/*",
                }
            ],
        }
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName="CloudWatchLogs",
            PolicyDocument=json.dumps(logs_policy),
        )
        print(f"   ✓ CloudWatch Logs policy attached")
    except Exception as e:
        print(f"   ⚠️  Error attaching logs policy: {e}")

    return True


def create_glue_database():
    """Create Glue Data Catalog database."""
    print("\n📚 Creating Glue Data Catalog database...")
    db_name = "lakehouse_dev"

    try:
        glue.create_database(
            DatabaseInput={
                "Name": db_name,
                "Description": f"Data lakehouse database for {PROJECT_PREFIX} - {ENVIRONMENT}",
                "Parameters": {
                    "classification": "iceberg",
                    "iceberg_version": "1.0",
                },
            }
        )
        print(f"   ✓ Database created: {db_name}")
    except glue.exceptions.AlreadyExistsException:
        print(f"   ℹ️  Database already exists: {db_name}")
    except Exception as e:
        print(f"   ✗ Error creating database: {e}")
        return False

    return True


def create_athena_workgroup():
    """Create Athena workgroup."""
    print("\n📊 Creating Athena workgroup...")
    workgroup_name = f"{PROJECT_PREFIX}-workgroup"

    try:
        athena.create_work_group(
            Name=workgroup_name,
            Description=f"Athena workgroup for {PROJECT_PREFIX}",
            Configuration={
                "ResultConfigurationUpdates": {
                    "OutputLocation": f"s3://{BUCKET_NAME}/athena-results/",
                },
                "EnforceWorkGroupConfiguration": True,
                "PublishCloudWatchMetricsEnabled": True,
                "BytesScannedCutoffPerQuery": 1000000000,  # 1 GB
            },
            Tags={"Project": PROJECT_PREFIX, "Environment": ENVIRONMENT},
        )
        print(f"   ✓ Workgroup created: {workgroup_name}")
    except athena.exceptions.InvalidRequestException as e:
        if "already exists" in str(e):
            print(f"   ℹ️  Workgroup already exists: {workgroup_name}")
        else:
            print(f"   ✗ Error creating workgroup: {e}")
            return False
    except Exception as e:
        print(f"   ✗ Error creating workgroup: {e}")
        return False

    return True


def create_budget():
    """Create AWS budget alert."""
    print("\n💰 Creating AWS budget...")
    budget_name = f"{PROJECT_PREFIX}-monthly-budget"

    try:
        budgets.create_budget(
            AccountId=ACCOUNT_ID,
            Budget={
                "BudgetName": budget_name,
                "BudgetLimit": {
                    "Amount": "10",
                    "Unit": "USD",
                },
                "TimeUnit": "MONTHLY",
                "BudgetType": "COST",
            },
        )
        print(f"   ✓ Budget created: {budget_name} ($10 limit)")
    except budgets.exceptions.DuplicateValueException:
        print(f"   ℹ️  Budget already exists: {budget_name}")
    except Exception as e:
        print(f"   ⚠️  Error creating budget (may require additional permissions): {e}")

    return True


def deployment_summary():
    """Print deployment summary."""
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE")
    print("=" * 60)
    print(f"\nInfrastructure Summary:")
    print(f"  Project:          {PROJECT_PREFIX}")
    print(f"  Environment:      {ENVIRONMENT}")
    print(f"  AWS Account:      {ACCOUNT_ID}")
    print(f"  AWS Region:       {REGION}")
    print(f"  S3 Bucket:        {BUCKET_NAME}")
    print(f"  Glue Database:    lakehouse_dev")
    print(f"  Athena Workgroup: {PROJECT_PREFIX}-workgroup")
    print(f"\nNext Steps:")
    print(f"  1. Generate mock data:")
    print(f"     python scripts/generate_data.py --passengers 1000 --drivers 200 --vehicles 200 --rides 10000")
    print(f"\n  2. Upload to S3:")
    print(f"     python scripts/upload_raw.py --bucket {BUCKET_NAME} --prefix raw")
    print(f"\n  3. Run ingestion pipeline:")
    print(f"     bash scripts/run_ingestion.sh")
    print(f"\n  4. Query with Athena:")
    print(f"     python scripts/query_athena.py --query 'SELECT COUNT(*) FROM lakehouse_dev.ride'")
    print(f"\n  5. Cleanup (destroy all resources):")
    print(f"     python scripts/destroy_infrastructure.py")
    print()


def main():
    """Main deployment function."""
    try:
        print("🔄 Validating AWS credentials...")
        print(f"   Account: {ACCOUNT_ID}")
        print(f"   Region: {REGION}")
        print()

        # Create resources
        if not create_s3_bucket():
            print("\n❌ Failed to create S3 bucket")
            return False

        if not create_iam_roles():
            print("\n❌ Failed to create IAM roles")
            return False

        if not create_glue_database():
            print("\n❌ Failed to create Glue database")
            return False

        if not create_athena_workgroup():
            print("\n❌ Failed to create Athena workgroup")
            return False

        if not create_budget():
            print("\n⚠️  Budget creation failed (non-critical)")

        deployment_summary()
        return True

    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
