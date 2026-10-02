"""Transformation logic for ETL pipeline."""

from typing import Dict, Any, List
from datetime import datetime


class BronzeTransformations:
    """Minimal transformations for Bronze layer (1:1 with source)."""

    @staticmethod
    def passenger(record: Dict[str, Any]) -> Dict[str, Any]:
        """Bronze passenger transformation (minimal)."""
        return {
            "passenger_id": record.get("passenger_id"),
            "first_name": record.get("first_name"),
            "last_name": record.get("last_name"),
            "email": record.get("email"),
            "phone": record.get("phone"),
            "signup_timestamp": record.get("signup_timestamp"),
            "city": record.get("city"),
            "country": record.get("country"),
            "status": record.get("status"),
        }

    @staticmethod
    def driver(record: Dict[str, Any]) -> Dict[str, Any]:
        """Bronze driver transformation (minimal)."""
        return {
            "driver_id": record.get("driver_id"),
            "first_name": record.get("first_name"),
            "last_name": record.get("last_name"),
            "signup_timestamp": record.get("signup_timestamp"),
            "rating": float(record.get("rating", 0)),
            "city": record.get("city"),
            "country": record.get("country"),
            "status": record.get("status"),
        }

    @staticmethod
    def vehicle(record: Dict[str, Any]) -> Dict[str, Any]:
        """Bronze vehicle transformation (minimal)."""
        return {
            "vehicle_id": record.get("vehicle_id"),
            "driver_id": record.get("driver_id"),
            "make": record.get("make"),
            "model": record.get("model"),
            "year": int(record.get("year", 0)),
            "vehicle_type": record.get("vehicle_type"),
            "license_plate": record.get("license_plate"),
        }

    @staticmethod
    def ride(record: Dict[str, Any]) -> Dict[str, Any]:
        """Bronze ride transformation (minimal)."""
        return {
            "ride_id": record.get("ride_id"),
            "passenger_id": record.get("passenger_id"),
            "driver_id": record.get("driver_id"),
            "vehicle_id": record.get("vehicle_id"),
            "request_timestamp": record.get("request_timestamp"),
            "pickup_timestamp": record.get("pickup_timestamp"),
            "dropoff_timestamp": record.get("dropoff_timestamp"),
            "pickup_latitude": float(record.get("pickup_latitude", 0)),
            "pickup_longitude": float(record.get("pickup_longitude", 0)),
            "dropoff_latitude": float(record.get("dropoff_latitude", 0)),
            "dropoff_longitude": float(record.get("dropoff_longitude", 0)),
            "pickup_city": record.get("pickup_city"),
            "dropoff_city": record.get("dropoff_city"),
            "distance_km": float(record.get("distance_km", 0)),
            "duration_minutes": int(record.get("duration_minutes", 0)),
            "fare_amount": float(record.get("fare_amount", 0)),
            "currency": record.get("currency"),
            "ride_status": record.get("ride_status"),
        }

    @staticmethod
    def payment(record: Dict[str, Any]) -> Dict[str, Any]:
        """Bronze payment transformation (minimal)."""
        return {
            "payment_id": record.get("payment_id"),
            "ride_id": record.get("ride_id"),
            "payment_timestamp": record.get("payment_timestamp"),
            "payment_method": record.get("payment_method"),
            "amount": float(record.get("amount", 0)),
            "currency": record.get("currency"),
            "payment_status": record.get("payment_status"),
        }


