from database.db_connection import get_connection
from repositories.telemetry_repository import TelemetryRepository
from services.weather_service import WeatherService
from services.telemetry_service import TelemetryService

def main():
    conn = get_connection()
    repo = TelemetryRepository(conn)
    repo.create_table()

    weather_service = WeatherService()
    telemetry_service = TelemetryService(repo, weather_service)

    while True:
        print("\nSentinelLog CLI")
        print("1. Log telemetry")
        print("2. View report")
        print("3. Exit")

        choice = input("> ").strip()

        if choice == "1":
            device_id = input("Device ID: ").strip()
            metric_type = input("Metric type: ").strip()

            try:
                metric_value = float(input("Metric value: ").strip())
            except ValueError:
                print("Metric value must be a number.")
                continue

            telemetry_service.log_telemetry(device_id, metric_type, metric_value)
            print("Telemetry saved.")

        elif choice == "2":
            report = telemetry_service.generate_report()
            print("\nTelemetry Records:")
            for row in report["telemetry"]:
                print(row)

            print("\nWeather Context:")
            print(report["weather"])

        elif choice == "3":
            print("Exiting SentinelLog.")
            conn.close()
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
