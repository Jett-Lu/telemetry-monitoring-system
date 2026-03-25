from models.device_factory import DeviceFactory


class DeviceService:
    def __init__(self, device_repository):
        self.device_repository = device_repository

    def register_device(self, device_id, name, device_type, location):
        existing_device = self.device_repository.get_by_device_id(device_id)
        if existing_device is not None:
            raise ValueError(f"Device '{device_id}' is already registered.")

        device = DeviceFactory.create_device(
            device_id=device_id,
            name=name,
            device_type=device_type,
            location=location,
        )
        return self.device_repository.insert(device)

    def get_device(self, device_id):
        return self.device_repository.get_by_device_id(device_id)

    def list_devices(self):
        return self.device_repository.get_all()
