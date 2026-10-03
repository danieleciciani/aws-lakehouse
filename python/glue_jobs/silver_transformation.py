"""Silver Transformation Glue Job - Iceberg v2 with Job Parameters"""

import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

# Required job parameters: JOB_NAME, BUCKET_NAME, DATABASE_NAME
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET_NAME', 'DATABASE_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

BUCKET = args['BUCKET_NAME']
DB = args['DATABASE_NAME']

# Configure Iceberg catalog
spark.conf.set("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.warehouse", f"s3://{BUCKET}/")
spark.conf.set("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

print("✅ Iceberg configured")

def write_iceberg(df, table_name, partition_by=None):
    """Write DataFrame as Iceberg v2 table, create or replace."""
    location = f"s3://{BUCKET}/silver/{table_name}/"
    table_full = f"glue_catalog.{DB}.silver_{table_name}"

    spark.sql(f"DROP TABLE IF EXISTS {table_full}")

    writer = df.writeTo(table_full) \
        .tableProperty("format-version", "2") \
        .tableProperty("location", location)

    if partition_by:
        writer = writer.partitionedBy(partition_by)

    writer.createOrReplace()
    print(f"  ✓ {table_name}")

print("Starting Silver Transformation")

# ── DRIVER ──────────────────────────────────────────────
print("\n📝 driver...")
driver = spark.read.parquet(f"s3://{BUCKET}/bronze/driver/")
driver_silver = driver \
    .withColumn("signup_timestamp", F.to_timestamp("signup_timestamp")) \
    .withColumn("rating", F.round("rating", 2)) \
    .filter(F.col("status").isin("active", "inactive")) \
    .dropDuplicates(["driver_id"])

write_iceberg(driver_silver, "driver")

# ── PASSENGER ───────────────────────────────────────────
print("📝 passenger...")
passenger = spark.read.parquet(f"s3://{BUCKET}/bronze/passenger/")
passenger_silver = passenger \
    .withColumn("signup_timestamp", F.to_timestamp("signup_timestamp")) \
    .filter(F.col("email").isNotNull()) \
    .dropDuplicates(["passenger_id"])

write_iceberg(passenger_silver, "passenger")

# ── VEHICLE ─────────────────────────────────────────────
print("📝 vehicle...")
vehicle = spark.read.parquet(f"s3://{BUCKET}/bronze/vehicle/")
vehicle_silver = vehicle \
    .filter(F.col("driver_id").isNotNull()) \
    .dropDuplicates(["vehicle_id"])

write_iceberg(vehicle_silver, "vehicle")

# ── PAYMENT ─────────────────────────────────────────────
print("📝 payment...")
payment = spark.read.parquet(f"s3://{BUCKET}/bronze/payment/")
payment_silver = payment \
    .withColumn("payment_timestamp", F.to_timestamp("payment_timestamp")) \
    .filter(F.col("payment_status") == "completed") \
    .filter(F.col("amount") > 0) \
    .dropDuplicates(["payment_id"])

write_iceberg(payment_silver, "payment")

# ── RIDE ────────────────────────────────────────────────
print("📝 ride...")
ride = spark.read.parquet(f"s3://{BUCKET}/bronze/ride/")
ride_silver = ride \
    .withColumn("request_timestamp", F.to_timestamp("request_timestamp")) \
    .withColumn("pickup_timestamp", F.to_timestamp("pickup_timestamp")) \
    .withColumn("dropoff_timestamp", F.to_timestamp("dropoff_timestamp")) \
    .filter(F.col("ride_status").isin("completed", "cancelled")) \
    .filter(F.col("fare_amount") > 0) \
    .filter(F.col("distance_km") > 0) \
    .dropDuplicates(["ride_id"])

write_iceberg(ride_silver, "ride", partition_by=["pickup_city"])

print("\n✅ Silver Transformation complete")
job.commit()
