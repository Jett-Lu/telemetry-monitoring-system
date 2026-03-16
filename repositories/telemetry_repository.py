class TelemetryRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id SERIAL PRIMARY KEY,
                device_id TEXT,
                metric_type TEXT,
                metric_value FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        cur.close()

    def insert_telemetry(self, device_id, metric_type, metric_value):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO telemetry (device_id, metric_type, metric_value)
            VALUES (%s, %s, %s)
            """,
            (device_id, metric_type, metric_value),
        )
        self.conn.commit()
        cur.close()

    def get_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM telemetry ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        return rows
