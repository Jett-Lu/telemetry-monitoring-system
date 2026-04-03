# SentinelLog

SentinelLog is a CLI-based telemetry logging and reporting system for SFWRTECH 4SA3. It uses PostgreSQL for persistence, Chrome UX Report (CrUX) for public web performance metrics, and UptimeRobot for public uptime status for `https://www.mcmaster.ca/`.

## Final project scope

SentinelLog supports:
- device registration with `device_id`, `name`, `type`, and `location`
- telemetry logging with `device_id`, `metric_type`, `metric_value`, and `timestamp`
- PostgreSQL storage for device and telemetry records
- telemetry history retrieval filtered by `device_id` and optional date range
- text-based report generation
- CrUX performance enrichment for the tracked origin
- UptimeRobot uptime enrichment for the tracked origin
- a clear-all-data reset option for demos and testing

## Architecture

The project follows a layered structure:

```text
sentinel-log/
|-- api/
|   |-- crux_adapter.py
|   |-- crux_client.py
|   |-- uptime_adapter.py
|   `-- uptime_client.py
|-- cli/
|   |-- main.py
|   `-- telemetry_cli.py
|-- config/
|   `-- environment.py
|-- database/
|   `-- db_connection.py
|-- models/
|   |-- device.py
|   |-- device_factory.py
|   |-- site_performance.py
|   |-- telemetry.py
|   `-- uptime_status.py
|-- repositories/
|   |-- device_repository.py
|   `-- telemetry_repository.py
|-- scripts/
|   `-- system_check.py
|-- services/
|   |-- database_reset_service.py
|   |-- device_service.py
|   |-- report_service.py
|   |-- report_strategies.py
|   |-- telemetry_service.py
|   `-- uptime_service.py
|-- tests/
|   |-- test_reset_service.py
|   |-- test_services.py
|   `-- test_uptime_service.py
|-- .env.example
|-- requirements.txt
`-- README.md
```

## Design patterns used

- Factory Method:
  `models/device_factory.py` creates `Device` objects for the service layer.
- Strategy:
  `services/report_strategies.py` defines report formatting behavior, with `PlainTextReportStrategy` used by default.
- Adapter:
  `api/crux_adapter.py` converts raw CrUX API responses into the internal site performance model used by reporting.
  `api/uptime_adapter.py` converts raw UptimeRobot monitor responses into the internal uptime model.

## Requirements

- Python 3.11+ recommended
- PostgreSQL database reachable through a cloud connection string

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=your_postgresql_connection_string
CRUX_API_KEY=your_google_crux_api_key
UPTIMEROBOT_API_KEY=your_uptimerobot_api_key
TRACKED_ORIGIN=https://www.mcmaster.ca/
```

Required variables:
- `DATABASE_URL`
- `CRUX_API_KEY`
- `UPTIMEROBOT_API_KEY`

Optional variable:
- `TRACKED_ORIGIN`
  Default: `https://www.mcmaster.ca/`

If a required variable is missing, SentinelLog prints a clear startup configuration error and exits immediately.

You can start from `.env.example` and fill in the real values.

## Running the application

From the project root:

```powershell
$env:PYTHONPATH="."
python -m cli.main
```

## CLI options

The final CLI supports:

1. Register device
2. List devices
3. Log telemetry
4. Retrieve telemetry history
5. Generate report
6. Exit
7. Clear all data

## Example flow

1. Register a device with `device_id`, `name`, `type`, and `location`
2. Log telemetry for that registered device
3. Retrieve telemetry history using:
   - no filters
   - a `device_id`
   - a `device_id` plus optional ISO-format start and end dates
4. Generate a report that summarizes telemetry and adds CrUX and UptimeRobot data for the tracked origin
5. Use clear-all-data when you want to reset the demo dataset without dropping tables

## Report output

The report is plain text and includes:
- telemetry summary by `device_id` and `metric_type`
- average, minimum, maximum, and sample count
- CrUX performance data for the tracked origin:
  - LCP
  - TTFB
  - FCP
  - CLS
- UptimeRobot uptime data for the tracked origin:
  - Status
  - Uptime percentage
  - Response time

## Logging

Database operations and failures are logged with timestamps to:

```text
sentinel.log
```

Logged events include:
- device inserts, updates, and deletes
- telemetry inserts
- clear-all-data reset operations with deleted record counts
- repository/database failures
- connection failures

## Validation script

Run the system validation script before submission:

```powershell
$env:PYTHONPATH="."
python scripts/system_check.py
```

The script checks:
- environment variables
- database connection
- `devices` table existence
- `telemetry` table existence
- CrUX API connectivity
- UptimeRobot API connectivity
- logging initialization
- report generation pipeline

It prints `PASS` or `FAIL` for each check and ends with a summary count.

## Unit tests

Run the tests:

```powershell
$env:PYTHONPATH="."
python -m unittest tests.test_services
python -m unittest tests.test_uptime_service
python -m unittest tests.test_reset_service
```

These tests cover:
- device registration
- duplicate device rejection
- telemetry logging for registered devices
- telemetry history filtering
- text report generation with CrUX and UptimeRobot output
- uptime adapter/service parsing
- clear-all-data reset behavior and confirmation logic

## Notes for submission

- SentinelLog uses CrUX and UptimeRobot as the final external integrations.
- Older weather-based integration code has been removed to keep the final prototype coherent.
- The repository is structured so CLI, service logic, persistence, configuration, models, and external integrations are clearly separated.
