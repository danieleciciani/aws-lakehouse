"""Gold Aggregation - Glue Job with Iceberg v2"""

import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.sql import functions as F
from awsglue.job import Job

# Inizializzazione standard Glue ETL
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

BUCKET = "lakehouse-uber-demo-605628228254-eu-north-1"
DB     = "lakehouse_dev"

# Configurazione Iceberg
spark.conf.set("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.warehouse", f"s3://{BUCKET}/")
spark.conf.set("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

# Read silver ride table
ride = spark.read.format("iceberg").load(f"glue_catalog.{DB}.silver_ride")

# Aggregation 1 - daily ride metrics
daily_metrics = ride \
    .withColumn("request_date", F.to_date("request_timestamp")) \
    .groupBy("request_date") \
    .agg(
        F.count("ride_id").alias("total_rides"),
        F.avg("fare_amount").alias("avg_fare")
    ) \
    .coalesce(1)

location = f"s3://{BUCKET}/gold/daily_ride_metrics/"
spark.sql(f"DROP TABLE IF EXISTS glue_catalog.{DB}.gold_daily_ride_metrics")
daily_metrics.writeTo(f"glue_catalog.{DB}.gold_daily_ride_metrics") \
    .tableProperty("format-version", "2") \
    .tableProperty("location", location) \
    .createOrReplace()

# Aggregation 2 - driver performance
driver_perf = ride \
    .filter(F.col("ride_status") == "completed") \
    .groupBy("driver_id") \
    .agg(
        F.count("ride_id").alias("completed_rides"),
        F.sum("fare_amount").alias("total_revenue"),
        F.avg("fare_amount").alias("avg_fare")
    ) \
    .coalesce(1)

location = f"s3://{BUCKET}/gold/driver_performance/"
spark.sql(f"DROP TABLE IF EXISTS glue_catalog.{DB}.gold_driver_performance")
driver_perf.writeTo(f"glue_catalog.{DB}.gold_driver_performance") \
    .tableProperty("format-version", "2") \
    .tableProperty("location", location) \
    .createOrReplace()

# Aggregation 3 - passenger activity
passenger_activity = ride \
    .groupBy("passenger_id") \
    .agg(
        F.count("ride_id").alias("total_rides"),
        F.sum("fare_amount").alias("total_spent"),
        F.avg("fare_amount").alias("avg_fare")
    ) \
    .coalesce(1)

location = f"s3://{BUCKET}/gold/passenger_activity/"
spark.sql(f"DROP TABLE IF EXISTS glue_catalog.{DB}.gold_passenger_activity")
passenger_activity.writeTo(f"glue_catalog.{DB}.gold_passenger_activity") \
    .tableProperty("format-version", "2") \
    .tableProperty("location", location) \
    .createOrReplace()

job.commit()
