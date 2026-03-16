# SentinelLog

CLI-based telemetry logging system demonstrating layered architecture, cloud PostgreSQL integration, and 4+1 architectural documentation.

## Updated file structure

```text
sentinellog/
├── api/
│   └── openweather_client.py
├── cli/
│   └── main.py
├── database/
│   └── db_connection.py
├── models/
│   ├── device.py
│   └── telemetry.py
├── repositories/
│   └── telemetry_repository.py
├── services/
│   ├── telemetry_service.py
│   └── weather_service.py
├── weather_test.py
├── requirements.txt
└── README.md
```

## Install

```powershell
py -m pip install -r requirements.txt
```

## Required environment variable

Set your Neon/PostgreSQL connection string:

```powershell
$env:DATABASE_URL = "your_postgresql_connection_string"
```

Optional override for the weather API key:

```powershell
$env:OPENWEATHER_API_KEY = "your_openweather_api_key"
```

## Run the full CLI app

From the project root:

```powershell
$env:PYTHONPATH="."
py cli/main.py
```

## Test the weather API only

```powershell
$env:PYTHONPATH="."
py weather_test.py
```

## What to expect

### CLI app
1. Choose `1` to log telemetry
2. Enter device id, metric type, and metric value
3. Choose `2` to view the report

The report prints:
- telemetry rows from PostgreSQL
- weather data from OpenWeatherMap

### Weather test
Prints temperature, humidity, and description for Toronto.
