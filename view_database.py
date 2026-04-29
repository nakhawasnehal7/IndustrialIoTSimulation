import sqlite3
import pandas as pd
import os

DB_PATH = 'data/iot_maintenance.db'


def view_database():
    """Interactive database viewer"""

    # Check if database exists
    if not os.path.exists(DB_PATH):

        return

    conn = sqlite3.connect(DB_PATH)

    while True:
        print("\n" + "=" * 60)
        print("SQLite DATABASE VIEWER")
        print("=" * 60)

        # Show available tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print("\nAvailable tables:")
        for idx, table in enumerate(tables, 1):
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"{idx}. {table[0]} ({count} rows)")

        print(f"{len(tables) + 1}. Exit")

        # Get user choice
        try:
            choice = int(input("\nSelect table number: "))

            if choice == len(tables) + 1:
                print("Goodbye!")
                break

            if choice < 1 or choice > len(tables):
                print("Invalid choice!")
                continue

            table_name = tables[choice - 1][0]

            # Ask how many rows to view
            limit = input(f"\nHow many rows to view? (default: 10, 'all' for all): ").strip()

            if limit.lower() == 'all':
                query = f"SELECT * FROM {table_name}"
            else:
                limit = int(limit) if limit else 10
                query = f"SELECT * FROM {table_name} LIMIT {limit}"

            # Fetch and display
            df = pd.read_sql_query(query, conn)

            print("\n" + "=" * 60)
            print(f"TABLE: {table_name}")
            print("=" * 60)
            print(df.to_string(index=False))

            # Show statistics for numeric columns
            print("\n" + "=" * 60)
            print("STATISTICS")
            print("=" * 60)
            print(df.describe())

            # Ask if user wants to export
            export = input("\nExport to CSV? (y/n): ").strip().lower()
            if export == 'y':
                filename = f"{table_name}_export.csv"
                df.to_csv(filename, index=False)


        except ValueError:
            print("Invalid input!")
        except Exception as e:
            print(f"Error: {e}")

    conn.close()


if __name__ == "__main__":
    view_database()