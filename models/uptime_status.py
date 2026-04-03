class UptimeStatus:
    def __init__(
        self,
        monitor_name,
        status,
        uptime_percentage,
        response_time,
        last_checked,
    ):
        self.monitor_name = monitor_name
        self.status = status
        self.uptime_percentage = uptime_percentage
        self.response_time = response_time
        self.last_checked = last_checked

    def to_dict(self):
        return {
            "monitor_name": self.monitor_name,
            "status": self.status,
            "uptime_percentage": self.uptime_percentage,
            "response_time": self.response_time,
            "last_checked": self.last_checked,
        }
