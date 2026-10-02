#!/usr/bin/env python3
"""
Mock data generator for Uber-like domain.

Generates realistic but completely synthetic data for:
- Passengers
- Drivers
- Vehicles
- Rides
- Payments

Usage:
    python scripts/generate_data.py --passengers 1000 --drivers 200 --vehicles 200 --rides 10000 --seed 42

Output:
    data/
      passenger/
      driver/
      vehicle/
      ride/
      payment/
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import sys


class MockDataGenerator:
    """Generate realistic synthetic data for Uber-like domain."""

    # Cities for geographic distribution
    CITIES = [
        ("San Francisco", 37.7749, -122.4194),
        ("Los Angeles", 34.0522, -118.2437),
        ("New York", 40.7128, -74.0060),
        ("Chicago", 41.8781, -87.6298),
        ("Houston", 29.7604, -95.3698),
        ("Phoenix", 33.4484, -112.0742),
        ("Philadelphia", 39.9526, -75.1652),
        ("San Antonio", 29.4241, -98.4936),
        ("San Diego", 32.7157, -117.1611),
        ("Dallas", 32.7767, -96.7970),
    ]

    VEHICLE_MAKES = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Tesla", "Uber"]
    VEHICLE_MODELS = {
        "Toyota": ["Camry", "Corolla", "Prius"],
        "Honda": ["Civic", "Accord", "CR-V"],
        "Ford": ["Focus", "Fusion", "Escape"],
        "Chevrolet": ["Malibu", "Impala", "Traverse"],
        "BMW": ["3 Series", "5 Series", "X5"],
        "Tesla": ["Model 3", "Model Y", "Model S"],
        "Uber": ["XL", "Pool", "Black"],
    }
    VEHICLE_TYPES = ["economy", "comfort", "xl", "premium"]
    PAYMENT_METHODS = ["credit_card", "debit_card", "cash", "digital_wallet", "uber_cash"]
    RIDE_STATUS = ["completed", "cancelled_by_driver", "cancelled_by_passenger", "no_show"]

    def __init__(self, seed: int = 42):
        """Initialize generator with deterministic seed."""
        self.seed = seed
        random.seed(seed)
        self.base_date = datetime(2026, 1, 1)

    def generate_passengers(self, count: int) -> List[Dict[str, Any]]:
        """Generate passenger records."""
        passengers = []
        for i in range(count):
            city, _, _ = random.choice(self.CITIES)
            passengers.append({
                "passenger_id": f"P{i+1:06d}",
                "first_name": self._random_first_name(),
                "last_name": self._random_last_name(),
                "email": f"passenger{i+1:06d}@example.com",
                "phone": self._random_phone(),
                "signup_timestamp": (self.base_date - timedelta(days=random.randint(30, 365))).isoformat(),
                "city": city,
                "country": "USA",
                "status": random.choice(["active", "inactive", "suspended"]),
            })
        return passengers

    def generate_drivers(self, count: int) -> List[Dict[str, Any]]:
        """Generate driver records."""
        drivers = []
        for i in range(count):
            city, _, _ = random.choice(self.CITIES)
            drivers.append({
                "driver_id": f"D{i+1:06d}",
                "first_name": self._random_first_name(),
                "last_name": self._random_last_name(),
                "signup_timestamp": (self.base_date - timedelta(days=random.randint(30, 730))).isoformat(),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "city": city,
                "country": "USA",
                "status": random.choice(["active", "inactive", "banned"]),
            })
        return drivers

    def generate_vehicles(self, count: int, driver_ids: List[str]) -> List[Dict[str, Any]]:
        """Generate vehicle records."""
        vehicles = []
        for i in range(count):
            make = random.choice(self.VEHICLE_MAKES)
            vehicles.append({
                "vehicle_id": f"V{i+1:06d}",
                "driver_id": random.choice(driver_ids),
                "make": make,
                "model": random.choice(self.VEHICLE_MODELS[make]),
                "year": random.randint(2015, 2025),
                "vehicle_type": random.choice(self.VEHICLE_TYPES),
                "license_plate": self._random_license_plate(),
            })
        return vehicles

    def generate_rides(
        self,
        count: int,
        passenger_ids: List[str],
        driver_ids: List[str],
        vehicle_ids: List[str],
    ) -> List[Dict[str, Any]]:
        """Generate ride records."""
        rides = []
        for i in range(count):
            pickup_city, pickup_lat, pickup_lon = random.choice(self.CITIES)
            dropoff_city, dropoff_lat, dropoff_lon = random.choice(self.CITIES)

            # Add some variation to coordinates within city
            pickup_lat += random.uniform(-0.05, 0.05)
            pickup_lon += random.uniform(-0.05, 0.05)
            dropoff_lat += random.uniform(-0.05, 0.05)
            dropoff_lon += random.uniform(-0.05, 0.05)

            request_time = self.base_date + timedelta(
                days=random.randint(0, 273),  # ~9 months
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            duration_minutes = random.randint(5, 120)
            pickup_time = request_time + timedelta(minutes=random.randint(1, 10))
            dropoff_time = pickup_time + timedelta(minutes=duration_minutes)

            # Calculate distance using simplified Haversine
            distance_km = self._haversine(
                pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
            )

            # Realistic fare calculation
            base_fare = 2.50
            per_km_rate = 1.25
            per_minute_rate = 0.25
            fare_amount = base_fare + (distance_km * per_km_rate) + (duration_minutes * per_minute_rate)
            fare_amount = round(fare_amount, 2)

            rides.append({
                "ride_id": f"R{i+1:08d}",
                "passenger_id": random.choice(passenger_ids),
                "driver_id": random.choice(driver_ids),
                "vehicle_id": random.choice(vehicle_ids),
                "request_timestamp": request_time.isoformat(),
                "pickup_timestamp": pickup_time.isoformat(),
                "dropoff_timestamp": dropoff_time.isoformat(),
                "pickup_latitude": round(pickup_lat, 6),
                "pickup_longitude": round(pickup_lon, 6),
                "dropoff_latitude": round(dropoff_lat, 6),
                "dropoff_longitude": round(dropoff_lon, 6),
                "pickup_city": pickup_city,
                "dropoff_city": dropoff_city,
                "distance_km": round(distance_km, 2),
                "duration_minutes": duration_minutes,
                "fare_amount": fare_amount,
                "currency": "USD",
                "ride_status": random.choice(self.RIDE_STATUS),
            })
        return rides

    def generate_payments(self, rides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate payment records for completed rides."""
        payments = []
        payment_id = 1

        for ride in rides:
            # Only generate payments for completed or most cancelled rides
            if ride["ride_status"] in ["completed", "cancelled_by_driver"]:
                if random.random() < 0.9:  # 90% payment success rate
                    payments.append({
                        "payment_id": f"PM{payment_id:08d}",
                        "ride_id": ride["ride_id"],
                        "payment_timestamp": ride["dropoff_timestamp"],
                        "payment_method": random.choice(self.PAYMENT_METHODS),
                        "amount": ride["fare_amount"],
                        "currency": "USD",
                        "payment_status": random.choice(["completed", "failed", "pending"]),
                    })
                    payment_id += 1

        return payments

    def save_data(self, base_dir: str = "data") -> Dict[str, int]:
        """Save all generated data to files."""
        base_path = Path(base_dir)
        base_path.mkdir(exist_ok=True)

        # Create entity directories
        for entity in ["passenger", "driver", "vehicle", "ride", "payment"]:
            (base_path / entity).mkdir(exist_ok=True)

        # Generate data
        passengers = self.generate_passengers(self.passenger_count)
        passenger_ids = [p["passenger_id"] for p in passengers]

        drivers = self.generate_drivers(self.driver_count)
        driver_ids = [d["driver_id"] for d in drivers]

        vehicles = self.generate_vehicles(self.vehicle_count, driver_ids)
        vehicle_ids = [v["vehicle_id"] for v in vehicles]

        rides = self.generate_rides(self.ride_count, passenger_ids, driver_ids, vehicle_ids)
        payments = self.generate_payments(rides)

        # Save as JSONL
        self._save_jsonl(base_path / "passenger" / "passengers.jsonl", passengers)
        self._save_jsonl(base_path / "driver" / "drivers.jsonl", drivers)
        self._save_jsonl(base_path / "vehicle" / "vehicles.jsonl", vehicles)
        self._save_jsonl(base_path / "ride" / "rides.jsonl", rides)
        self._save_jsonl(base_path / "payment" / "payments.jsonl", payments)

        return {
            "passengers": len(passengers),
            "drivers": len(drivers),
            "vehicles": len(vehicles),
            "rides": len(rides),
            "payments": len(payments),
        }

    # Private helper methods
    def _save_jsonl(self, filepath: Path, records: List[Dict[str, Any]]) -> None:
        """Save records as JSON Lines."""
        with open(filepath, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

    @staticmethod
    def _random_first_name() -> str:
        """Generate random first name."""
        names = [
            "James", "Mary", "Robert", "Patricia", "Michael", "Jennifer",
            "William", "Linda", "David", "Barbara", "Richard", "Susan",
            "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
            "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty",
            "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
            "Steven", "Kimberly", "Paul", "Donna", "Andrew", "Carol",
            "Joshua", "Michelle", "Kenneth", "Emily", "Kevin", "Melissa",
            "Brian", "Deborah", "George", "Stephanie", "Edward", "Rebecca",
            "Ronald", "Sharon", "Timothy", "Laura", "Jason", "Cynthia",
            "Jeffrey", "Kathleen", "Ryan", "Amy", "Jacob", "Angela",
            "Gary", "Shirley", "Nicholas", "Anna", "Eric", "Brenda",
            "Jonathan", "Pamela", "Stephen", "Emma", "Larry", "Nicole",
            "Justin", "Helen", "Scott", "Samantha", "Brandon", "Katherine",
            "Benjamin", "Christine", "Samuel", "Debra", "Frank", "Rachel",
            "Alexander", "Catherine", "Raymond", "Carolyn", "Patrick", "Janet",
            "Jack", "Maria", "Dennis", "Heather", "Jerry", "Diane",
            "Tyler", "Virginia", "Aaron", "Julie", "Jose", "Joyce",
        ]
        return random.choice(names)

    @staticmethod
    def _random_last_name() -> str:
        """Generate random last name."""
        names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
            "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
            "Walker", "Young", "Allen", "King", "Wright", "Scott",
            "Torres", "Peterson", "Phillips", "Campbell", "Parker", "Evans",
            "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales",
            "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
            "Peterson", "Cooper", "Peterson", "Reed", "Bell", "Gomez",
            "Russell", "Fox", "Bryant", "Beverly", "Waller", "Watts",
            "Welch", "Wells", "West", "Wheeler", "Whitaker", "White",
            "Whitfield", "Whitley", "Whitney", "Wiggins", "Wilcox", "Wilder",
            "Wilkes", "Wilkins", "Wilkinson", "Wille", "Willey", "Williams",
        ]
        return random.choice(names)

    @staticmethod
    def _random_phone() -> str:
        """Generate random US phone number."""
        return f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"

    @staticmethod
    def _random_license_plate() -> str:
        """Generate random license plate."""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digits = "0123456789"
        return "".join(random.choices(chars, k=3)) + "".join(random.choices(digits, k=4))

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers."""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth radius in kilometers
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate mock data for Uber-like domain"
    )
    parser.add_argument(
        "--passengers",
        type=int,
        default=1000,
        help="Number of passengers to generate",
    )
    parser.add_argument(
        "--drivers", type=int, default=200, help="Number of drivers to generate"
    )
    parser.add_argument(
        "--vehicles", type=int, default=200, help="Number of vehicles to generate"
    )
    parser.add_argument(
        "--rides", type=int, default=10000, help="Number of rides to generate"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--output", type=str, default="data", help="Output directory for generated data"
    )

    args = parser.parse_args()

    # Validate inputs
    if args.passengers < 1 or args.drivers < 1 or args.vehicles < 1 or args.rides < 1:
        print("Error: All counts must be >= 1", file=sys.stderr)
        sys.exit(1)

    if args.passengers < args.drivers * 2:
        print(
            "Warning: Fewer passengers than 2x drivers. Rides may have duplicate drivers.",
            file=sys.stderr,
        )

    print(f"Generating mock data with seed={args.seed}")
    print(f"  Passengers: {args.passengers}")
    print(f"  Drivers: {args.drivers}")
    print(f"  Vehicles: {args.vehicles}")
    print(f"  Rides: {args.rides}")

    generator = MockDataGenerator(seed=args.seed)
    generator.passenger_count = args.passengers
    generator.driver_count = args.drivers
    generator.vehicle_count = args.vehicles
    generator.ride_count = args.rides

    counts = generator.save_data(args.output)

    print(f"\nData generated successfully:")
    for entity, count in counts.items():
        print(f"  {entity}: {count}")
    print(f"\nOutput directory: {args.output}")
    print("Files:")
    for entity in ["passenger", "driver", "vehicle", "ride", "payment"]:
        filepath = Path(args.output) / entity / f"{entity}s.jsonl"
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  {filepath} ({size:,} bytes)")


if __name__ == "__main__":
    main()
