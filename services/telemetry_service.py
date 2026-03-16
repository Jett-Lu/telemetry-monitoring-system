class TelemetryService:
    def __init__(self, telemetry_repository, weather_service):
        self.telemetry_repository = telemetry_repository
        self.weather_service = weather_service

    def log_telemetry(self, device_id, metric_type, metric_value):
        self.telemetry_repository.insert_telemetry(device_id, metric_type, metric_value)

    def generate_report(self):
        telemetry_rows = self.telemetry_repository.get_all()
        weather = self.weather_service.get_weather()

        return {
            "telemetry": telemetry_rows,
            "weather": weather,
        }
