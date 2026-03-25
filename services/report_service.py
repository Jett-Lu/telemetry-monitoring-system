from collections import defaultdict

from api.crux_client import CrUXClient, DEFAULT_TARGET_URL
from api.uptime_client import UptimeRobotClient


class ReportService:
    def __init__(self, telemetry_service, uptime_client=None, crux_client=None):
        self.telemetry_service = telemetry_service
        self.uptime_client = uptime_client or UptimeRobotClient()
        self.crux_client = crux_client or CrUXClient()

    def generate_text_report(self, device_id=None, start_date=None, end_date=None):
        telemetry_rows = self.telemetry_service.get_telemetry_data(
            device_id=device_id,
            start_date=start_date,
            end_date=end_date,
        )
        telemetry_summary = self._summarize_telemetry(telemetry_rows)
        uptime_data = self._safe_get_uptime()
        crux_data = self._safe_get_crux()

        sections = [
            "SentinelLog Report",
            "",
            self._format_telemetry_section(telemetry_summary),
            "",
            self._format_service_health_section(uptime_data, crux_data),
        ]
        return "\n".join(sections).strip()

    def _summarize_telemetry(self, telemetry_rows):
        grouped = defaultdict(list)

        for row in telemetry_rows:
            key = (row["device_id"], row["metric_type"])
            grouped[key].append(float(row["metric_value"]))

        summary = []
        for (device_id, metric_type), values in sorted(grouped.items()):
            summary.append(
                {
                    "device_id": device_id,
                    "metric_type": metric_type,
                    "average": sum(values) / len(values),
                    "minimum": min(values),
                    "maximum": max(values),
                    "samples": len(values),
                }
            )

        return summary

    def _safe_get_uptime(self):
        try:
            return self.uptime_client.get_monitor_status(DEFAULT_TARGET_URL)
        except Exception as exc:
            return {
                "error": True,
                "message": f"Unable to retrieve UptimeRobot data: {exc}",
            }

    def _safe_get_crux(self):
        try:
            return self.crux_client.get_performance_data(DEFAULT_TARGET_URL)
        except Exception as exc:
            return {
                "error": True,
                "message": f"Unable to retrieve CrUX data: {exc}",
            }

    def _format_telemetry_section(self, telemetry_summary):
        lines = ["Telemetry Summary"]

        if not telemetry_summary:
            lines.append("No telemetry data found for the selected filters.")
            return "\n".join(lines)

        for item in telemetry_summary:
            lines.append(
                (
                    f"- Device {item['device_id']} | {item['metric_type']}: "
                    f"avg={item['average']:.2f}, "
                    f"min={item['minimum']:.2f}, "
                    f"max={item['maximum']:.2f}, "
                    f"samples={item['samples']}"
                )
            )

        return "\n".join(lines)

    def _format_service_health_section(self, uptime_data, crux_data):
        lines = ["Service Health", f"Target: {DEFAULT_TARGET_URL}"]

        lines.extend(self._format_uptime_lines(uptime_data))
        lines.extend(self._format_crux_lines(crux_data))
        return "\n".join(lines)

    def _format_uptime_lines(self, uptime_data):
        lines = ["", "UptimeRobot"]

        if uptime_data.get("error"):
            lines.append(f"- Error: {uptime_data.get('message', 'Unavailable')}")
            return lines

        lines.append(f"- Status: {uptime_data.get('status', 'unknown')}")
        lines.append(f"- Uptime: {self._format_percent(uptime_data.get('uptime_ratio'))}")
        lines.append(
            "- Latest response time: "
            f"{self._format_ms(uptime_data.get('latest_response_time_ms'))}"
        )
        lines.append(
            "- Average response time: "
            f"{self._format_ms(uptime_data.get('average_response_time_ms'))}"
        )
        return lines

    def _format_crux_lines(self, crux_data):
        lines = ["", "CrUX"]

        if crux_data.get("error"):
            lines.append(f"- Error: {crux_data.get('message', 'Unavailable')}")
            return lines

        metrics = crux_data.get("metrics", {})
        lines.append(f"- LCP: {self._format_crux_metric(metrics.get('lcp'))}")
        lines.append(f"- TTFB: {self._format_crux_metric(metrics.get('ttfb'))}")
        lines.append(f"- FCP: {self._format_crux_metric(metrics.get('fcp'))}")
        lines.append(f"- CLS: {self._format_crux_metric(metrics.get('cls'))}")
        return lines

    def _format_crux_metric(self, metric):
        if not metric:
            return "Unavailable"

        percentile = metric.get("percentile")
        unit = metric.get("unit")
        rating = metric.get("rating") or "unknown"

        if percentile is None:
            return f"Unavailable ({rating})"

        suffix = "" if unit == "unitless" else " ms"
        return f"{percentile}{suffix} ({rating})"

    def _format_percent(self, value):
        if value is None:
            return "Unavailable"
        return f"{value:.2f}%"

    def _format_ms(self, value):
        if value is None:
            return "Unavailable"
        return f"{value:.0f} ms"
