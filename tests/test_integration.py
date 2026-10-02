"""Integration tests for the full pipeline."""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_data import MockDataGenerator
from python.validation import DataValidator


def test_end_to_end_generation():
    """Test full data generation pipeline."""
    gen = MockDataGenerator(seed=42)
    gen.passenger_count = 100
    gen.driver_count = 20
    gen.vehicle_count = 20
    gen.ride_count = 500

    passengers = gen.generate_passengers(100)
    drivers = gen.generate_drivers(20)
    vehicles = gen.generate_vehicles(20, [d["driver_id"] for d in drivers])
    rides = gen.generate_rides(500, [p["passenger_id"] for p in passengers],
                               [d["driver_id"] for d in drivers],
                               [v["vehicle_id"] for v in vehicles])
    payments = gen.generate_payments(rides)

    # Validate counts
    assert len(passengers) == 100
    assert len(drivers) == 20
    assert len(vehicles) == 20
    assert len(rides) == 500
    assert len(payments) > 0
    assert len(payments) < len(rides)  # Not all rides have payments

    # Validate structure
    for passenger in passengers:
        is_valid, errors = DataValidator.validate_passenger(passenger)
        assert is_valid, f"Invalid passenger: {errors}"

    for driver in drivers:
        is_valid, errors = DataValidator.validate_driver(driver)
        assert is_valid, f"Invalid driver: {errors}"

    for ride in rides:
        is_valid, errors = DataValidator.validate_ride(ride)
        assert is_valid, f"Invalid ride {ride.get('ride_id')}: {errors}"

    for payment in payments:
        is_valid, errors = DataValidator.validate_payment(payment)
        assert is_valid, f"Invalid payment: {errors}"


def test_foreign_key_relationships():
    """Test that all foreign keys are valid."""
    gen = MockDataGenerator(seed=42)
    gen.passenger_count = 50
    gen.driver_count = 10
    gen.vehicle_count = 10
    gen.ride_count = 200

    passengers = gen.generate_passengers(50)
    drivers = gen.generate_drivers(10)
    vehicles = gen.generate_vehicles(10, [d["driver_id"] for d in drivers])
    rides = gen.generate_rides(200, [p["passenger_id"] for p in passengers],
                               [d["driver_id"] for d in drivers],
                               [v["vehicle_id"] for v in vehicles])
    payments = gen.generate_payments(rides)

    passenger_ids = {p["passenger_id"] for p in passengers}
    driver_ids = {d["driver_id"] for d in drivers}
    vehicle_ids = {v["vehicle_id"] for v in vehicles}
    ride_ids = {r["ride_id"] for r in rides}

    # Verify foreign keys
    for ride in rides:
        assert ride["passenger_id"] in passenger_ids, f"Invalid passenger reference in ride {ride['ride_id']}"
        assert ride["driver_id"] in driver_ids, f"Invalid driver reference in ride {ride['ride_id']}"
        assert ride["vehicle_id"] in vehicle_ids, f"Invalid vehicle reference in ride {ride['ride_id']}"

    for payment in payments:
        assert payment["ride_id"] in ride_ids, f"Invalid ride reference in payment {payment['payment_id']}"

    for vehicle in vehicles:
        assert vehicle["driver_id"] in driver_ids, f"Invalid driver reference in vehicle {vehicle['vehicle_id']}"


def test_timestamp_ordering():
    """Test that ride timestamps are in correct order."""
    gen = MockDataGenerator(seed=42)
    gen.ride_count = 200

    rides = gen.generate_rides(200, [f"P{i:06d}" for i in range(50)],
                               [f"D{i:06d}" for i in range(10)],
                               [f"V{i:06d}" for i in range(10)])

    for ride in rides:
        try:
            request_ts = datetime.fromisoformat(ride["request_timestamp"])
            pickup_ts = datetime.fromisoformat(ride["pickup_timestamp"])
            dropoff_ts = datetime.fromisoformat(ride["dropoff_timestamp"])

            assert request_ts <= pickup_ts, f"Request should be before pickup in {ride['ride_id']}"
            assert pickup_ts <= dropoff_ts, f"Pickup should be before dropoff in {ride['ride_id']}"
        except (ValueError, TypeError) as e:
            raise AssertionError(f"Timestamp parsing failed for ride {ride['ride_id']}: {e}")


def test_data_ranges():
    """Test that generated data falls within expected ranges."""
    gen = MockDataGenerator(seed=42)
    gen.ride_count = 200

    rides = gen.generate_rides(200, [f"P{i:06d}" for i in range(50)],
                               [f"D{i:06d}" for i in range(10)],
                               [f"V{i:06d}" for i in range(10)])

    for ride in rides:
        assert 0 <= ride["distance_km"] <= 1000, "Distance should be reasonable"
        assert 0 <= ride["fare_amount"] <= 500, "Fare should be reasonable"
        assert 0 <= ride["duration_minutes"] <= 300, "Duration should be reasonable"
        assert -90 <= ride["pickup_latitude"] <= 90, "Latitude should be valid"
        assert -180 <= ride["pickup_longitude"] <= 180, "Longitude should be valid"


def test_jsonl_serialization(tmp_path):
    """Test that generated data can be serialized to JSONL."""
    gen = MockDataGenerator(seed=42)
    gen.passenger_count = 50
    gen.driver_count = 10
    gen.vehicle_count = 10
    gen.ride_count = 200

    data_dir = tmp_path / "test_data"
    counts = gen.save_data(str(data_dir))

    # Verify files were created
    assert (data_dir / "passenger" / "passengers.jsonl").exists()
    assert (data_dir / "driver" / "drivers.jsonl").exists()
    assert (data_dir / "vehicle" / "vehicles.jsonl").exists()
    assert (data_dir / "ride" / "rides.jsonl").exists()
    assert (data_dir / "payment" / "payments.jsonl").exists()

    # Verify records match counts
    with open(data_dir / "passenger" / "passengers.jsonl") as f:
        passengers = [json.loads(line) for line in f]
    assert len(passengers) == 50

    with open(data_dir / "ride" / "rides.jsonl") as f:
        rides = [json.loads(line) for line in f]
    assert len(rides) == 200
