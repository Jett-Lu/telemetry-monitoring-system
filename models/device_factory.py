from models.device import Device


class DeviceFactory:
    @staticmethod
    def create_device(device_id, name, device_type, location):
        return Device(
            device_id=device_id,
            name=name,
            device_type=device_type,
            location=location,
        )
