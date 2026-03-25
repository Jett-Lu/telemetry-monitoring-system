from config.environment import get_tracked_origin


class ReportFormattingStrategy:
    def format_report(self, telemetry_summary, external_snapshot):
        raise NotImplementedError


class PlainTextReportStrategy(ReportFormattingStrategy):
    def format_report(self, telemetry_summary, external_snapshot):
        sections = [
            "SentinelLog Report",
            "",
            self._format_telemetry_section(telemetry_summary),
            "",
            self._format_external_section(external_snapshot),
        ]
        return "\n".join(sections).strip()

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

    def _format_external_section(self, external_snapshot):
        lines = ["External Performance", f"Target: {get_tracked_origin()}"]

        if external_snapshot.get("error"):
            lines.append(f"- Error: {external_snapshot.get('message', 'Unavailable')}")
            return "\n".join(lines)

        metrics = external_snapshot.get("metrics", {})
        lines.append(f"- LCP: {self._format_metric(metrics.get('lcp'))}")
        lines.append(f"- TTFB: {self._format_metric(metrics.get('ttfb'))}")
        lines.append(f"- FCP: {self._format_metric(metrics.get('fcp'))}")
        lines.append(f"- CLS: {self._format_metric(metrics.get('cls'))}")
        return "\n".join(lines)

    def _format_metric(self, metric):
        if not metric:
            return "Unavailable"

        percentile = metric.get("percentile")
        unit = metric.get("unit")
        rating = metric.get("rating") or "unknown"
        if percentile is None:
            return f"Unavailable ({rating})"

        suffix = "" if unit == "unitless" else " ms"
        return f"{percentile}{suffix} ({rating})"
