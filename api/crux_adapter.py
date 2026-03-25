from models.site_performance import SitePerformanceSnapshot


class CrUXAdapter:
    METRIC_KEYS = {
        "largest_contentful_paint": "lcp",
        "experimental_time_to_first_byte": "ttfb",
        "first_contentful_paint": "fcp",
        "cumulative_layout_shift": "cls",
    }

    def adapt(self, record, queried_url):
        metrics = record.get("metrics", {})
        adapted_metrics = {}

        for api_name, short_name in self.METRIC_KEYS.items():
            payload = metrics.get(api_name)
            adapted_metrics[short_name] = self._adapt_metric(short_name, payload)

        snapshot = SitePerformanceSnapshot(
            origin=queried_url,
            record_type="origin" if record.get("key", {}).get("origin") else "url",
            collection_period=record.get("collectionPeriod"),
            metrics=adapted_metrics,
        )
        return snapshot.to_dict()

    def _adapt_metric(self, metric_name, payload):
        if not payload:
            return None

        percentile = payload.get("percentiles", {}).get("p75")
        if percentile is None:
            percentile = payload.get("percentiles", {}).get("P75")

        return {
            "name": metric_name,
            "percentile": percentile,
            "unit": "unitless" if metric_name == "cls" else "ms",
            "rating": self._classify_metric(metric_name, percentile),
            "histogram": payload.get("histogram", []),
        }

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
