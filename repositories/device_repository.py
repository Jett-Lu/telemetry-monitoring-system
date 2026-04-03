import logging

from models.device import Device


logger = logging.getLogger(__name__)


class DeviceRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self):
        cur = self.conn.cursor()
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
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            logger.exception("Failed to create or update devices table.")
            raise
        finally:
            cur.close()

    def insert(self, device):
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO devices (device_id, name, type, location)
                VALUES (%s, %s, %s, %s)
                """,
                (device.device_id, device.name, device.device_type, device.location),
            )
            self.conn.commit()
            logger.info(
                "Inserted device device_id=%s name=%s type=%s location=%s",
                device.device_id,
                device.name,
                device.device_type,
                device.location,
            )
            return device
        except Exception:
            self.conn.rollback()
            logger.exception("Failed to insert device device_id=%s", device.device_id)
            raise
        finally:
            cur.close()

    def update(self, device):
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE devices
                SET name = %s, type = %s, location = %s
                WHERE device_id = %s
                """,
                (device.name, device.device_type, device.location, device.device_id),
            )
            updated = cur.rowcount
            self.conn.commit()
            if updated:
                logger.info("Updated device device_id=%s", device.device_id)
            return updated > 0
        except Exception:
            self.conn.rollback()
            logger.exception("Failed to update device device_id=%s", device.device_id)
            raise
        finally:
            cur.close()

    def get_by_device_id(self, device_id):
        cur = self.conn.cursor()
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

        return Device.from_row(row)

    def get_all(self):
        cur = self.conn.cursor()
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

        return [Device.from_row(row) for row in rows]

    def delete(self, device_id):
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM devices WHERE device_id = %s", (device_id,))
            deleted = cur.rowcount
            self.conn.commit()
            if deleted:
                logger.info("Deleted device device_id=%s", device_id)
            return deleted > 0
        except Exception:
            self.conn.rollback()
            logger.exception("Failed to delete device device_id=%s", device_id)
            raise
        finally:
            cur.close()

    def delete_all(self):
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM devices")
            deleted = cur.rowcount
            self.conn.commit()
            logger.info("Deleted all devices count=%s", deleted)
            return deleted
        except Exception:
            self.conn.rollback()
            logger.exception("Failed to delete all devices.")
            raise
        finally:
            cur.close()
