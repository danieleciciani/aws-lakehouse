"""Bronze Ingestion Glue Job - Parquet Format (simple, reliable)."""

import sys
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ["JOB_NAME", "BUCKET_NAME", "DATABASE_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

BUCKET_NAME = args.get("BUCKET_NAME")
DATABASE_NAME = args.get("DATABASE_NAME", "lakehouse_dev")
S3_PREFIX = f"s3://{BUCKET_NAME}"

print(f"Starting Bronze Ingestion (Parquet)")
print(f"Database: {DATABASE_NAME}")
print(f"Bucket: {BUCKET_NAME}\n")

entities = ["passenger", "driver", "vehicle", "ride", "payment"]

for entity in entities:
    print(f"Processing {entity}...")

    raw_path = f"{S3_PREFIX}/raw/{entity}/"
    bronze_path = f"{S3_PREFIX}/bronze/{entity}/"

    # Read from raw (JSONL)
    df = spark.read.json(f"{raw_path}*.jsonl")

    # Write as Parquet
    df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(bronze_path)

    print(f"  ✓ Written {bronze_path}")

print("\n✅ Bronze Ingestion completed")
job.commit()
