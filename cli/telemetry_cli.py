class TelemetryCLI:
    def __init__(self, telemetry_service):
        self.telemetry_service = telemetry_service

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
            self.telemetry_service.register_device(
                device_id=device_id,
                name=name,
                device_type=device_type,
                location=location,
            )
        except ValueError as exc:
            print(exc)
            return

        print("Device registered.")

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
