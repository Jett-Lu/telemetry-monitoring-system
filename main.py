from db import initialize_database, insert_telemetry, fetch_all_telemetry


def main():
    print("Initializing database...")
    initialize_database()

    print("Inserting sample telemetry record...")
    insert_telemetry("device001", "cpu_usage", 42.5)

    print("Fetching telemetry records...")
    records = fetch_all_telemetry()

    for record in records:
        print(record)


if __name__ == "__main__":
    main()