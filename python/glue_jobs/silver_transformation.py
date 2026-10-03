"""Silver Transformation Glue Job - Read Bronze, Transform, Write Parquet."""

import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET_NAME', 'DATABASE_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

BUCKET = args['BUCKET_NAME']
DB = args['DATABASE_NAME']

print(f"Starting Silver Transformation")

# ── DRIVER ──────────────────────────────────────────────
print("Transforming driver...")
driver = spark.read.parquet(f"s3://{BUCKET}/bronze/driver/")
driver_silver = driver \
    .withColumn("signup_timestamp", F.to_timestamp("signup_timestamp")) \
    .withColumn("rating", F.round("rating", 2)) \
    .filter(F.col("status").isin("active", "inactive")) \
    .dropDuplicates(["driver_id"])

driver_silver.write.mode("overwrite").parquet(f"s3://{BUCKET}/silver/driver/")
print("  ✓ silver_driver written")

# ── PASSENGER ───────────────────────────────────────────
print("Transforming passenger...")
passenger = spark.read.parquet(f"s3://{BUCKET}/bronze/passenger/")
passenger_silver = passenger \
    .withColumn("signup_timestamp", F.to_timestamp("signup_timestamp")) \
    .filter(F.col("email").isNotNull()) \
    .dropDuplicates(["passenger_id"])

passenger_silver.write.mode("overwrite").parquet(f"s3://{BUCKET}/silver/passenger/")
print("  ✓ silver_passenger written")

# ── VEHICLE ─────────────────────────────────────────────
print("Transforming vehicle...")
vehicle = spark.read.parquet(f"s3://{BUCKET}/bronze/vehicle/")
vehicle_silver = vehicle \
    .filter(F.col("driver_id").isNotNull()) \
    .dropDuplicates(["vehicle_id"])

vehicle_silver.write.mode("overwrite").parquet(f"s3://{BUCKET}/silver/vehicle/")
print("  ✓ silver_vehicle written")

# ── PAYMENT ─────────────────────────────────────────────
print("Transforming payment...")
payment = spark.read.parquet(f"s3://{BUCKET}/bronze/payment/")
payment_silver = payment \
    .withColumn("payment_timestamp", F.to_timestamp("payment_timestamp")) \
    .filter(F.col("payment_status") == "completed") \
    .filter(F.col("amount") > 0) \
    .dropDuplicates(["payment_id"])

payment_silver.write.mode("overwrite").parquet(f"s3://{BUCKET}/silver/payment/")
print("  ✓ silver_payment written")

# ── RIDE ────────────────────────────────────────────────
print("Transforming ride...")
ride = spark.read.parquet(f"s3://{BUCKET}/bronze/ride/")
ride_silver = ride \
    .withColumn("request_timestamp", F.to_timestamp("request_timestamp")) \
    .withColumn("pickup_timestamp", F.to_timestamp("pickup_timestamp")) \
    .withColumn("dropoff_timestamp", F.to_timestamp("dropoff_timestamp")) \
    .filter(F.col("ride_status").isin("completed", "cancelled")) \
    .filter(F.col("fare_amount") >= 0) \
    .dropDuplicates(["ride_id"])

ride_silver.write.mode("overwrite").parquet(f"s3://{BUCKET}/silver/ride/")
print("  ✓ silver_ride written")

print("\n✅ Silver layer complete - Parquet files ready for Iceberg registration via Athena")
job.commit()
