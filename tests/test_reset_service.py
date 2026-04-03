import unittest
from io import StringIO
from unittest.mock import patch

from cli.telemetry_cli import TelemetryCLI
from services.database_reset_service import DatabaseResetService


class FakeDeviceRepository:
    def __init__(self, deleted_count=2):
        self.deleted_count = deleted_count
        self.cleared = False

    def delete_all(self):
        self.cleared = True
        return self.deleted_count


class FakeTelemetryRepository:
    def __init__(self, deleted_count=5):
        self.deleted_count = deleted_count
        self.cleared = False

    def delete_all(self):
        self.cleared = True
        return self.deleted_count


class FakeNoOpService:
    pass


class DatabaseResetServiceTests(unittest.TestCase):
    def test_clear_all_data_deletes_telemetry_and_devices(self):
        device_repository = FakeDeviceRepository(deleted_count=2)
        telemetry_repository = FakeTelemetryRepository(deleted_count=5)
        service = DatabaseResetService(device_repository, telemetry_repository)

        result = service.clear_all_data()

        self.assertTrue(device_repository.cleared)
        self.assertTrue(telemetry_repository.cleared)
        self.assertEqual(result["devices_deleted"], 2)
        self.assertEqual(result["telemetry_deleted"], 5)


class TelemetryCLIClearDataTests(unittest.TestCase):
    def test_prompt_clear_all_data_requires_yes_confirmation(self):
        reset_service = DatabaseResetService(
            FakeDeviceRepository(),
            FakeTelemetryRepository(),
        )
        cli = TelemetryCLI(
            FakeNoOpService(),
            FakeNoOpService(),
            FakeNoOpService(),
            reset_service,
        )

        with patch("builtins.input", side_effect=["no"]), patch(
            "sys.stdout", new_callable=StringIO
        ) as stdout:
            cli.prompt_clear_all_data()

        self.assertIn("Clear data cancelled.", stdout.getvalue())

    def test_prompt_clear_all_data_executes_reset_on_yes(self):
        reset_service = DatabaseResetService(
            FakeDeviceRepository(deleted_count=1),
            FakeTelemetryRepository(deleted_count=3),
        )
        cli = TelemetryCLI(
            FakeNoOpService(),
            FakeNoOpService(),
            FakeNoOpService(),
            reset_service,
        )

        with patch("builtins.input", side_effect=["yes"]), patch(
            "sys.stdout", new_callable=StringIO
        ) as stdout:
            cli.prompt_clear_all_data()

        output = stdout.getvalue()
        self.assertIn("All data cleared.", output)
        self.assertIn("Removed 3 telemetry records and 1 devices.", output)


if __name__ == "__main__":
    unittest.main()
