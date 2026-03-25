class SitePerformanceSnapshot:
    def __init__(self, origin, record_type, collection_period, metrics):
        self.origin = origin
        self.record_type = record_type
        self.collection_period = collection_period
        self.metrics = metrics

    def to_dict(self):
        return {
            "origin": self.origin,
            "record_type": self.record_type,
            "collection_period": self.collection_period,
            "metrics": self.metrics,
        }
