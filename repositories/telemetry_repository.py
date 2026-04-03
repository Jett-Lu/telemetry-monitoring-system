import logging

from models.telemetry import Telemetry


logger = logging.getLogger(__name__)


class TelemetryRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self):
        cur = self.conn.cursor()
        try:
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
                    INSERT INTO devices (device_id, name, type, location)
                    SELECT DISTINCT t.device_id, t.device_id, 'legacy-device', 'unknown'
                    FROM telemetry t
                    LEFT JOIN devices d ON d.device_id = t.device_id
                    WHERE d.device_id IS NULL;

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
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_telemetry_device_id_timestamp
                ON telemetry (device_id, timestamp)
                """
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            logger.exception("Failed to create or update telemetry table.")
            raise
        finally:
            cur.close()

    def insert_telemetry(self, device_id, metric_type, metric_value, timestamp=None):
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO telemetry (device_id, metric_type, metric_value, timestamp)
                VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
                """,
                (device_id, metric_type, metric_value, timestamp),
            )
            self.conn.commit()
            logger.info(
                "Inserted telemetry device_id=%s metric_type=%s metric_value=%s timestamp=%s",
                device_id,
                metric_type,
                metric_value,
                timestamp or "CURRENT_TIMESTAMP",
            )
        except Exception:
            self.conn.rollback()
            logger.exception(
                "Failed to insert telemetry device_id=%s metric_type=%s",
                device_id,
                metric_type,
            )
            raise
        finally:
            cur.close()

    def get_history(self, device_id=None, start_date=None, end_date=None):
        cur = self.conn.cursor()
        query = """
            SELECT device_id, metric_type, metric_value, timestamp
            FROM telemetry
            WHERE (%s IS NULL OR device_id = %s)
              AND (%s IS NULL OR timestamp >= %s)
              AND (%s IS NULL OR timestamp <= %s)
            ORDER BY timestamp, device_id
        """
        try:
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
        except Exception:
            logger.exception(
                "Failed to fetch telemetry device_id=%s start_date=%s end_date=%s",
                device_id,
                start_date,
                end_date,
            )
            raise
        finally:
            cur.close()
        return [Telemetry.from_row(row).to_dict() for row in rows]

    def get_all(self, device_id=None, start_date=None, end_date=None):
        return self.get_history(
            device_id=device_id,
            start_date=start_date,
            end_date=end_date,
        )

    def delete_all(self):
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM telemetry")
            deleted = cur.rowcount
            self.conn.commit()
            logger.info("Deleted all telemetry records count=%s", deleted)
            return deleted
        except Exception:
            self.conn.rollback()
            logger.exception("Failed to delete all telemetry records.")
            raise
        finally:
            cur.close()
