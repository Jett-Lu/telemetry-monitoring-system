from database.db_connection import configure_logging, get_connection
from cli.telemetry_cli import TelemetryCLI
from config.environment import load_and_validate_environment
from repositories.device_repository import DeviceRepository
from repositories.telemetry_repository import TelemetryRepository
from services.database_reset_service import DatabaseResetService
from services.device_service import DeviceService
from services.report_service import ReportService
from services.telemetry_service import TelemetryService

def main():
    try:
        load_and_validate_environment()
    except RuntimeError as exc:
        print(f"Startup configuration error: {exc}")
        raise SystemExit(1)

    configure_logging()
    try:
        conn = get_connection()
        device_repository = DeviceRepository(conn)
        telemetry_repository = TelemetryRepository(conn)
        device_repository.create_table()
        telemetry_repository.create_table()
    except Exception as exc:
        print(f"Startup initialization error: {exc}")
        raise SystemExit(1)

    device_service = DeviceService(device_repository)
    telemetry_service = TelemetryService(telemetry_repository, device_repository)
    report_service = ReportService(telemetry_service)
    database_reset_service = DatabaseResetService(
        device_repository,
        telemetry_repository,
    )
    telemetry_cli = TelemetryCLI(
        device_service,
        telemetry_service,
        report_service,
        database_reset_service,
    )

    while True:
        print("\nSentinelLog CLI")
        print("1. Register device")
        print("2. List devices")
        print("3. Log telemetry")
        print("4. Retrieve telemetry history")
        print("5. Generate report")
        print("6. Exit")
        print("7. Clear all data")

        choice = input("> ").strip()

        if choice == "1":
            telemetry_cli.prompt_device_registration()

        elif choice == "2":
            telemetry_cli.list_devices()

        elif choice == "3":
            telemetry_cli.prompt_telemetry_logging()

        elif choice == "4":
            telemetry_cli.prompt_telemetry_history()

        elif choice == "5":
            telemetry_cli.prompt_report()

        elif choice == "6":
            print("Exiting SentinelLog.")
            conn.close()
            break

        elif choice == "7":
            telemetry_cli.prompt_clear_all_data()

        else:
            print("Invalid option. Please choose 1, 2, 3, 4, 5, 6, or 7.")

if __name__ == "__main__":
    main()
