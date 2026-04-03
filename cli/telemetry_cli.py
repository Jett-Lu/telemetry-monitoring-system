class TelemetryCLI:
    def __init__(
        self,
        device_service,
        telemetry_service,
        report_service,
        database_reset_service,
    ):
        self.device_service = device_service
        self.telemetry_service = telemetry_service
        self.report_service = report_service
        self.database_reset_service = database_reset_service

    def prompt_device_registration(self):
        device_id = input("Device ID: ").strip()
        name = input("Device name: ").strip()
        device_type = input("Device type: ").strip()
        location = input("Device location: ").strip()

        validation_error = self._validate_device_fields(
            device_id, name, device_type, location
        )
        if validation_error:
            print(validation_error)
            return

        try:
            self.device_service.register_device(
                device_id=device_id,
                name=name,
                device_type=device_type,
                location=location,
            )
        except ValueError as exc:
            print(exc)
            return

        print("Device registered.")

    def list_devices(self):
        devices = self.device_service.list_devices()

        if not devices:
            print("No devices registered.")
            return

        print("\nRegistered Devices:")
        for device in devices:
            print(
                f"- {device.device_id} | {device.name} | "
                f"{device.device_type} | {device.location}"
            )

    def prompt_telemetry_logging(self):
        device_id = input("Device ID: ").strip()
        metric_type = input("Metric type: ").strip()
        timestamp = input(
            "Timestamp (optional, ISO format like 2026-03-25 14:30:00): "
        ).strip()

        try:
            metric_value = float(input("Metric value: ").strip())
        except ValueError:
            print("Metric value must be a number.")
            return

        try:
            self.telemetry_service.log_telemetry(
                device_id,
                metric_type,
                metric_value,
                timestamp=timestamp or None,
            )
        except ValueError as exc:
            print(exc)
            return

        print("Telemetry saved.")

    def prompt_telemetry_history(self):
        device_id = input("Filter by Device ID (optional): ").strip() or None
        start_date = input(
            "Start date (optional, ISO format like 2026-03-25 00:00:00): "
        ).strip() or None
        end_date = input(
            "End date (optional, ISO format like 2026-03-25 23:59:59): "
        ).strip() or None

        try:
            rows = self.telemetry_service.retrieve_history(
                device_id=device_id,
                start_date=start_date,
                end_date=end_date,
            )
        except ValueError as exc:
            print(exc)
            return

        if not rows:
            print("No telemetry records found for the selected filters.")
            return

        print("\nTelemetry History:")
        for row in rows:
            print(
                f"- {row['timestamp']} | {row['device_id']} | "
                f"{row['metric_type']} = {row['metric_value']}"
            )

    def prompt_report(self):
        report_device_id = input("Filter by Device ID (optional): ").strip() or None
        start_date = input(
            "Start date (optional, ISO format like 2026-03-25 00:00:00): "
        ).strip() or None
        end_date = input(
            "End date (optional, ISO format like 2026-03-25 23:59:59): "
        ).strip() or None

        try:
            report = self.report_service.generate_text_report(
                device_id=report_device_id,
                start_date=start_date,
                end_date=end_date,
            )
        except ValueError as exc:
            print(exc)
            return

        print()
        print(report)

    def prompt_clear_all_data(self):
        confirmation = input(
            "Are you sure you want to clear all data? (yes/no) "
        ).strip().lower()

        if confirmation != "yes":
            print("Clear data cancelled.")
            return

        result = self.database_reset_service.clear_all_data()
        print(
            "All data cleared. "
            f"Removed {result['telemetry_deleted']} telemetry records and "
            f"{result['devices_deleted']} devices."
        )

    def _validate_device_fields(self, device_id, name, device_type, location):
        if not device_id:
            return "Device ID is required."
        if not name:
            return "Device name is required."
        if not device_type:
            return "Device type is required."
        if not location:
            return "Device location is required."
        return None
