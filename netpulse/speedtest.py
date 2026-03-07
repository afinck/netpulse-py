"""
Speedtest module for Netpulse
"""

import json
import logging
import re
import subprocess
from datetime import datetime
from typing import Dict, Optional

from .config import get_config
from .database import get_database

logger = logging.getLogger(__name__)


class SpeedtestRunner:
    """Runner for librespeed-cli speed tests"""

    def __init__(self):
        config = get_config()
        self.timeout = config.get("measurement.timeout_seconds", 30)
        self.retry_count = config.get("measurement.retry_count", 3)
        self.servers = config.get("measurement.servers", [])

    def check_librespeed(self) -> bool:
        """Check if librespeed-cli is available"""
        try:
            result = subprocess.run(
                ["librespeed-cli", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def run_speedtest(self) -> Optional[Dict]:
        """Run a complete speed test"""
        if not self.check_librespeed():
            logger.error("librespeed-cli not found")
            return None

        for attempt in range(self.retry_count):
            try:
                logger.info(
                    f"Running speed test (attempt {attempt + 1}/{self.retry_count})"
                )
                result = self._run_librespeed()

                if result:
                    measurement = self._parse_result(result)
                    if measurement:
                        return measurement

            except Exception as e:
                logger.error(f"Speed test attempt {attempt + 1} failed: {e}")

        logger.error("All speed test attempts failed")
        return None

    def _run_librespeed(self) -> Optional[str]:
        """Run librespeed-cli and return output"""
        cmd = ["librespeed-cli", "--json", "--simple", "--duration", "5"]

        if self.servers:
            cmd.extend(["--server", ",".join(map(str, self.servers))])

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout
            )

            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"librespeed-cli failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("librespeed-cli timed out")
            return None
        except Exception as e:
            logger.error(f"Failed to run librespeed-cli: {e}")
            return None

    def _parse_result(self, output: str) -> Optional[Dict]:
        """Parse librespeed-cli JSON output"""
        try:
            # librespeed-cli returns a JSON array, take the first element
            data = json.loads(output)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            elif not isinstance(data, dict):
                logger.error(f"Unexpected JSON format: {type(data)}")
                return None

            measurement = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "download_speed": 0.0,
                "upload_speed": 0.0,
                "latency": 0.0,
                "jitter": 0.0,
                "packet_loss": 0.0,
                "server_name": "",
                "test_type": "bandwidth",
            }

            # Extract download speed (librespeed-cli returns Mbps directly)
            if "download" in data:
                measurement["download_speed"] = float(data["download"])

            # Extract upload speed
            if "upload" in data:
                measurement["upload_speed"] = float(data["upload"])

            # Extract latency
            if "ping" in data:
                measurement["latency"] = float(data["ping"])

            # Extract jitter
            if "jitter" in data:
                measurement["jitter"] = float(data["jitter"])

            # Extract server info
            if "server" in data:
                server = data["server"]
                measurement["server_name"] = (
                    f"{server.get('name', 'Unknown')} ({server.get('country', 'Unknown')})"
                )

            return measurement

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON output: {e}")
            return None
        except KeyError as e:
            logger.error(f"Missing expected field in output: {e}")
            return None

    def run_latency_test(self) -> Optional[Dict]:
        """Run a simple latency test using ping"""
        try:
            # Use google.com as a reliable target
            cmd = ["ping", "-c", "4", "-W", "5", "8.8.8.8"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                return self._parse_ping_result(result.stdout)
            else:
                logger.error(f"Ping test failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Ping test timed out")
            return None
        except Exception as e:
            logger.error(f"Failed to run ping test: {e}")
            return None

    def _parse_ping_result(self, output: str) -> Optional[Dict]:
        """Parse ping output for latency measurement"""
        try:
            # Extract average latency from ping output
            # Try different patterns for different ping versions
            patterns = [
                r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms",  # Linux ping
                r"round-trip min/avg/max/stddev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms",  # macOS ping
                r"Average = ([\d.]+)ms",  # Windows ping
            ]

            for pattern in patterns:
                match = re.search(pattern, output)
                if match:
                    avg_latency = float(match.group(1))

                    measurement = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "download_speed": 0.0,
                        "upload_speed": 0.0,
                        "latency": avg_latency,
                        "jitter": 0.0,
                        "packet_loss": 0.0,
                        "server_name": "8.8.8.8 (Google DNS)",
                        "test_type": "latency",
                    }

                    return measurement

            logger.error("Could not parse ping output")
            return None

        except Exception as e:
            logger.error(f"Failed to parse ping result: {e}")
            return None

    def run_measurement(self, test_type: str = "bandwidth") -> bool:
        """Run a measurement and store it in the database"""
        if test_type == "bandwidth":
            measurement = self.run_speedtest()
        elif test_type == "latency":
            measurement = self.run_latency_test()
        else:
            logger.error(f"Unknown test type: {test_type}")
            return False

        if measurement:
            try:
                db = get_database()
                measurement_id = db.add_measurement(measurement)
                logger.info(
                    f"Stored measurement {measurement_id}: {measurement['test_type']} - "
                    f"DL: {measurement['download_speed']:.2f} Mbit/s, "
                    f"Latency: {measurement['latency']:.2f} ms"
                )
                return True
            except Exception as e:
                logger.error(f"Failed to store measurement: {e}")
                return False
        else:
            logger.error(f"No measurement data for {test_type} test")
            return False


def main():
    """Command line interface for manual testing"""
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Run network speed tests")
    parser.add_argument(
        "--type",
        choices=["bandwidth", "latency", "both"],
        default="bandwidth",
        help="Type of test to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = SpeedtestRunner()

    if not runner.check_librespeed():
        print("Error: librespeed-cli not found. Please install it first.")
        sys.exit(1)

    success = True

    if args.type in ["bandwidth", "both"]:
        print("Running bandwidth test...")
        success &= runner.run_measurement("bandwidth")

    if args.type in ["latency", "both"]:
        print("Running latency test...")
        success &= runner.run_measurement("latency")

    if success:
        print("Tests completed successfully")
    else:
        print("Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
