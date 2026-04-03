from api.uptime_client import UptimeRobotClient


class UptimeService:
    def __init__(self, uptime_client=None):
        self.uptime_client = uptime_client or UptimeRobotClient()

    def get_uptime_status(self):
        try:
            return self.uptime_client.get_monitor_status()
        except Exception as exc:
            return {
                "error": True,
                "message": f"Uptime data unavailable: {exc}",
            }
