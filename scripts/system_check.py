import logging
import os

from api.crux_client import CrUXClient
from config.environment import load_and_validate_environment
from database.db_connection import LOG_FILE_PATH, configure_logging, get_connection
from repositories.device_repository import DeviceRepository
from repositories.telemetry_repository import TelemetryRepository
from services.report_service import ReportService
from services.telemetry_service import TelemetryService


def print_result(name, passed, message):
    status = "PASS" if passed else "FAIL"
    print(f"{status} - {name}: {message}")


def run_check(name, check_fn):
    try:
        message = check_fn()
        print_result(name, True, message)
        return True
    except Exception as exc:
        print_result(name, False, str(exc))
        return False


def check_environment_variables():
    load_and_validate_environment()
    return "DATABASE_URL and CRUX_API_KEY are loaded."


def check_database_connection():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        return "Database connection succeeded."
    finally:
        conn.close()


def table_exists(conn, table_name):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = %s
            )
            """,
            (table_name,),
        )
        return bool(cur.fetchone()[0])
    finally:
        cur.close()


def initialize_schema(conn):
    device_repository = DeviceRepository(conn)
    telemetry_repository = TelemetryRepository(conn)
    device_repository.create_table()
    telemetry_repository.create_table()


def check_devices_table():
    conn = get_connection()
    try:
        initialize_schema(conn)
        if not table_exists(conn, "devices"):
            raise RuntimeError("Devices table does not exist.")
        return "Devices table exists."
    finally:
        conn.close()


def check_telemetry_table():
    conn = get_connection()
    try:
        initialize_schema(conn)
        if not table_exists(conn, "telemetry"):
            raise RuntimeError("Telemetry table does not exist.")
        return "Telemetry table exists."
    finally:
        conn.close()


def check_crux_connectivity():
    client = CrUXClient()
    data = client.get_performance_data()
    if data.get("error"):
        raise RuntimeError(data.get("message", "CrUX returned an error payload."))

    metrics = data.get("metrics", {})
    lcp = metrics.get("lcp", {})
    ttfb = metrics.get("ttfb", {})
    return (
        "Connected to CrUX. "
        f"LCP={lcp.get('percentile')} {lcp.get('unit')}, "
        f"TTFB={ttfb.get('percentile')} {ttfb.get('unit')}."
    )


def check_logging_initialization():
    configure_logging()
    logger = logging.getLogger("sentinel.system_check")
    logger.info("System check logging validation.")

    if not logging.getLogger().handlers:
        raise RuntimeError("Logging handlers were not initialized.")
    if not os.path.exists(LOG_FILE_PATH):
        raise RuntimeError(f"Log file was not created at {LOG_FILE_PATH}.")

    return f"Logging initialized and writing to {LOG_FILE_PATH}."


def check_report_pipeline():
    conn = get_connection()
    try:
        device_repository = DeviceRepository(conn)
        telemetry_repository = TelemetryRepository(conn)
        initialize_schema(conn)
        telemetry_service = TelemetryService(telemetry_repository, device_repository)
        report_service = ReportService(telemetry_service)

        report = report_service.generate_text_report()
        if not report or "SentinelLog Report" not in report:
            raise RuntimeError("Report generation returned an unexpected result.")

        return "Report generation completed successfully."
    finally:
        conn.close()


def main():
    try:
        load_and_validate_environment()
    except RuntimeError as exc:
        print_result("Startup configuration", False, str(exc))
        print()
        print("System check completed: 0/7 checks passed.")
        raise SystemExit(1)

    checks = [
        ("Environment variables are loaded", check_environment_variables),
        ("Database connection", check_database_connection),
        ("Devices table exists", check_devices_table),
        ("Telemetry table exists", check_telemetry_table),
        ("Chrome UX Report API connectivity", check_crux_connectivity),
        ("Logging system initialization", check_logging_initialization),
        ("Report generation pipeline", check_report_pipeline),
    ]

    passed = 0
    for name, check_fn in checks:
        if run_check(name, check_fn):
            passed += 1

    total = len(checks)
    print()
    print(f"System check completed: {passed}/{total} checks passed.")


if __name__ == "__main__":
    main()
