from datetime import datetime


class Telemetry:
    def __init__(self, device_id, metric_type, metric_value, timestamp):
        self.device_id = device_id
        self.metric_type = metric_type
        self.metric_value = metric_value
        self.timestamp = timestamp

    @classmethod
    def from_row(cls, row):
        return cls(
            device_id=row[0],
            metric_type=row[1],
            metric_value=row[2],
            timestamp=row[3],
        )

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "metric_type": self.metric_type,
            "metric_value": self.metric_value,
            "timestamp": self._format_timestamp(self.timestamp),
        }

    @staticmethod
    def _format_timestamp(value):
        if isinstance(value, datetime):
            return value.isoformat(sep=" ", timespec="seconds")
        return value
