#!/usr/bin/env python3
"""
Upload generated raw data to S3.

Usage:
    python scripts/upload_raw.py
"""

import argparse
import boto3
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_raw_data(data_dir: str, bucket_name: str, prefix: str = "raw"):
    """Upload local data files to S3 raw layer."""
    s3 = boto3.client("s3")
    data_path = Path(data_dir)

    if not data_path.exists():
        logger.error(f"Data directory {data_dir} does not exist")
        return

    ingestion_date = datetime.now().strftime("%Y-%m-%d")

    # Upload each entity
    entities = ["passenger", "driver", "vehicle", "ride", "payment"]

    for entity in entities:
        entity_path = data_path / entity / f"{entity}s.jsonl"
        if not entity_path.exists():
            logger.warning(f"Missing {entity_path}")
            continue

        # S3 path: s3://bucket/raw/entity/ingestion_date=YYYY-MM-DD/
        s3_key = f"{prefix}/{entity}/ingestion_date={ingestion_date}/{entity}s.jsonl"

        try:
            logger.info(f"Uploading {entity}...")
            s3.upload_file(str(entity_path), bucket_name, s3_key)
            logger.info(f"  ✓ {s3_key}")
        except Exception as e:
            logger.error(f"  ✗ Upload failed: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Upload raw data to S3")
    parser.add_argument("--data-dir", default="data", help="Local data directory")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--prefix", default="raw", help="S3 prefix for raw data")

    args = parser.parse_args()
    upload_raw_data(args.data_dir, args.bucket, args.prefix)


if __name__ == "__main__":
    main()
