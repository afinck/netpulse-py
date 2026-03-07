"""
Database module for Netpulse
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import get_config

logger = logging.getLogger(__name__)


class Database:
    """Database manager for network measurements"""

    def __init__(self, db_path=None):
        config = get_config()
        self.db_path = db_path or config.get("database.path")
        self.ensure_database()

    def ensure_database(self):
        """Ensure database exists and tables are created"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    download_speed REAL NOT NULL,
                    upload_speed REAL,
                    latency REAL NOT NULL,
                    jitter REAL,
                    packet_loss REAL,
                    server_name TEXT,
                    test_type TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for better performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON measurements(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_test_type ON measurements(test_type)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_created_at ON measurements(created_at)"
            )

            conn.commit()

    def add_measurement(self, measurement: Dict) -> int:
        """Add a new measurement to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO measurements (
                        timestamp, download_speed, upload_speed, latency,
                        jitter, packet_loss, server_name, test_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        measurement["timestamp"],
                        measurement["download_speed"],
                        measurement.get("upload_speed"),
                        measurement["latency"],
                        measurement.get("jitter"),
                        measurement.get("packet_loss"),
                        measurement.get("server_name"),
                        measurement["test_type"],
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add measurement: {e}")
            raise

    def get_measurements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        test_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Get measurements from the database"""
        query = "SELECT * FROM measurements WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        if test_type:
            query += " AND test_type = ?"
            params.append(test_type)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get measurements: {e}")
            return []

    def get_latest_measurements(self, count: int = 10) -> List[Dict]:
        """Get the latest measurements"""
        return self.get_measurements(limit=count)

    def get_measurements_by_period(self, period: str) -> List[Dict]:
        """Get measurements by time period (day, week, month, year)"""
        now = datetime.now()

        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
        else:
            raise ValueError(f"Invalid period: {period}")

        start_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        return self.get_measurements(start_date=start_str)

    def get_statistics(self, period: str = "day") -> Dict:
        """Get statistics for a time period"""
        measurements = self.get_measurements_by_period(period)

        if not measurements:
            return {}

        download_speeds = [
            m["download_speed"] for m in measurements if m["download_speed"]
        ]
        upload_speeds = [
            m["upload_speed"] for m in measurements if m.get("upload_speed")
        ]
        latencies = [m["latency"] for m in measurements if m["latency"]]

        stats = {
            "count": len(measurements),
            "period": period,
            "download_speed": {
                "min": min(download_speeds) if download_speeds else 0,
                "max": max(download_speeds) if download_speeds else 0,
                "avg": (
                    sum(download_speeds) / len(download_speeds)
                    if download_speeds
                    else 0
                ),
            },
            "upload_speed": {
                "min": min(upload_speeds) if upload_speeds else 0,
                "max": max(upload_speeds) if upload_speeds else 0,
                "avg": sum(upload_speeds) / len(upload_speeds) if upload_speeds else 0,
            },
            "latency": {
                "min": min(latencies) if latencies else 0,
                "max": max(latencies) if latencies else 0,
                "avg": sum(latencies) / len(latencies) if latencies else 0,
            },
        }

        return stats

    def cleanup_old_data(self, days: int = 30):
        """Remove measurements older than specified days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM measurements WHERE timestamp < ?", (cutoff_date,)
                )
                conn.commit()
                logger.info(f"Cleaned up {cursor.rowcount} old measurements")
                return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

    def export_to_csv(
        self,
        filename: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        """Export measurements to CSV file"""
        import csv

        measurements = self.get_measurements(start_date=start_date, end_date=end_date)

        if not measurements:
            logger.warning("No measurements to export")
            return

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "timestamp",
                "download_speed",
                "upload_speed",
                "latency",
                "jitter",
                "packet_loss",
                "server_name",
                "test_type",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for measurement in measurements:
                writer.writerow(
                    {field: measurement.get(field, "") for field in fieldnames}
                )

        logger.info(f"Exported {len(measurements)} measurements to {filename}")


# Global database instance - will be initialized when needed
db = None


def get_database(db_path=None):
    """Get a database instance, initializing if necessary"""
    global db
    if db is None or db_path is not None:
        db = Database(db_path)
    return db
