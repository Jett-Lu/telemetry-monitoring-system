import unittest

from api.uptime_adapter import UptimeAdapter
from services.uptime_service import UptimeService


class UptimeAdapterTests(unittest.TestCase):
    def test_adapter_maps_monitor_payload(self):
        adapter = UptimeAdapter()
        payload = {
            "friendly_name": "McMaster Website",
            "status": 2,
            "all_time_uptime_ratio": "99.98",
            "response_times": [{"value": "215", "datetime": "1712016000"}],
        }

        result = adapter.adapt(payload)

        self.assertEqual(result["monitor_name"], "McMaster Website")
        self.assertEqual(result["status"], "Up")
        self.assertEqual(result["uptime_percentage"], 99.98)
        self.assertEqual(result["response_time"], 215.0)
        self.assertEqual(result["last_checked"], "1712016000")


class FakeUptimeClient:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def get_monitor_status(self):
        if self.error:
            raise self.error
        return self.payload


class UptimeServiceTests(unittest.TestCase):
    def test_service_returns_normalized_uptime_data(self):
        payload = {
            "monitor_name": "McMaster Website",
            "status": "Up",
            "uptime_percentage": 99.98,
            "response_time": 215.0,
            "last_checked": "1712016000",
        }
        service = UptimeService(uptime_client=FakeUptimeClient(payload=payload))

        result = service.get_uptime_status()

        self.assertEqual(result["status"], "Up")
        self.assertEqual(result["response_time"], 215.0)

    def test_service_handles_api_failure_gracefully(self):
        service = UptimeService(uptime_client=FakeUptimeClient(error=RuntimeError("boom")))

        result = service.get_uptime_status()

        self.assertTrue(result["error"])
        self.assertIn("Uptime data unavailable", result["message"])


if __name__ == "__main__":
    unittest.main()
