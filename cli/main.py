from database.db_connection import configure_logging, get_connection
from cli.telemetry_cli import TelemetryCLI
from repositories.device_repository import DeviceRepository
from repositories.telemetry_repository import TelemetryRepository
from services.device_service import DeviceService
from services.report_service import ReportService
from services.telemetry_service import TelemetryService

def main():
    configure_logging()
    conn = get_connection()
    device_repository = DeviceRepository(conn)
    telemetry_repository = TelemetryRepository(conn)
    device_repository.create_table()
    telemetry_repository.create_table()

    device_service = DeviceService(device_repository)
    telemetry_service = TelemetryService(telemetry_repository, device_repository)
    report_service = ReportService(telemetry_service)
    telemetry_cli = TelemetryCLI(device_service, telemetry_service, report_service)

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
            telemetry_cli.prompt_telemetry_logging()

        elif choice == "3":
            telemetry_cli.prompt_report()

        elif choice == "4":
            print("Exiting SentinelLog.")
            conn.close()
            break

        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
