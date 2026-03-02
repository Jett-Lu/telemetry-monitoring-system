import os
import psycopg2


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set.")
    return psycopg2.connect(database_url)


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(50),
            metric_type VARCHAR(50),
            metric_value FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_telemetry(device_id, metric_type, metric_value):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO telemetry (device_id, metric_type, metric_value)
        VALUES (%s, %s, %s);
    """, (device_id, metric_type, metric_value))

    conn.commit()
    cur.close()
    conn.close()


def fetch_all_telemetry():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM telemetry;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows