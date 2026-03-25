import os

import requests


DEFAULT_UPTIMEROBOT_API_KEY = "u3391604-b88a84f7823b707c6572474a"
DEFAULT_MONITOR_URL = "https://www.mcmaster.ca/"
DEFAULT_MONITOR_NAME = "McMaster Website"


class UptimeRobotClient:
    BASE_URL = "https://api.uptimerobot.com/v2"
    STATUS_LABELS = {
        0: "paused",
        1: "not_checked_yet",
        2: "up",
        8: "seems_down",
        9: "down",
    }

    def __init__(self, api_key=None, timeout=15):
        self.api_key = api_key or os.getenv("UPTIMEROBOT_API_KEY", DEFAULT_UPTIMEROBOT_API_KEY)
        self.timeout = timeout

    def _post(self, endpoint, payload):
        response = requests.post(
            f"{self.BASE_URL}/{endpoint}",
            data={
                "api_key": self.api_key,
                "format": "json",
                **payload,
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        if data.get("stat") != "ok":
            raise RuntimeError(f"UptimeRobot API error: {data}")

        return data

    def _find_monitor(self, url):
        data = self._post(
            "getMonitors",
            {
                "response_times": 1,
                "response_times_limit": 1,
                "all_time_uptime_ratio": 1,
            },
        )

        for monitor in data.get("monitors", []):
            if monitor.get("url") == url:
                return monitor

        return None

    def _create_monitor(self, url, friendly_name=DEFAULT_MONITOR_NAME):
        data = self._post(
            "newMonitor",
            {
                "type": 1,
                "url": url,
                "friendly_name": friendly_name,
            },
        )
        monitor_id = data.get("monitor", {}).get("id")
        if not monitor_id:
            raise RuntimeError(f"UptimeRobot did not return a monitor id: {data}")
        return monitor_id

    def _coerce_float(self, value):
        if value in (None, ""):
            return None
        return float(value)

    def _format_monitor(self, monitor):
        response_times = monitor.get("response_times") or []
        latest_response = response_times[0] if response_times else {}

        status_code = monitor.get("status")
        return {
            "service": "uptimerobot",
            "target": monitor.get("url"),
            "friendly_name": monitor.get("friendly_name"),
            "monitor_id": monitor.get("id"),
            "status_code": status_code,
            "status": self.STATUS_LABELS.get(status_code, "unknown"),
            "uptime_ratio": self._coerce_float(monitor.get("all_time_uptime_ratio")),
            "average_response_time_ms": self._coerce_float(monitor.get("average_response_time")),
            "latest_response_time_ms": self._coerce_float(latest_response.get("value")),
            "latest_response_checked_at": latest_response.get("datetime"),
        }

    def get_monitor_status(self, url=DEFAULT_MONITOR_URL, friendly_name=DEFAULT_MONITOR_NAME):
        monitor = self._find_monitor(url)
        if monitor is None:
            self._create_monitor(url, friendly_name)
            monitor = self._find_monitor(url)

        if monitor is None:
            raise RuntimeError(f"Monitor for {url} could not be created or retrieved.")

        return self._format_monitor(monitor)