class SilverTransformations:
    """Cleaning and standardization for Silver layer."""

    @staticmethod
    def passenger(record: Dict[str, Any]) -> Dict[str, Any]:
        """Silver passenger transformation (cleaned, standardized)."""
        signup_ts = record.get("signup_timestamp", "")
        signup_date = None
        if signup_ts:
            try:
                signup_date = datetime.fromisoformat(signup_ts).date()
            except (ValueError, TypeError):
                pass

        return {
            "passenger_id": record.get("passenger_id", ""),
            "first_name": (record.get("first_name", "") or "").strip(),
            "last_name": (record.get("last_name", "") or "").strip(),
            "email": (record.get("email", "") or "").lower().strip(),
            "phone": (record.get("phone", "") or "").strip(),
            "signup_date": signup_date,
            "city": (record.get("city", "") or "").strip(),
            "country": (record.get("country", "") or "").strip(),
            "status": (record.get("status", "") or "").lower().strip(),
        }

    @staticmethod
    def driver(record: Dict[str, Any]) -> Dict[str, Any]:
        """Silver driver transformation (cleaned, standardized)."""
        signup_ts = record.get("signup_timestamp", "")
        signup_date = None
        if signup_ts:
            try:
                signup_date = datetime.fromisoformat(signup_ts).date()
            except (ValueError, TypeError):
                pass

        return {
            "driver_id": record.get("driver_id", ""),
            "first_name": (record.get("first_name", "") or "").strip(),
            "last_name": (record.get("last_name", "") or "").strip(),
            "signup_date": signup_date,
            "rating": min(5.0, max(0.0, float(record.get("rating", 0)))),  # Clamp to 0-5
            "city": (record.get("city", "") or "").strip(),
            "country": (record.get("country", "") or "").strip(),
            "status": (record.get("status", "") or "").lower().strip(),
        }

    @staticmethod
    def vehicle(record: Dict[str, Any]) -> Dict[str, Any]:
        """Silver vehicle transformation (cleaned, standardized)."""
        return {
            "vehicle_id": record.get("vehicle_id", ""),
            "driver_id": record.get("driver_id", ""),
            "make": (record.get("make", "") or "").strip(),
            "model": (record.get("model", "") or "").strip(),
            "year": max(1900, min(2050, int(record.get("year", 2000)))),  # Reasonable year range
            "vehicle_type": (record.get("vehicle_type", "") or "").lower().strip(),
            "license_plate": (record.get("license_plate", "") or "").upper().strip(),
        }

    @staticmethod
    def ride(record: Dict[str, Any]) -> Dict[str, Any]:
        """Silver ride transformation (cleaned, standardized, structured)."""
        request_ts = record.get("request_timestamp", "")
        request_date = None
        if request_ts:
            try:
                dt = datetime.fromisoformat(request_ts)
                request_date = dt.date()
            except (ValueError, TypeError):
                pass

        return {
            "ride_id": record.get("ride_id", ""),
            "passenger_id": record.get("passenger_id", ""),
            "driver_id": record.get("driver_id", ""),
            "vehicle_id": record.get("vehicle_id", ""),
            "request_date": request_date,
            "request_time": record.get("request_timestamp", ""),
            "pickup_time": record.get("pickup_timestamp", ""),
            "dropoff_time": record.get("dropoff_timestamp", ""),
            "pickup_location": {
                "latitude": float(record.get("pickup_latitude", 0)),
                "longitude": float(record.get("pickup_longitude", 0)),
                "city": (record.get("pickup_city", "") or "").strip(),
            },
            "dropoff_location": {
                "latitude": float(record.get("dropoff_latitude", 0)),
                "longitude": float(record.get("dropoff_longitude", 0)),
                "city": (record.get("dropoff_city", "") or "").strip(),
            },
            "distance_km": max(0, float(record.get("distance_km", 0))),
            "duration_minutes": max(0, int(record.get("duration_minutes", 0))),
            "fare_amount": max(0, float(record.get("fare_amount", 0))),
            "currency": (record.get("currency", "USD") or "USD").upper(),
            "ride_status": (record.get("ride_status", "") or "").lower(),
        }

    @staticmethod
    def payment(record: Dict[str, Any]) -> Dict[str, Any]:
        """Silver payment transformation (cleaned, standardized)."""
        payment_ts = record.get("payment_timestamp", "")
        payment_date = None
        if payment_ts:
            try:
                dt = datetime.fromisoformat(payment_ts)
                payment_date = dt.date()
            except (ValueError, TypeError):
                pass

        return {
            "payment_id": record.get("payment_id", ""),
            "ride_id": record.get("ride_id", ""),
            "payment_date": payment_date,
            "payment_time": payment_ts,
            "payment_method": (record.get("payment_method", "") or "").lower().strip(),
            "amount": max(0, float(record.get("amount", 0))),
            "currency": (record.get("currency", "USD") or "USD").upper(),
            "payment_status": (record.get("payment_status", "") or "").lower().strip(),
        }


