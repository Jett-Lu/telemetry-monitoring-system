# SentinelLog

SentinelLog is a CLI-based telemetry logging and reporting system for SFWRTECH 4SA3. It demonstrates a layered software architecture with PostgreSQL persistence, timestamped database logging, filtered telemetry retrieval, and external website performance enrichment using the Chrome UX Report (CrUX) API for `https://www.mcmaster.ca/`.

## Final Milestone 4 scope

SentinelLog supports:
- device registration with `device_id`, `name`, `type`, and `location`
- telemetry logging with `device_id`, `metric_type`, `metric_value`, and `timestamp`
- PostgreSQL storage for devices and telemetry records
- telemetry history retrieval filtered by `device_id` and optional date range
- text-based summary report generation
- external performance enrichment from CrUX for the tracked McMaster origin

## Architecture

The project uses a layered structure:

```text
sentinel-log/
|-- api/
|   |-- crux_adapter.py
|   `-- crux_client.py
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
|   `-- telemetry.py
|-- repositories/
|   |-- device_repository.py
|   `-- telemetry_repository.py
|-- scripts/
|   `-- system_check.py
|-- services/
|   |-- device_service.py
|   |-- report_service.py
|   |-- report_strategies.py
|   `-- telemetry_service.py
|-- tests/
|   `-- test_services.py
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
TRACKED_ORIGIN=https://www.mcmaster.ca/
```

Required variables:
- `DATABASE_URL`
- `CRUX_API_KEY`

Optional variable:
- `TRACKED_ORIGIN`
  Default: `https://www.mcmaster.ca/`

If a required variable is missing, SentinelLog prints a clear startup configuration error and exits immediately.

You can start from `.env.example` and fill in the real values.

## Running the application

From the project root:

```powershell
$env:PYTHONPATH="."
python cli/main.py
```

## CLI options

The final CLI supports:

1. Register device
2. List devices
3. Log telemetry
4. Retrieve telemetry history
5. Generate report
6. Exit

## Example flow

1. Register a device with `device_id`, `name`, `type`, and `location`
2. Log telemetry for that registered device
3. Retrieve telemetry history using:
   - no filters
   - a `device_id`
   - a `device_id` plus optional ISO-format start and end dates
4. Generate a report that summarizes telemetry and adds CrUX performance data for the tracked origin

## Report output

The report is plain text and includes:
- telemetry summary by `device_id` and `metric_type`
- average, minimum, maximum, and sample count
- CrUX performance data for the tracked origin:
  - LCP
  - TTFB
  - FCP
  - CLS

## Logging

Database operations and failures are logged with timestamps to:

```text
sentinel.log
```

Logged events include:
- device inserts, updates, and deletes
- telemetry inserts
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
- logging initialization
- report generation pipeline

It prints `PASS` or `FAIL` for each check and ends with a summary count.

## Unit tests

Run the lightweight service-level tests:

```powershell
$env:PYTHONPATH="."
python -m unittest tests.test_services
```

These tests cover:
- device registration
- duplicate device rejection
- telemetry logging for registered devices
- telemetry history filtering
- text report generation with CrUX-formatted output

## Notes for submission

- SentinelLog uses one final external integration path: CrUX.
- Older weather-based and duplicate external integration code has been removed to keep the final prototype coherent.
- The repository is structured so CLI, service logic, persistence, configuration, models, and external integrations are clearly separated.
