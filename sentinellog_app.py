
import psycopg2
import requests
import os

DATABASE_URL = os.getenv("DATABASE_URL")
WEATHER_API_KEY = "5747e1b6e4add1a3316b577fca2b7d88"

def get_connection():
    return psycopg2.connect(DATABASE_URL)

class TelemetryRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetry(
            id SERIAL PRIMARY KEY,
            device_id TEXT,
            metric_type TEXT,
            metric_value FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def insert_telemetry(self, device_id, metric_type, metric_value):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO telemetry(device_id,metric_type,metric_value) VALUES(%s,%s,%s)",
            (device_id, metric_type, metric_value)
        )
        self.conn.commit()

    def get_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM telemetry")
        return cur.fetchall()

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city="Toronto"):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"]
            }
        return None

class TelemetryService:
    def __init__(self, repository, weather_service):
        self.repository = repository
        self.weather_service = weather_service

    def log_telemetry(self, device_id, metric_type, metric_value):
        self.repository.insert_telemetry(device_id, metric_type, metric_value)

    def generate_report(self):
        telemetry = self.repository.get_all()
        weather = self.weather_service.get_weather()
        return {"telemetry": telemetry, "weather": weather}

def run_cli(service):
    while True:
        print("\nSentinelLog CLI")
        print("1. Log telemetry")
        print("2. View report")
        print("3. Exit")
        choice = input("> ")
        if choice == "1":
            device = input("Device ID: ")
            metric = input("Metric type: ")
            value = float(input("Metric value: "))
            service.log_telemetry(device, metric, value)
            print("Telemetry saved.")
        elif choice == "2":
            report = service.generate_report()
            print("\nTelemetry Records:")
            for row in report["telemetry"]:
                print(row)
            print("\nWeather Context:")
            print(report["weather"])
        elif choice == "3":
            break
        else:
            print("Invalid option")

def main():
    conn = get_connection()
    repo = TelemetryRepository(conn)
    repo.create_table()
    weather = WeatherService(WEATHER_API_KEY)
    service = TelemetryService(repo, weather)
    run_cli(service)

if __name__ == "__main__":
    main()
