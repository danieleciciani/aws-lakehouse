"""Gold Aggregation - Glue Job with Iceberg v2"""

import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.sql import functions as F
from awsglue.job import Job

# Inizializzazione standard Glue ETL
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET_NAME', 'DATABASE_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

BUCKET = args['BUCKET_NAME']
DB = args['DATABASE_NAME']

# Configurazione Iceberg
spark.conf.set("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.warehouse", f"s3://{BUCKET}/")
spark.conf.set("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
spark.conf.set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

def write_iceberg(df, table_name, partition_by=None):
    location = f"s3://{BUCKET}/gold/{table_name}/"
    spark.sql(f"DROP TABLE IF EXISTS glue_catalog.{DB}.gold_{table_name}")
    writer = df.writeTo(f"glue_catalog.{DB}.gold_{table_name}") \
        .tableProperty("format-version", "2") \
        .tableProperty("location", location)
    if partition_by:
        writer = writer.partitionedBy(partition_by)
    writer.createOrReplace()


# Read silver tables
ride = spark.read.parquet(f"s3://{BUCKET}/silver/ride/")
driver = spark.read.parquet(f"s3://{BUCKET}/silver/driver/")
passenger = spark.read.parquet(f"s3://{BUCKET}/silver/passenger/")

# ── DAILY RIDE METRICS ──────────────────────────────────
daily_metrics = ride \
    .withColumn("request_date", F.to_date("request_timestamp")) \
    .groupBy("request_date", "pickup_city") \
    .agg(
        F.count("ride_id").alias("total_rides"),
        F.sum(F.when(F.col("ride_status") == "completed", 1).otherwise(0)).alias("completed_rides"),
        F.avg("fare_amount").alias("avg_fare"),
        F.sum("distance_km").alias("total_distance_km")
    )

write_iceberg(daily_metrics, "daily_ride_metrics", partition_by="request_date")

# ── DRIVER PERFORMANCE ──────────────────────────────────
driver_perf = ride \
    .filter(F.col("ride_status") == "completed") \
    .groupBy("driver_id") \
    .agg(
        F.count("ride_id").alias("completed_rides"),
        F.sum("fare_amount").alias("total_revenue"),
        F.avg("fare_amount").alias("avg_fare")
    ) \
    .join(driver.select("driver_id", "rating"), on="driver_id", how="left")

write_iceberg(driver_perf, "driver_performance")

# ── PASSENGER ACTIVITY ──────────────────────────────────
passenger_activity = ride \
    .groupBy("passenger_id") \
    .agg(
        F.count("ride_id").alias("total_rides"),
        F.sum("fare_amount").alias("total_spent"),
        F.avg("fare_amount").alias("avg_fare")
    ) \
    .join(passenger.select("passenger_id", "city", "status"), on="passenger_id", how="left")

write_iceberg(passenger_activity, "passenger_activity")

job.commit()
