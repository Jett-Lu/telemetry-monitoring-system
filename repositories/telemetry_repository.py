from models.telemetry import Telemetry


class TelemetryRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry (
                id SERIAL PRIMARY KEY,
                device_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value FLOAT NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_telemetry_device
                    FOREIGN KEY (device_id) REFERENCES devices (device_id)
            )
            """
        )
        cur.execute(
            """
            ALTER TABLE telemetry
            ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            """
        )
        cur.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'telemetry'
                      AND column_name = 'created_at'
                ) THEN
                    UPDATE telemetry
                    SET timestamp = created_at
                    WHERE timestamp IS NULL;
                END IF;
            END $$;
            """
        )
        cur.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'fk_telemetry_device'
                ) THEN
                    ALTER TABLE telemetry
                    ADD CONSTRAINT fk_telemetry_device
                    FOREIGN KEY (device_id) REFERENCES devices (device_id);
                END IF;
            END $$;
            """
        )
        self.conn.commit()
        cur.close()

    def insert_telemetry(self, device_id, metric_type, metric_value, timestamp=None):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO telemetry (device_id, metric_type, metric_value, timestamp)
            VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
            """,
            (device_id, metric_type, metric_value, timestamp),
        )
        self.conn.commit()
        cur.close()

    def get_all(self, device_id=None, start_date=None, end_date=None):
        cur = self.conn.cursor()
        query = """
            SELECT device_id, metric_type, metric_value, timestamp
            FROM telemetry
            WHERE (%s IS NULL OR device_id = %s)
              AND (%s IS NULL OR timestamp >= %s)
              AND (%s IS NULL OR timestamp <= %s)
            ORDER BY timestamp, device_id
        """
        cur.execute(
            query,
            (
                device_id,
                device_id,
                start_date,
                start_date,
                end_date,
                end_date,
            ),
        )
        rows = cur.fetchall()
        cur.close()
        return [Telemetry.from_row(row).to_dict() for row in rows]
