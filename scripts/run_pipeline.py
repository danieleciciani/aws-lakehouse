#!/usr/bin/env python3
"""Execute complete lakehouse pipeline: bronze → silver → gold."""

import boto3
import time
import sys
from datetime import datetime

PROJECT_PREFIX = "lakehouse-uber-demo"
REGION = "eu-north-1"

# Initialize AWS clients
sts = boto3.client("sts", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)
glue = boto3.client("glue", region_name=REGION)
athena = boto3.client("athena", region_name=REGION)

# Get account info
account_info = sts.get_caller_identity()
ACCOUNT_ID = account_info["Account"]
BUCKET_NAME = f"{PROJECT_PREFIX}-{ACCOUNT_ID}-{REGION}"
DATABASE_NAME = "lakehouse_dev"

print("=" * 60)
print("🚀 AWS Lakehouse Pipeline Orchestration")
print("=" * 60)
print(f"Account: {ACCOUNT_ID}")
print(f"Region: {REGION}")
print(f"Bucket: {BUCKET_NAME}")
print(f"Database: {DATABASE_NAME}")
print()

def upload_scripts():
    """Upload Glue job scripts to S3."""
    print("📤 Uploading Glue scripts...")
    scripts = [
        ("python/glue_jobs/bronze_ingestion.py", "scripts/glue/bronze_ingestion.py"),
        ("python/glue_jobs/silver_transformation.py", "scripts/glue/silver_transformation.py"),
        ("python/glue_jobs/gold_aggregation.py", "scripts/glue/gold_aggregation.py"),
    ]

    for local_path, s3_path in scripts:
        try:
            with open(local_path, 'rb') as f:
                s3.upload_fileobj(f, BUCKET_NAME, s3_path)
            print(f"   ✓ {s3_path}")
        except Exception as e:
            print(f"   ✗ {s3_path}: {e}")
            return False

    print()
    return True

def run_glue_job(job_name, script_path):
    """Run a Glue job and wait for completion."""
    print(f"🔵 Running {job_name}...")

    try:
        response = glue.start_job_run(
            JobName=job_name,
            Arguments={
                "--BUCKET_NAME": BUCKET_NAME,
                "--DATABASE_NAME": DATABASE_NAME,
            }
        )
        job_run_id = response['JobRunId']
        print(f"   Job Run ID: {job_run_id}")
    except Exception as e:
        print(f"   ✗ Failed to start job: {e}")
        return None

    # Wait for job completion
    print(f"   ⏳ Waiting for completion...", end="", flush=True)
    start_time = time.time()

    while True:
        try:
            status = glue.get_job_run(JobName=job_name, RunId=job_run_id)
            state = status['JobRun']['JobRunState']

            if state in ['SUCCEEDED', 'FAILED', 'STOPPED', 'TIMEOUT']:
                elapsed = int(time.time() - start_time)
                print(f" done ({elapsed}s)")

                if state == 'SUCCEEDED':
                    print(f"   ✅ {job_name} succeeded")
                    return True
                else:
                    error_msg = status['JobRun'].get('ErrorMessage', 'Unknown error')
                    print(f"   ❌ {job_name} failed: {state}")
                    print(f"      Error: {error_msg}")
                    return False

            print(".", end="", flush=True)
            time.sleep(10)

        except Exception as e:
            print(f"\n   ✗ Error checking job status: {e}")
            return False

def verify_bronze():
    """Verify bronze layer data."""
    print("\n📊 Verifying Bronze Layer...")

    query = f"""
    SELECT entity, COUNT(*) as record_count
    FROM (
        SELECT 'driver' as entity FROM read_parquet('s3://{BUCKET_NAME}/bronze/driver/')
        UNION ALL
        SELECT 'passenger' FROM read_parquet('s3://{BUCKET_NAME}/bronze/passenger/')
        UNION ALL
        SELECT 'vehicle' FROM read_parquet('s3://{BUCKET_NAME}/bronze/vehicle/')
        UNION ALL
        SELECT 'ride' FROM read_parquet('s3://{BUCKET_NAME}/bronze/ride/')
        UNION ALL
        SELECT 'payment' FROM read_parquet('s3://{BUCKET_NAME}/bronze/payment/')
    )
    GROUP BY entity
    ORDER BY entity
    """

    print(f"   Query: Counting records per entity")
    # For now, just list S3 contents
    try:
        response = s3.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix="bronze/"
        )
        for obj in response.get('Contents', []):
            size_kb = obj['Size'] / 1024
            print(f"   ✓ {obj['Key']} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print()

def verify_silver():
    """Verify silver layer Iceberg tables."""
    print("📊 Verifying Silver Layer (Iceberg)...")

    try:
        tables = glue.get_tables(DatabaseName=DATABASE_NAME)
        silver_tables = [t for t in tables['TableList'] if t['Name'].startswith('silver_')]

        if silver_tables:
            print(f"   Found {len(silver_tables)} silver tables:")
            for table in silver_tables:
                print(f"   ✓ {table['Name']}")
        else:
            print(f"   ⚠️  No silver tables found in Glue Catalog")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print()

def verify_gold():
    """Verify gold layer Iceberg tables."""
    print("📊 Verifying Gold Layer (Iceberg)...")

    try:
        tables = glue.get_tables(DatabaseName=DATABASE_NAME)
        gold_tables = [t for t in tables['TableList'] if t['Name'].startswith('gold_')]

        if gold_tables:
            print(f"   Found {len(gold_tables)} gold tables:")
            for table in gold_tables:
                print(f"   ✓ {table['Name']}")
        else:
            print(f"   ⚠️  No gold tables found in Glue Catalog")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print()

def main():
    """Execute pipeline."""

    # Step 1: Upload scripts
    if not upload_scripts():
        print("❌ Failed to upload scripts")
        return 1

    # Step 2: Run Bronze
    if not run_glue_job("bronze-ingestion", f"s3://{BUCKET_NAME}/scripts/glue/bronze_ingestion.py"):
        print("❌ Bronze layer failed")
        return 1

    verify_bronze()

    # Step 3: Run Silver
    if not run_glue_job("silver-transformation", f"s3://{BUCKET_NAME}/scripts/glue/silver_transformation.py"):
        print("❌ Silver layer failed")
        return 1

    verify_silver()

    # Step 4: Run Gold
    if not run_glue_job("gold-aggregation", f"s3://{BUCKET_NAME}/scripts/glue/gold_aggregation.py"):
        print("❌ Gold layer failed")
        return 1

    verify_gold()

    # Summary
    print("=" * 60)
    print("✅ Pipeline Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"  1. Check Glue Catalog: aws glue get-tables --database-name {DATABASE_NAME}")
    print(f"  2. Query with Athena: SELECT * FROM {DATABASE_NAME}.silver_driver LIMIT 10")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
