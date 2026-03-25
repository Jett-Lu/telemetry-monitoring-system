import os

import requests

from api.crux_adapter import CrUXAdapter
from config.environment import get_tracked_origin


class CrUXClient:
    BASE_URL = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"

    def __init__(self, api_key=None, timeout=15, adapter=None):
        self.api_key = api_key or os.getenv("CRUX_API_KEY")
        if not self.api_key:
            raise RuntimeError("CRUX_API_KEY is not set.")
        self.timeout = timeout
        self.adapter = adapter or CrUXAdapter()

    def get_performance_data(self, url=None):
        url = url or get_tracked_origin()
        response = requests.post(
            f"{self.BASE_URL}?key={self.api_key}",
            json={"origin": url},
            timeout=self.timeout,
        )

        try:
            data = response.json()
        except ValueError:
            data = {"raw_response": response.text}

        if response.status_code == 200:
            record = data.get("record")
            if not record:
                return {
                    "service": "crux",
                    "target": url,
                    "error": True,
                    "reason": "missing_record",
                    "message": "CrUX returned a successful response without record data.",
                }
            return self.adapter.adapt(record, url)

        error = data.get("error", {})
        message = error.get("message", "CrUX request failed.")
        status = error.get("status")

        insufficient_data = response.status_code == 404 or "insufficient" in message.lower()

        return {
            "service": "crux",
            "target": url,
            "error": True,
            "reason": "insufficient_data" if insufficient_data else "api_error",
            "status_code": response.status_code,
            "status": status,
            "message": message,
            "details": data,
        }
