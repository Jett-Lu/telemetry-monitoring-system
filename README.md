# SentinelLog

CLI-based telemetry logging system demonstrating layered architecture, cloud PostgreSQL integration, and 4+1 architectural documentation.

## Overview

SentinelLog is a lightweight command-line application designed to:

- Register devices  
- Record telemetry metrics  
- Store data in a cloud-hosted PostgreSQL database  
- Retrieve telemetry history  
- Generate structured text-based reports  

This project was developed as part of **SFWRTECH 4SA3 – Software Architecture** and focuses on architectural structure rather than UI complexity.

## Architecture

SentinelLog follows a layered architecture:

- **CLI Layer** – Handles user interaction  
- **Service Layer** – Implements application logic  
- **Repository Layer** – Manages database access  
- **Cloud Database** – PostgreSQL (Neon/Supabase)  
- **External API** – OpenWeatherMap (Milestone 3)

The system is documented using the **4+1 View Model**, including:

- Scenario View  
- Physical View  
- Logical View (Milestone 3)  
- Development View (Milestone 3)  
- Process View (Milestone 3)

## Technologies

- Python 3  
- PostgreSQL (Cloud-hosted)  
- psycopg2  
- Git for version control  

## Setup Instructions

### 1. Install dependencies

```bash
pip install psycopg2-binary
```

### 2. Set database connection

Set the environment variable:

Mac/Linux:
```bash
export DATABASE_URL="your_postgresql_connection_string"
```

Windows (PowerShell):
```powershell
setx DATABASE_URL "your_postgresql_connection_string"
```

### 3. Run the application

```bash
python main.py
```

## Project Purpose

This project demonstrates:

- Cloud database integration  
- Clean separation of architectural layers  
- Traceable version control practices  
- Application of structured software architecture documentation  

## Status

Milestone 2 complete  
Milestone 3 in progress  