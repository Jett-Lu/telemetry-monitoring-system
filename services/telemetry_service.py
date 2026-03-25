from datetime import datetime


class TelemetryService:
    def __init__(self, telemetry_repository, weather_service, device_model):
        self.telemetry_repository = telemetry_repository
        self.weather_service = weather_service
        self.device_model = device_model

    def register_device(self, device_id, name, device_type, location):
        conn = self.telemetry_repository.conn
        existing_device = self.device_model.get_by_device_id(conn, device_id)
        if existing_device is not None:
            raise ValueError(f"Device '{device_id}' is already registered.")

        device = self.device_model(device_id, name, device_type, location)
        device.create(conn)
        return device

    def log_telemetry(self, device_id, metric_type, metric_value, timestamp=None):
        device = self.device_model.get_by_device_id(
            self.telemetry_repository.conn, device_id
        )
        if device is None:
            raise ValueError(f"Device '{device_id}' is not registered.")
        parsed_timestamp = self._parse_timestamp(timestamp) if timestamp else None
        self.telemetry_repository.insert_telemetry(
            device_id, metric_type, metric_value, parsed_timestamp
        )

    def generate_report(self, device_id=None, start_date=None, end_date=None):
        if device_id:
            device = self.device_model.get_by_device_id(
                self.telemetry_repository.conn, device_id
            )
            if device is None:
                raise ValueError(f"Device '{device_id}' is not registered.")

        parsed_start = self._parse_timestamp(start_date) if start_date else None
        parsed_end = self._parse_timestamp(end_date) if end_date else None
        telemetry_rows = self.telemetry_repository.get_all(
            device_id=device_id,
            start_date=parsed_start,
            end_date=parsed_end,
        )
        weather = self.weather_service.get_weather()

        return {
            "telemetry": telemetry_rows,
            "weather": weather,
        }

    def _parse_timestamp(self, value):
        if isinstance(value, datetime):
            return value

        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                "Timestamp must use ISO format, for example 2026-03-25 14:30:00."
            ) from exc
