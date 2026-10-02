"""Tests for mock data generation."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_data import MockDataGenerator


def test_deterministic_generation():
    """Test that same seed produces same results."""
    gen1 = MockDataGenerator(seed=42)
    gen1.passenger_count = 10
    gen1.driver_count = 5
    gen1.vehicle_count = 5
    gen1.ride_count = 100

    passengers1 = gen1.generate_passengers(10)
    drivers1 = gen1.generate_drivers(5)

    gen2 = MockDataGenerator(seed=42)
    gen2.passenger_count = 10
    gen2.driver_count = 5
    gen2.vehicle_count = 5
    gen2.ride_count = 100

    passengers2 = gen2.generate_passengers(10)
    drivers2 = gen2.generate_drivers(5)

    assert passengers1[0] == passengers2[0], "Same seed should produce identical data"
    assert drivers1[0] == drivers1[0], "Drivers should match"


def test_passenger_generation():
    """Test passenger record generation."""
    gen = MockDataGenerator(seed=42)
    passengers = gen.generate_passengers(5)

    assert len(passengers) == 5
    for p in passengers:
        assert "passenger_id" in p
        assert "first_name" in p
        assert "last_name" in p
        assert "email" in p
        assert "phone" in p
        assert "signup_timestamp" in p
        assert "city" in p
        assert "country" in p
        assert "status" in p
        assert p["status"] in ["active", "inactive", "suspended"]


def test_driver_generation():
    """Test driver record generation."""
    gen = MockDataGenerator(seed=42)
    drivers = gen.generate_drivers(5)

    assert len(drivers) == 5
    for d in drivers:
        assert "driver_id" in d
        assert "rating" in d
        assert 0 <= d["rating"] <= 5, "Rating should be 0-5"
        assert d["status"] in ["active", "inactive", "banned"]


def test_vehicle_generation():
    """Test vehicle record generation."""
    gen = MockDataGenerator(seed=42)
    driver_ids = [f"D{i:06d}" for i in range(10)]
    vehicles = gen.generate_vehicles(5, driver_ids)

    assert len(vehicles) == 5
    for v in vehicles:
        assert "vehicle_id" in v
        assert "driver_id" in v
        assert "make" in v
        assert "model" in v
        assert "year" in v
        assert "vehicle_type" in v
        assert "license_plate" in v
        assert v["driver_id"] in driver_ids


def test_ride_generation():
    """Test ride record generation."""
    gen = MockDataGenerator(seed=42)
    passenger_ids = [f"P{i:06d}" for i in range(50)]
    driver_ids = [f"D{i:06d}" for i in range(10)]
    vehicle_ids = [f"V{i:06d}" for i in range(10)]

    rides = gen.generate_rides(100, passenger_ids, driver_ids, vehicle_ids)

    assert len(rides) == 100
    for r in rides:
        assert "ride_id" in r
        assert "passenger_id" in r
        assert "driver_id" in r
        assert "vehicle_id" in r
        assert "distance_km" in r
        assert r["distance_km"] >= 0, "Distance should be non-negative"
        assert "fare_amount" in r
        assert r["fare_amount"] >= 0, "Fare should be non-negative"
        assert r["ride_status"] in ["completed", "cancelled_by_driver", "cancelled_by_passenger", "no_show"]


def test_payment_generation():
    """Test payment record generation."""
    gen = MockDataGenerator(seed=42)
    rides = [
        {
            "ride_id": f"R{i:08d}",
            "ride_status": "completed" if i % 2 == 0 else "cancelled_by_driver",
            "dropoff_timestamp": "2026-05-01T12:00:00",
            "fare_amount": 25.50,
        }
        for i in range(100)
    ]

    payments = gen.generate_payments(rides)

    assert len(payments) > 0, "Should generate at least some payments"
    assert len(payments) < len(rides), "Not all rides should have payments"

    for p in payments:
        assert "payment_id" in p
        assert "ride_id" in p
        assert "payment_timestamp" in p
        assert "payment_method" in p
        assert p["payment_method"] in ["credit_card", "debit_card", "cash", "digital_wallet", "uber_cash"]
        assert "amount" in p
        assert p["amount"] >= 0
        assert p["payment_status"] in ["completed", "failed", "pending"]


def test_unique_ids():
    """Test that generated IDs are unique."""
    gen = MockDataGenerator(seed=42)
    passengers = gen.generate_passengers(1000)
    passenger_ids = [p["passenger_id"] for p in passengers]

    assert len(passenger_ids) == len(set(passenger_ids)), "All passenger IDs should be unique"


def test_foreign_key_validity():
    """Test that foreign keys reference valid entities."""
    gen = MockDataGenerator(seed=42)
    passenger_ids = [f"P{i:06d}" for i in range(100)]
    driver_ids = [f"D{i:06d}" for i in range(20)]
    vehicle_ids = [f"V{i:06d}" for i in range(20)]

    rides = gen.generate_rides(500, passenger_ids, driver_ids, vehicle_ids)

    for ride in rides:
        assert ride["passenger_id"] in passenger_ids, "Passenger ID should reference valid passenger"
        assert ride["driver_id"] in driver_ids, "Driver ID should reference valid driver"
        assert ride["vehicle_id"] in vehicle_ids, "Vehicle ID should reference valid vehicle"
