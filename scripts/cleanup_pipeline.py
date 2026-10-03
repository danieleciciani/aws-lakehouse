#!/usr/bin/env python3
"""Clean up all Bronze, Silver, Gold layers and tables"""

import boto3
import sys

glue = boto3.client("glue", region_name="eu-north-1")
s3 = boto3.client("s3", region_name="eu-north-1")

BUCKET = "lakehouse-uber-demo-605628228254-eu-north-1"
DB = "lakehouse_dev"

print("=" * 75)
print("🗑️  CLEANUP: Bronze, Silver, Gold layers")
print("=" * 75)

# Delete S3 data
print("\n📁 Deleting S3 data...")
for prefix in ["bronze/", "silver/", "gold/"]:
    print(f"   Cleaning {prefix}...", end="")
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET, Prefix=prefix)

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    s3.delete_object(Bucket=BUCKET, Key=obj['Key'])
        print(" ✓")
    except Exception as e:
        print(f" ✗ ({str(e)[:50]})")

# Delete Glue tables
print("\n🗄️  Deleting Glue tables...")
all_tables = [
    "bronze_driver", "bronze_passenger", "bronze_vehicle", "bronze_ride", "bronze_payment",
    "silver_driver", "silver_passenger", "silver_vehicle", "silver_payment", "silver_ride",
    "gold_daily_ride_metrics", "gold_driver_performance", "gold_passenger_activity"
]

for table_name in all_tables:
    try:
        glue.delete_table(DatabaseName=DB, Name=table_name)
        print(f"   ✓ {table_name}")
    except glue.exceptions.EntityNotFoundException:
        pass  # Table doesn't exist, skip
    except Exception as e:
        print(f"   ⚠️  {table_name}: {str(e)[:50]}")

print("\n" + "=" * 75)
print("✅ CLEANUP COMPLETE - Ready for fresh pipeline run")
print("=" * 75 + "\n")
