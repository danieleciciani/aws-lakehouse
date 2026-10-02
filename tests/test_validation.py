"""Tests for data validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.validation import DataValidator, DataQualityReport


def test_email_validation():
    """Test email validation."""
    assert DataValidator.validate_email("user@example.com")
    assert DataValidator.validate_email("test.user+tag@domain.co.uk")
    assert not DataValidator.validate_email("invalid.email")
    assert not DataValidator.validate_email("@example.com")


def test_phone_validation():
    """Test phone validation."""
    assert DataValidator.validate_phone("+12025551234")
    assert DataValidator.validate_phone("+14155551234")
    assert not DataValidator.validate_phone("2025551234")
    assert not DataValidator.validate_phone("+1202555")


def test_passenger_validation():
    """Test passenger record validation."""
    valid_record = {
        "passenger_id": "P000001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+12025551234",
        "status": "active",
    }

    is_valid, errors = DataValidator.validate_passenger(valid_record)
    assert is_valid, f"Valid record should pass: {errors}"

    invalid_record = {
        "passenger_id": "P000001",
        "email": "invalid-email",
        "status": "unknown",
    }

    is_valid, errors = DataValidator.validate_passenger(invalid_record)
    assert not is_valid, "Invalid record should fail"
    assert len(errors) > 0


def test_driver_validation():
    """Test driver record validation."""
    valid_record = {
        "driver_id": "D000001",
        "first_name": "Jane",
        "last_name": "Doe",
        "rating": 4.5,
        "status": "active",
    }

    is_valid, errors = DataValidator.validate_driver(valid_record)
    assert is_valid

    invalid_record = {
        "driver_id": "D000001",
        "rating": 6.5,  # Invalid: >5
        "status": "unknown",
    }

    is_valid, errors = DataValidator.validate_driver(invalid_record)
    assert not is_valid


def test_ride_validation():
    """Test ride record validation."""
    valid_record = {
        "ride_id": "R00000001",
        "passenger_id": "P000001",
        "driver_id": "D000001",
        "vehicle_id": "V000001",
        "request_timestamp": "2026-05-01T10:00:00",
        "pickup_timestamp": "2026-05-01T10:05:00",
        "dropoff_timestamp": "2026-05-01T10:30:00",
        "distance_km": 5.5,
        "duration_minutes": 25,
        "fare_amount": 15.50,
        "ride_status": "completed",
    }

    is_valid, errors = DataValidator.validate_ride(valid_record)
    assert is_valid, f"Valid record should pass: {errors}"

    invalid_record = {
        "ride_id": "R00000001",
        "distance_km": -1,
        "fare_amount": 15.50,
    }

    is_valid, errors = DataValidator.validate_ride(invalid_record)
    assert not is_valid


def test_data_quality_report():
    """Test data quality report generation."""
    report = DataQualityReport("test_dataset")

    report.add_record(True)
    report.add_record(True)
    report.add_record(False, ["missing_field"])
    report.add_record(False, ["invalid_value"])

    assert report.total_records == 4
    assert report.valid_records == 2
    assert report.invalid_records == 2

    report_dict = report.to_dict()
    assert report_dict["dataset"] == "test_dataset"
    assert report_dict["records"] == 4
    assert report_dict["validity_rate"] == 50.0
