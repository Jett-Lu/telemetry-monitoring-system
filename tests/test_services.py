import unittest
from datetime import datetime

from models.device import Device
from services.device_service import DeviceService
from services.report_service import ReportService
from services.telemetry_service import TelemetryService


class FakeDeviceRepository:
    def __init__(self):
        self.devices = {}

    def get_by_device_id(self, device_id):
        return self.devices.get(device_id)

    def insert(self, device):
        self.devices[device.device_id] = device
        return device

    def get_all(self):
        return list(self.devices.values())


class FakeTelemetryRepository:
    def __init__(self):
        self.rows = []

    def insert_telemetry(self, device_id, metric_type, metric_value, timestamp=None):
        self.rows.append(
            {
                "device_id": device_id,
                "metric_type": metric_type,
                "metric_value": metric_value,
                "timestamp": timestamp or datetime(2026, 3, 25, 12, 0, 0),
            }
        )

    def get_history(self, device_id=None, start_date=None, end_date=None):
        results = self.rows

        if device_id:
            results = [row for row in results if row["device_id"] == device_id]
        if start_date:
            results = [row for row in results if row["timestamp"] >= start_date]
        if end_date:
            results = [row for row in results if row["timestamp"] <= end_date]

        normalized = []
        for row in results:
            normalized.append(
                {
                    "device_id": row["device_id"],
                    "metric_type": row["metric_type"],
                    "metric_value": row["metric_value"],
                    "timestamp": row["timestamp"].isoformat(sep=" ", timespec="seconds"),
                }
            )
        return normalized


class FakeCrUXClient:
    def get_performance_data(self):
        return {
            "origin": "https://www.mcmaster.ca/",
            "metrics": {
                "lcp": {"percentile": 2100, "unit": "ms", "rating": "good"},
                "ttfb": {"percentile": 700, "unit": "ms", "rating": "good"},
                "fcp": {"percentile": 1500, "unit": "ms", "rating": "good"},
                "cls": {"percentile": 0.08, "unit": "unitless", "rating": "good"},
            },
        }


class DeviceServiceTests(unittest.TestCase):
    def test_register_device_stores_device(self):
        repository = FakeDeviceRepository()
        service = DeviceService(repository)

        device = service.register_device("device-001", "Sensor", "sensor", "Lab")

        self.assertEqual(device.device_id, "device-001")
        self.assertEqual(repository.get_by_device_id("device-001").name, "Sensor")

    def test_register_device_rejects_duplicate_device_id(self):
        repository = FakeDeviceRepository()
        service = DeviceService(repository)
        service.register_device("device-001", "Sensor", "sensor", "Lab")

        with self.assertRaises(ValueError):
            service.register_device("device-001", "Other", "sensor", "Office")


class TelemetryServiceTests(unittest.TestCase):
    def test_log_telemetry_requires_registered_device(self):
        device_repository = FakeDeviceRepository()
        telemetry_repository = FakeTelemetryRepository()
        service = TelemetryService(telemetry_repository, device_repository)

        with self.assertRaises(ValueError):
            service.log_telemetry("missing-device", "cpu", 50.0)

    def test_log_telemetry_stores_row_for_registered_device(self):
        device_repository = FakeDeviceRepository()
        telemetry_repository = FakeTelemetryRepository()
        device_repository.insert(Device("device-001", "Sensor", "sensor", "Lab"))
        service = TelemetryService(telemetry_repository, device_repository)

        service.log_telemetry("device-001", "cpu", 42.5, "2026-03-25 14:30:00")

        self.assertEqual(len(telemetry_repository.rows), 1)
        self.assertEqual(telemetry_repository.rows[0]["metric_type"], "cpu")

    def test_retrieve_history_filters_by_device_id(self):
        device_repository = FakeDeviceRepository()
        telemetry_repository = FakeTelemetryRepository()
        device_repository.insert(Device("device-001", "Sensor", "sensor", "Lab"))
        device_repository.insert(Device("device-002", "Node", "server", "DC"))
        service = TelemetryService(telemetry_repository, device_repository)

        service.log_telemetry("device-001", "cpu", 42.5, "2026-03-25 14:30:00")
        service.log_telemetry("device-002", "cpu", 55.0, "2026-03-25 14:35:00")

        rows = service.retrieve_history(device_id="device-001")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["device_id"], "device-001")


class ReportServiceTests(unittest.TestCase):
    def test_generate_text_report_contains_summary_and_crux_metrics(self):
        device_repository = FakeDeviceRepository()
        telemetry_repository = FakeTelemetryRepository()
        device_repository.insert(Device("device-001", "Sensor", "sensor", "Lab"))
        telemetry_service = TelemetryService(telemetry_repository, device_repository)
        telemetry_service.log_telemetry("device-001", "cpu", 40.0, "2026-03-25 14:30:00")
        telemetry_service.log_telemetry("device-001", "cpu", 60.0, "2026-03-25 14:35:00")
        report_service = ReportService(telemetry_service, crux_client=FakeCrUXClient())

        report = report_service.generate_text_report()

        self.assertIn("SentinelLog Report", report)
        self.assertIn("avg=50.00", report)
        self.assertIn("LCP: 2100 ms (good)", report)
        self.assertIn("TTFB: 700 ms (good)", report)


if __name__ == "__main__":
    unittest.main()
