from database.db_connection import get_connection
from cli.telemetry_cli import TelemetryCLI
from models.device import Device
from repositories.telemetry_repository import TelemetryRepository
from services.weather_service import WeatherService
from services.telemetry_service import TelemetryService

def main():
    conn = get_connection()
    Device.create_table(conn)
    repo = TelemetryRepository(conn)
    repo.create_table()

    weather_service = WeatherService()
    telemetry_service = TelemetryService(repo, weather_service, Device)
    telemetry_cli = TelemetryCLI(telemetry_service)

    while True:
        print("\nSentinelLog CLI")
        print("1. Register device")
        print("2. Log telemetry")
        print("3. View report")
        print("4. Exit")

        choice = input("> ").strip()

        if choice == "1":
            telemetry_cli.prompt_device_registration()

        elif choice == "2":
            device_id = input("Device ID: ").strip()
            metric_type = input("Metric type: ").strip()
            timestamp = input(
                "Timestamp (optional, ISO format like 2026-03-25 14:30:00): "
            ).strip()

            try:
                metric_value = float(input("Metric value: ").strip())
            except ValueError:
                print("Metric value must be a number.")
                continue

            try:
                telemetry_service.log_telemetry(
                    device_id,
                    metric_type,
                    metric_value,
                    timestamp=timestamp or None,
                )
            except ValueError as exc:
                print(exc)
                continue

            print("Telemetry saved.")

        elif choice == "3":
            report_device_id = input("Filter by Device ID (optional): ").strip() or None
            start_date = input(
                "Start date (optional, ISO format like 2026-03-25 00:00:00): "
            ).strip() or None
            end_date = input(
                "End date (optional, ISO format like 2026-03-25 23:59:59): "
            ).strip() or None

            try:
                report = telemetry_service.generate_report(
                    device_id=report_device_id,
                    start_date=start_date,
                    end_date=end_date,
                )
            except ValueError as exc:
                print(exc)
                continue

            print("\nTelemetry Records:")
            for row in report["telemetry"]:
                print(row)

            print("\nWeather Context:")
            print(report["weather"])

        elif choice == "4":
            print("Exiting SentinelLog.")
            conn.close()
            break

        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
