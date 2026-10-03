"""Gold Aggregation Glue Job - Read Silver, Aggregate, Write Parquet."""

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

print(f"Starting Gold Aggregation")

# ── DAILY RIDE METRICS ──────────────────────────────────
print("Creating daily_ride_metrics...")
ride = spark.read.parquet(f"s3://{BUCKET}/silver/ride/")
daily_metrics = ride \
    .withColumn("request_date", F.to_date("request_timestamp")) \
    .groupBy("request_date", "pickup_city") \
    .agg(
        F.count("ride_id").alias("total_rides"),
        F.sum(F.when(F.col("ride_status") == "completed", 1).otherwise(0)).alias("completed_rides"),
        F.avg("fare_amount").alias("avg_fare"),
        F.sum("distance_km").alias("total_distance_km")
    )

daily_metrics.write.partitionBy("request_date").mode("overwrite").parquet(f"s3://{BUCKET}/gold/daily_ride_metrics/")
print("  ✓ gold_daily_ride_metrics written")

# ── DRIVER PERFORMANCE ──────────────────────────────────
print("Creating driver_performance...")
driver = spark.read.parquet(f"s3://{BUCKET}/silver/driver/")
driver_perf = ride \
    .filter(F.col("ride_status") == "completed") \
    .groupBy("driver_id") \
    .agg(
        F.count("ride_id").alias("completed_rides"),
        F.sum("fare_amount").alias("total_revenue"),
        F.avg("fare_amount").alias("avg_fare")
    ) \
    .join(driver.select("driver_id", "rating"), on="driver_id", how="left")

driver_perf.write.mode("overwrite").parquet(f"s3://{BUCKET}/gold/driver_performance/")
print("  ✓ gold_driver_performance written")

# ── PASSENGER ACTIVITY ──────────────────────────────────
print("Creating passenger_activity...")
passenger = spark.read.parquet(f"s3://{BUCKET}/silver/passenger/")
passenger_activity = ride \
    .groupBy("passenger_id") \
    .agg(
        F.count("ride_id").alias("total_rides"),
        F.sum("fare_amount").alias("total_spent"),
        F.avg("fare_amount").alias("avg_fare")
    ) \
    .join(passenger.select("passenger_id", "city", "status"), on="passenger_id", how="left")

passenger_activity.write.mode("overwrite").parquet(f"s3://{BUCKET}/gold/passenger_activity/")
print("  ✓ gold_passenger_activity written")

print("\n✅ Gold layer complete - Parquet files ready for Iceberg registration via Athena")
job.commit()
