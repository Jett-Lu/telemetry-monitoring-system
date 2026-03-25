from collections import defaultdict

from api.crux_client import CrUXClient
from services.report_strategies import PlainTextReportStrategy


class ReportService:
    def __init__(self, telemetry_service, crux_client=None, report_strategy=None):
        self.telemetry_service = telemetry_service
        self.crux_client = crux_client or CrUXClient()
        self.report_strategy = report_strategy or PlainTextReportStrategy()

    def generate_text_report(self, device_id=None, start_date=None, end_date=None):
        telemetry_rows = self.telemetry_service.get_telemetry_data(
            device_id=device_id,
            start_date=start_date,
            end_date=end_date,
        )
        telemetry_summary = self._summarize_telemetry(telemetry_rows)
        crux_data = self._safe_get_crux()
        return self.report_strategy.format_report(telemetry_summary, crux_data)

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

    def _safe_get_crux(self):
        try:
            return self.crux_client.get_performance_data()
        except Exception as exc:
            return {
                "error": True,
                "message": f"Unable to retrieve CrUX data: {exc}",
            }
