import os

import requests


DEFAULT_CRUX_API_KEY = "AIzaSyAaNOVctBMisDcxT3EMib0a-SXS14SUdSI"
DEFAULT_TARGET_URL = "https://www.mcmaster.ca/"


class CrUXClient:
    BASE_URL = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"
    METRIC_KEYS = {
        "largest_contentful_paint": "lcp",
        "experimental_time_to_first_byte": "ttfb",
        "first_contentful_paint": "fcp",
        "cumulative_layout_shift": "cls",
    }

    def __init__(self, api_key=None, timeout=15):
        self.api_key = api_key or os.getenv("CRUX_API_KEY", DEFAULT_CRUX_API_KEY)
        self.timeout = timeout

    def _classify_metric(self, metric_name, value):
        if value is None:
            return None

        thresholds = {
            "lcp": (2500, 4000),
            "ttfb": (800, 1800),
            "fcp": (1800, 3000),
            "cls": (0.1, 0.25),
        }
        good, poor = thresholds[metric_name]

        if value <= good:
            return "good"
        if value <= poor:
            return "needs_improvement"
        return "poor"

    def _format_metric(self, api_name, payload):
        short_name = self.METRIC_KEYS[api_name]
        percentile = payload.get("percentiles", {}).get("p75")
        if percentile is None:
            percentile = payload.get("percentiles", {}).get("P75")

        return {
            "name": short_name,
            "percentile": percentile,
            "unit": "unitless" if short_name == "cls" else "ms",
            "rating": self._classify_metric(short_name, percentile),
            "histogram": payload.get("histogram", []),
            "densities": payload.get("fractions", []),
        }

    def _format_record(self, record, queried_url):
        metrics = record.get("metrics", {})
        formatted_metrics = {}

        for api_name, short_name in self.METRIC_KEYS.items():
            payload = metrics.get(api_name)
            formatted_metrics[short_name] = (
                self._format_metric(api_name, payload) if payload else None
            )

        return {
            "service": "crux",
            "target": queried_url,
            "record_type": "origin" if record.get("key", {}).get("origin") else "url",
            "collection_period": record.get("collectionPeriod"),
            "metrics": formatted_metrics,
        }

    def get_performance_data(self, url=DEFAULT_TARGET_URL):
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
            return self._format_record(record, url)

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
