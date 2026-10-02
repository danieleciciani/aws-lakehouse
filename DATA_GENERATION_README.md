# Mock Data Generation

## Overview

The mock data generator produces realistic but completely synthetic data for an Uber-like domain. All data is randomly generated using Python's `random` module with deterministic seeding for reproducibility.

## Generated Data

### Entities

1. **Passenger** (100–1000 records)
   - UUID: `P{000001}`
   - Fields: first_name, last_name, email, phone, signup_timestamp, city, country, status

2. **Driver** (20–200 records)
   - UUID: `D{000001}`
   - Fields: first_name, last_name, signup_timestamp, rating (0–5), city, country, status

3. **Vehicle** (20–200 records)
   - UUID: `V{000001}`
   - Fields: driver_id (FK), make, model, year, vehicle_type, license_plate

4. **Ride** (500–100k records)
   - UUID: `R{00000001}`
   - Fields: passenger_id (FK), driver_id (FK), vehicle_id (FK), timestamps, locations, distance, fare, status

5. **Payment** (~80% of rides)
   - UUID: `PM{00000001}`
   - Fields: ride_id (FK), payment_timestamp, payment_method, amount, payment_status

### Data Characteristics

**Realistic Elements:**
- Valid geographic coordinates (latitude/longitude) for 10 US cities
- Timestamps in chronological order: request → pickup → dropoff
- Fare calculated from: base_fare + distance_km × $1.25 + duration_minutes × $0.25
- Distance calculated using Haversine formula
- Rating values between 0 and 5
- Payment methods: credit_card, debit_card, cash, digital_wallet, uber_cash
- Status values: active/inactive/suspended (passenger), active/inactive/banned (driver), completed/cancelled (ride)

**Data Volume:**
```
Passengers:   100–10,000
Drivers:      20–1,000
Vehicles:     20–1,000
Rides:        500–100,000
Payments:     ~80% of rides

Total size: 5 MB (100 pax, 20 drivers, 10k rides) → ~500 MB (10k pax, 1k drivers, 100k rides)
```

## Usage

### Basic Generation

```bash
python scripts/generate_data.py \
  --passengers 1000 \
  --drivers 200 \
  --vehicles 200 \
  --rides 10000 \
  --seed 42 \
  --output data
```

### Output Structure

```
data/
├── passenger/
│   └── passengers.jsonl          # One JSON object per line
├── driver/
│   └── drivers.jsonl
├── vehicle/
│   └── vehicles.jsonl
├── ride/
│   └── rides.jsonl
└── payment/
    └── payments.jsonl
```

### Deterministic Generation

Same seed produces identical results:
```bash
# Run 1: identical data
python scripts/generate_data.py --seed 42 --passengers 1000 --rides 10000

# Run 2: identical data (same seed)
python scripts/generate_data.py --seed 42 --passengers 1000 --rides 10000

# Run 3: different data (different seed)
python scripts/generate_data.py --seed 99 --passengers 1000 --rides 10000
```

## Data Quality

### Foreign Key Validity

- All `ride.passenger_id` reference valid passengers
- All `ride.driver_id` reference valid drivers
- All `ride.vehicle_id` reference valid vehicles
- All `payment.ride_id` reference valid rides
- All `vehicle.driver_id` reference valid drivers

### Timestamp Validity

For all rides:
```
request_timestamp <= pickup_timestamp <= dropoff_timestamp
```

### Numeric Ranges

- Rating: 0.0–5.0
- Distance: 0–3000 km (Haversine between US cities)
- Duration: 5–120 minutes
- Fare: $2.50–$5000 (based on distance + duration)
- Latitude: -90 to +90 (±0.05 variation around city)
- Longitude: -180 to +180 (±0.05 variation around city)

### Completeness

- No `NULL` values (all fields populated)
- All required fields present
- All foreign keys valid

## Dataset Statistics

Default configuration (1k passengers, 200 drivers, 200 vehicles, 10k rides):

```
File sizes:
  passengers.jsonl:  ~24 KB   (1,000 records)
  drivers.jsonl:     ~3.8 KB  (200 records)
  vehicles.jsonl:    ~3.1 KB  (200 records)
  rides.jsonl:       ~270 KB  (10,000 records)
  payments.jsonl:    ~42 KB   (8,000 records, ~80% payment rate)
  ─────────────────────────────
  Total:             ~343 KB

Time periods covered:
  Base date: 2026-01-01
  Data range: Jan 2026 – Oct 2026 (~9 months)

Cities represented:
  San Francisco, Los Angeles, New York, Chicago, Houston,
  Phoenix, Philadelphia, San Antonio, San Diego, Dallas
```

## Customization

### Custom Counts

```bash
python scripts/generate_data.py \
  --passengers 5000 \
  --drivers 500 \
  --vehicles 500 \
  --rides 50000 \
  --seed 42
```

### Reproducibility

All data is deterministic. Same seed → same data:
```python
from scripts.generate_data import MockDataGenerator

gen = MockDataGenerator(seed=42)
gen.passenger_count = 1000
gen.driver_count = 200
gen.vehicle_count = 200
gen.ride_count = 10000

data = gen.save_data("data/")
# Always produces identical results
```

## Privacy

**This is completely synthetic data.** No real customer data is used.

- Names generated from randomized pools of common first/last names
- Emails follow pattern `entity_type{id}@example.com`
- Phone numbers generated in +1XXX format (not real)
- No PII, no real customer records, no privacy concerns

---

## Next Steps

1. ✅ Generate mock data locally
2. → Upload to S3 RAW layer
3. → Run Glue ETL to BRONZE layer
4. → Implement SILVER transformations
5. → Build GOLD analytics tables

See [README.md](README.md) for full pipeline overview.
