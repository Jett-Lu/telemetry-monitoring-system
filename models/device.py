import logging


logger = logging.getLogger(__name__)


class Device:
    def __init__(self, device_id, name, device_type, location):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.location = location

    @classmethod
    def create_table(cls, conn):
        cur = conn.cursor()
        try:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    id SERIAL PRIMARY KEY,
                    device_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    location TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_devices_device_id
                ON devices (device_id)
                """
            )
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Failed to create or update devices table.")
            raise
        finally:
            cur.close()

    def create(self, conn):
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO devices (device_id, name, type, location)
                VALUES (%s, %s, %s, %s)
                """,
                (self.device_id, self.name, self.device_type, self.location),
            )
            conn.commit()
            logger.info(
                "Inserted device device_id=%s name=%s type=%s location=%s",
                self.device_id,
                self.name,
                self.device_type,
                self.location,
            )
        except Exception:
            conn.rollback()
            logger.exception("Failed to insert device device_id=%s", self.device_id)
            raise
        finally:
            cur.close()
        return self

    def update(self, conn):
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE devices
                SET name = %s, type = %s, location = %s
                WHERE device_id = %s
                """,
                (self.name, self.device_type, self.location, self.device_id),
            )
            updated = cur.rowcount
            conn.commit()
            if updated:
                logger.info("Updated device device_id=%s", self.device_id)
            return updated > 0
        except Exception:
            conn.rollback()
            logger.exception("Failed to update device device_id=%s", self.device_id)
            raise
        finally:
            cur.close()

    @classmethod
    def get_by_device_id(cls, conn, device_id):
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT device_id, name, type, location
                FROM devices
                WHERE device_id = %s
                """,
                (device_id,),
            )
            row = cur.fetchone()
        except Exception:
            logger.exception("Failed to fetch device device_id=%s", device_id)
            raise
        finally:
            cur.close()

        if not row:
            return None

        return cls(
            device_id=row[0],
            name=row[1],
            device_type=row[2],
            location=row[3],
        )

    @classmethod
    def get_all(cls, conn):
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT device_id, name, type, location
                FROM devices
                ORDER BY device_id
                """
            )
            rows = cur.fetchall()
        except Exception:
            logger.exception("Failed to fetch devices.")
            raise
        finally:
            cur.close()
        return [
            cls(
                device_id=row[0],
                name=row[1],
                device_type=row[2],
                location=row[3],
            )
            for row in rows
        ]

    @classmethod
    def delete(cls, conn, device_id):
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM devices WHERE device_id = %s", (device_id,))
            deleted = cur.rowcount
            conn.commit()
            if deleted:
                logger.info("Deleted device device_id=%s", device_id)
            return deleted > 0
        except Exception:
            conn.rollback()
            logger.exception("Failed to delete device device_id=%s", device_id)
            raise
        finally:
            cur.close()
