"""Data schemas for all entities."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PassengerSchema:
    """Passenger entity schema."""
    passenger_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    signup_timestamp: str
    city: str
    country: str
    status: str


@dataclass
class DriverSchema:
    """Driver entity schema."""
    driver_id: str
    first_name: str
    last_name: str
    signup_timestamp: str
    rating: float
    city: str
    country: str
    status: str


@dataclass
class VehicleSchema:
    """Vehicle entity schema."""
    vehicle_id: str
    driver_id: str
    make: str
    model: str
    year: int
    vehicle_type: str
    license_plate: str


@dataclass
class RideSchema:
    """Ride entity schema."""
    ride_id: str
    passenger_id: str
    driver_id: str
    vehicle_id: str
    request_timestamp: str
    pickup_timestamp: str
    dropoff_timestamp: str
    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float
    pickup_city: str
    dropoff_city: str
    distance_km: float
    duration_minutes: int
    fare_amount: float
    currency: str
    ride_status: str


@dataclass
class PaymentSchema:
    """Payment entity schema."""
    payment_id: str
    ride_id: str
    payment_timestamp: str
    payment_method: str
    amount: float
    currency: str
    payment_status: str


# SQL DDL for Iceberg tables

BRONZE_PASSENGER_DDL = """
CREATE TABLE IF NOT EXISTS bronze.passenger (
    passenger_id STRING NOT NULL,
    first_name STRING NOT NULL,
    last_name STRING NOT NULL,
    email STRING,
    phone STRING,
    signup_timestamp TIMESTAMP,
    city STRING,
    country STRING,
    status STRING
)
USING ICEBERG
PARTITIONED BY (years(signup_timestamp))
"""

BRONZE_DRIVER_DDL = """
CREATE TABLE IF NOT EXISTS bronze.driver (
    driver_id STRING NOT NULL,
    first_name STRING NOT NULL,
    last_name STRING NOT NULL,
    signup_timestamp TIMESTAMP,
    rating DECIMAL(2, 1),
    city STRING,
    country STRING,
    status STRING
)
USING ICEBERG
PARTITIONED BY (years(signup_timestamp))
"""

BRONZE_VEHICLE_DDL = """
CREATE TABLE IF NOT EXISTS bronze.vehicle (
    vehicle_id STRING NOT NULL,
    driver_id STRING NOT NULL,
    make STRING,
    model STRING,
    year INT,
    vehicle_type STRING,
    license_plate STRING
)
USING ICEBERG
"""

BRONZE_RIDE_DDL = """
CREATE TABLE IF NOT EXISTS bronze.ride (
    ride_id STRING NOT NULL,
    passenger_id STRING NOT NULL,
    driver_id STRING NOT NULL,
    vehicle_id STRING NOT NULL,
    request_timestamp TIMESTAMP,
    pickup_timestamp TIMESTAMP,
    dropoff_timestamp TIMESTAMP,
    pickup_latitude DECIMAL(9, 6),
    pickup_longitude DECIMAL(9, 6),
    dropoff_latitude DECIMAL(9, 6),
    dropoff_longitude DECIMAL(9, 6),
    pickup_city STRING,
    dropoff_city STRING,
    distance_km DECIMAL(6, 2),
    duration_minutes INT,
    fare_amount DECIMAL(8, 2),
    currency STRING,
    ride_status STRING
)
USING ICEBERG
PARTITIONED BY (days(request_timestamp))
"""

BRONZE_PAYMENT_DDL = """
CREATE TABLE IF NOT EXISTS bronze.payment (
    payment_id STRING NOT NULL,
    ride_id STRING NOT NULL,
    payment_timestamp TIMESTAMP,
    payment_method STRING,
    amount DECIMAL(8, 2),
    currency STRING,
    payment_status STRING
)
USING ICEBERG
PARTITIONED BY (days(payment_timestamp))
"""

SILVER_PASSENGER_DDL = """
CREATE TABLE IF NOT EXISTS silver.passenger (
    passenger_id STRING NOT NULL,
    first_name STRING NOT NULL,
    last_name STRING NOT NULL,
    email STRING NOT NULL,
    phone STRING NOT NULL,
    signup_date DATE,
    city STRING NOT NULL,
    country STRING NOT NULL,
    status STRING NOT NULL
)
USING ICEBERG
PARTITIONED BY (country, city)
"""

SILVER_DRIVER_DDL = """
CREATE TABLE IF NOT EXISTS silver.driver (
    driver_id STRING NOT NULL,
    first_name STRING NOT NULL,
    last_name STRING NOT NULL,
    signup_date DATE,
    rating DECIMAL(2, 1),
    city STRING NOT NULL,
    country STRING NOT NULL,
    status STRING NOT NULL
)
USING ICEBERG
PARTITIONED BY (country, city)
"""

SILVER_VEHICLE_DDL = """
CREATE TABLE IF NOT EXISTS silver.vehicle (
    vehicle_id STRING NOT NULL,
    driver_id STRING NOT NULL,
    make STRING NOT NULL,
    model STRING NOT NULL,
    year INT NOT NULL,
    vehicle_type STRING NOT NULL,
    license_plate STRING NOT NULL UNIQUE
)
USING ICEBERG
"""

SILVER_RIDE_DDL = """
CREATE TABLE IF NOT EXISTS silver.ride (
    ride_id STRING NOT NULL,
    passenger_id STRING NOT NULL,
    driver_id STRING NOT NULL,
    vehicle_id STRING NOT NULL,
    request_date DATE,
    request_time TIMESTAMP NOT NULL,
    pickup_time TIMESTAMP NOT NULL,
    dropoff_time TIMESTAMP NOT NULL,
    pickup_location STRUCT<latitude: DECIMAL(9, 6), longitude: DECIMAL(9, 6), city: STRING>,
    dropoff_location STRUCT<latitude: DECIMAL(9, 6), longitude: DECIMAL(9, 6), city: STRING>,
    distance_km DECIMAL(6, 2) NOT NULL,
    duration_minutes INT NOT NULL,
    fare_amount DECIMAL(8, 2) NOT NULL,
    currency STRING NOT NULL,
    ride_status STRING NOT NULL,
    valid_record BOOLEAN DEFAULT TRUE,
    data_quality_checks MAP<STRING, BOOLEAN>
)
USING ICEBERG
PARTITIONED BY (days(request_time))
"""

SILVER_PAYMENT_DDL = """
CREATE TABLE IF NOT EXISTS silver.payment (
    payment_id STRING NOT NULL,
    ride_id STRING NOT NULL,
    payment_date DATE,
    payment_time TIMESTAMP NOT NULL,
    payment_method STRING NOT NULL,
    amount DECIMAL(8, 2) NOT NULL,
    currency STRING NOT NULL,
    payment_status STRING NOT NULL,
    valid_record BOOLEAN DEFAULT TRUE
)
USING ICEBERG
PARTITIONED BY (days(payment_time))
"""

GOLD_RIDE_DAILY_METRICS_DDL = """
CREATE TABLE IF NOT EXISTS gold.ride_daily_metrics (
    date DATE NOT NULL,
    city STRING NOT NULL,
    total_rides INT NOT NULL,
    completed_rides INT NOT NULL,
    cancelled_rides INT NOT NULL,
    total_distance_km DECIMAL(10, 2) NOT NULL,
    total_revenue DECIMAL(10, 2) NOT NULL,
    avg_fare DECIMAL(8, 2) NOT NULL,
    avg_distance_km DECIMAL(6, 2) NOT NULL,
    avg_duration_minutes DECIMAL(6, 2) NOT NULL
)
USING ICEBERG
PARTITIONED BY (years(date), months(date))
"""

GOLD_DRIVER_METRICS_DDL = """
CREATE TABLE IF NOT EXISTS gold.driver_metrics (
    date DATE NOT NULL,
    driver_id STRING NOT NULL,
    completed_rides INT NOT NULL,
    total_distance_km DECIMAL(10, 2) NOT NULL,
    total_revenue DECIMAL(10, 2) NOT NULL,
    avg_rating DECIMAL(2, 1)
)
USING ICEBERG
PARTITIONED BY (years(date), months(date))
"""

GOLD_CITY_METRICS_DDL = """
CREATE TABLE IF NOT EXISTS gold.city_metrics (
    date DATE NOT NULL,
    city STRING NOT NULL,
    total_rides INT NOT NULL,
    completed_rides INT NOT NULL,
    total_revenue DECIMAL(10, 2) NOT NULL,
    avg_fare DECIMAL(8, 2) NOT NULL,
    avg_distance_km DECIMAL(6, 2) NOT NULL
)
USING ICEBERG
PARTITIONED BY (years(date), months(date))
"""

# Schema definitions for validation
BRONZE_SCHEMAS = {
    "passenger": PassengerSchema,
    "driver": DriverSchema,
    "vehicle": VehicleSchema,
    "ride": RideSchema,
    "payment": PaymentSchema,
}

DDL_STATEMENTS = {
    "bronze_passenger": BRONZE_PASSENGER_DDL,
    "bronze_driver": BRONZE_DRIVER_DDL,
    "bronze_vehicle": BRONZE_VEHICLE_DDL,
    "bronze_ride": BRONZE_RIDE_DDL,
    "bronze_payment": BRONZE_PAYMENT_DDL,
    "silver_passenger": SILVER_PASSENGER_DDL,
    "silver_driver": SILVER_DRIVER_DDL,
    "silver_vehicle": SILVER_VEHICLE_DDL,
    "silver_ride": SILVER_RIDE_DDL,
    "silver_payment": SILVER_PAYMENT_DDL,
    "gold_ride_daily_metrics": GOLD_RIDE_DAILY_METRICS_DDL,
    "gold_driver_metrics": GOLD_DRIVER_METRICS_DDL,
    "gold_city_metrics": GOLD_CITY_METRICS_DDL,
}
