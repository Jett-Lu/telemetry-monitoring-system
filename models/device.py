class Device:
    def __init__(self, device_id, name, device_type, location):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.location = location

    @classmethod
    def from_row(cls, row):
        return cls(
            device_id=row[0],
            name=row[1],
            device_type=row[2],
            location=row[3],
        )

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "name": self.name,
            "type": self.device_type,
            "location": self.location,
        }