class AggregationLogic:
    """Aggregation logic for Gold layer."""

    @staticmethod
    def calculate_daily_ride_metrics(rides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate daily ride metrics by city."""
        from collections import defaultdict
        from datetime import datetime

        metrics = defaultdict(lambda: {
            "total_rides": 0,
            "completed_rides": 0,
            "cancelled_rides": 0,
            "distances": [],
            "revenues": [],
            "durations": [],
        })

        for ride in rides:
            if not isinstance(ride, dict):
                continue

            try:
                request_ts = datetime.fromisoformat(ride.get("request_timestamp", ""))
                date = request_ts.date()
                pickup_city = (ride.get("pickup_city") or "Unknown").strip()
                key = (date, pickup_city)

                metrics[key]["total_rides"] += 1

                if ride.get("ride_status") == "completed":
                    metrics[key]["completed_rides"] += 1
                    metrics[key]["revenues"].append(float(ride.get("fare_amount", 0)))
                    metrics[key]["distances"].append(float(ride.get("distance_km", 0)))
                    metrics[key]["durations"].append(int(ride.get("duration_minutes", 0)))
                else:
                    metrics[key]["cancelled_rides"] += 1
            except (ValueError, TypeError, KeyError):
                continue

        result = []
        for (date, city), data in metrics.items():
            total_distance = sum(data["distances"])
            total_revenue = sum(data["revenues"])

            result.append({
                "date": date,
                "city": city,
                "total_rides": data["total_rides"],
                "completed_rides": data["completed_rides"],
                "cancelled_rides": data["cancelled_rides"],
                "total_distance_km": round(total_distance, 2),
                "total_revenue": round(total_revenue, 2),
                "avg_fare": round(total_revenue / len(data["revenues"]), 2) if data["revenues"] else 0,
                "avg_distance_km": round(sum(data["distances"]) / len(data["distances"]), 2) if data["distances"] else 0,
                "avg_duration_minutes": round(sum(data["durations"]) / len(data["durations"]), 2) if data["durations"] else 0,
            })

        return result

    @staticmethod
    def calculate_driver_metrics(rides: List[Dict[str, Any]], drivers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate driver metrics."""
        from collections import defaultdict
        from datetime import datetime

        # Create driver rating lookup
        driver_ratings = {d.get("driver_id"): d.get("rating", 0) for d in drivers}

        metrics = defaultdict(lambda: {
            "completed_rides": 0,
            "distances": [],
            "revenues": [],
        })

        for ride in rides:
            if not isinstance(ride, dict):
                continue

            try:
                request_ts = datetime.fromisoformat(ride.get("request_timestamp", ""))
                date = request_ts.date()
                driver_id = ride.get("driver_id")
                key = (date, driver_id)

                if ride.get("ride_status") == "completed":
                    metrics[key]["completed_rides"] += 1
                    metrics[key]["distances"].append(float(ride.get("distance_km", 0)))
                    metrics[key]["revenues"].append(float(ride.get("fare_amount", 0)))
            except (ValueError, TypeError, KeyError):
                continue

        result = []
        for (date, driver_id), data in metrics.items():
            result.append({
                "date": date,
                "driver_id": driver_id,
                "completed_rides": data["completed_rides"],
                "total_distance_km": round(sum(data["distances"]), 2),
                "total_revenue": round(sum(data["revenues"]), 2),
                "avg_rating": driver_ratings.get(driver_id, 0),
            })

        return result
