import os

import requests

from api.uptime_adapter import UptimeAdapter
from config.environment import get_tracked_origin


DEFAULT_MONITOR_NAME = "McMaster Website"


class UptimeRobotClient:
    BASE_URL = "https://api.uptimerobot.com/v2"

    def __init__(self, api_key=None, timeout=15, adapter=None):
        self.api_key = api_key or os.getenv("UPTIMEROBOT_API_KEY")
        if not self.api_key:
            raise RuntimeError("UPTIMEROBOT_API_KEY is not set.")
        self.timeout = timeout
        self.adapter = adapter or UptimeAdapter()

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

    def get_monitor_status(self, url=None, friendly_name=DEFAULT_MONITOR_NAME):
        url = url or get_tracked_origin()
        monitor = self._find_monitor(url)

        if monitor is None:
            self._create_monitor(url, friendly_name)
            monitor = self._find_monitor(url)

        if monitor is None:
            return {
                "error": True,
                "message": f"Monitor for {url} could not be created or retrieved.",
            }

        return self.adapter.adapt(monitor)
