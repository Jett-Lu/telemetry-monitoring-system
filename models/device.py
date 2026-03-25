class Device:
    def __init__(self, device_id, name, device_type, location):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.location = location

    @classmethod
    def create_table(cls, conn):
        cur = conn.cursor()
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
        cur.close()

    def create(self, conn):
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO devices (device_id, name, type, location)
            VALUES (%s, %s, %s, %s)
            """,
            (self.device_id, self.name, self.device_type, self.location),
        )
        conn.commit()
        cur.close()
        return self

    def update(self, conn):
        cur = conn.cursor()
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
        cur.close()
        return updated > 0

    @classmethod
    def get_by_device_id(cls, conn, device_id):
        cur = conn.cursor()
        cur.execute(
            """
            SELECT device_id, name, type, location
            FROM devices
            WHERE device_id = %s
            """,
            (device_id,),
        )
        row = cur.fetchone()
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
        cur.execute(
            """
            SELECT device_id, name, type, location
            FROM devices
            ORDER BY device_id
            """
        )
        rows = cur.fetchall()
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
        cur.execute("DELETE FROM devices WHERE device_id = %s", (device_id,))
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        return deleted > 0
