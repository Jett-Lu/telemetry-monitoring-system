class TelemetryService:
    def __init__(self, telemetry_repository, weather_service, device_model):
        self.telemetry_repository = telemetry_repository
        self.weather_service = weather_service
        self.device_model = device_model

    def log_telemetry(self, device_id, metric_type, metric_value):
        device = self.device_model.get_by_device_id(
            self.telemetry_repository.conn, device_id
        )
        if device is None:
            raise ValueError(f"Device '{device_id}' is not registered.")
        self.telemetry_repository.insert_telemetry(device_id, metric_type, metric_value)

    def generate_report(self):
        telemetry_rows = self.telemetry_repository.get_all()
        weather = self.weather_service.get_weather()

        return {
            "telemetry": telemetry_rows,
            "weather": weather,
        }
