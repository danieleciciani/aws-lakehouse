"""Data validation utilities."""

from typing import Dict, List, Any, Tuple
import json
import re
from datetime import datetime


class DataValidator:
    """Validates records against business rules."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone format."""
        # Accept +1XXX format
        pattern = r"^\+1\d{10}$"
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_passenger(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate passenger record."""
        errors = []

        if not record.get("passenger_id"):
            errors.append("passenger_id is required")
        if not record.get("first_name"):
            errors.append("first_name is required")
        if not record.get("last_name"):
            errors.append("last_name is required")
        if not record.get("email") or not DataValidator.validate_email(record.get("email", "")):
            errors.append("email is invalid or missing")
        if not record.get("phone") or not DataValidator.validate_phone(record.get("phone", "")):
            errors.append("phone is invalid or missing")
        if record.get("status") not in ["active", "inactive", "suspended"]:
            errors.append(f"status '{record.get('status')}' is invalid")

        return len(errors) == 0, errors

    @staticmethod
    def validate_driver(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate driver record."""
        errors = []

        if not record.get("driver_id"):
            errors.append("driver_id is required")
        if not record.get("first_name"):
            errors.append("first_name is required")
        if not record.get("last_name"):
            errors.append("last_name is required")

        rating = record.get("rating")
        if rating is None or not (0 <= float(rating) <= 5):
            errors.append(f"rating '{rating}' must be between 0 and 5")

        if record.get("status") not in ["active", "inactive", "banned"]:
            errors.append(f"status '{record.get('status')}' is invalid")

        return len(errors) == 0, errors

    @staticmethod
    def validate_vehicle(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate vehicle record."""
        errors = []

        if not record.get("vehicle_id"):
            errors.append("vehicle_id is required")
        if not record.get("driver_id"):
            errors.append("driver_id is required")
        if not record.get("license_plate"):
            errors.append("license_plate is required")

        return len(errors) == 0, errors

    @staticmethod
    def validate_ride(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate ride record."""
        errors = []

        if not record.get("ride_id"):
            errors.append("ride_id is required")
        if not record.get("passenger_id"):
            errors.append("passenger_id is required")
        if not record.get("driver_id"):
            errors.append("driver_id is required")
        if not record.get("vehicle_id"):
            errors.append("vehicle_id is required")

        # Timestamp validation
        try:
            request_ts = datetime.fromisoformat(record.get("request_timestamp", ""))
            pickup_ts = datetime.fromisoformat(record.get("pickup_timestamp", ""))
            dropoff_ts = datetime.fromisoformat(record.get("dropoff_timestamp", ""))

            if not (request_ts <= pickup_ts <= dropoff_ts):
                errors.append("timestamps out of order: request <= pickup <= dropoff")
        except (ValueError, TypeError):
            errors.append("invalid timestamp format")

        # Distance and fare validation
        distance = record.get("distance_km")
        if distance is None or float(distance) < 0:
            errors.append(f"distance_km '{distance}' must be >= 0")

        fare = record.get("fare_amount")
        if fare is None or float(fare) < 0:
            errors.append(f"fare_amount '{fare}' must be >= 0")

        duration = record.get("duration_minutes")
        if duration is None or int(duration) < 0:
            errors.append(f"duration_minutes '{duration}' must be >= 0")

        if record.get("ride_status") not in ["completed", "cancelled_by_driver", "cancelled_by_passenger", "no_show"]:
            errors.append(f"ride_status '{record.get('ride_status')}' is invalid")

        return len(errors) == 0, errors

    @staticmethod
    def validate_payment(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate payment record."""
        errors = []

        if not record.get("payment_id"):
            errors.append("payment_id is required")
        if not record.get("ride_id"):
            errors.append("ride_id is required")

        amount = record.get("amount")
        if amount is None or float(amount) < 0:
            errors.append(f"amount '{amount}' must be >= 0")

        if record.get("payment_status") not in ["completed", "failed", "pending"]:
            errors.append(f"payment_status '{record.get('payment_status')}' is invalid")

        return len(errors) == 0, errors


class DataQualityReport:
    """Generate data quality reports."""

    def __init__(self, dataset_name: str):
        """Initialize report."""
        self.dataset_name = dataset_name
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.checks: Dict[str, int] = {}
        self.errors: List[str] = []

    def add_record(self, is_valid: bool, errors: List[str] = None):
        """Record validation result."""
        self.total_records += 1
        if is_valid:
            self.valid_records += 1
        else:
            self.invalid_records += 1
            if errors:
                for error in errors:
                    self.checks[error] = self.checks.get(error, 0) + 1
                    self.errors.append(f"Record {self.total_records}: {error}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "dataset": self.dataset_name,
            "records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "validity_rate": round(100 * self.valid_records / self.total_records, 2) if self.total_records > 0 else 0,
            "checks": self.checks,
            "errors": self.errors[:100],  # Limit to 100 errors
            "errors_truncated": len(self.errors) > 100,
        }

    def to_json(self, filepath: str) -> None:
        """Save report to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
