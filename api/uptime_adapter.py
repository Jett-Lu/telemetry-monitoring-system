from models.uptime_status import UptimeStatus


class UptimeAdapter:
    STATUS_LABELS = {
        0: "Paused",
        1: "Not checked yet",
        2: "Up",
        8: "Seems down",
        9: "Down",
    }

    def adapt(self, monitor):
        response_times = monitor.get("response_times") or []
        latest_response = response_times[0] if response_times else {}

        status = monitor.get("status")
        uptime_percentage = self._coerce_number(monitor.get("all_time_uptime_ratio"))
        response_time = self._coerce_number(
            latest_response.get("value", monitor.get("average_response_time"))
        )

        snapshot = UptimeStatus(
            monitor_name=monitor.get("friendly_name"),
            status=self.STATUS_LABELS.get(status, "Unknown"),
            uptime_percentage=uptime_percentage,
            response_time=response_time,
            last_checked=latest_response.get("datetime"),
        )
        return snapshot.to_dict()

    def _coerce_number(self, value):
        if value in (None, ""):
            return None

        if isinstance(value, (int, float)):
            return value

        return float(str(value).strip())
