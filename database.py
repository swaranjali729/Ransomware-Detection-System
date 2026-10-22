
import sqlite3

DB_NAME = "scan_history.db"


def initialize_database():
    connection = sqlite3.connect(DB_NAME)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_time TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            result TEXT NOT NULL,
            indicators TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_scan(scan_time, filename, file_size, sha256, result, indicators):
    connection = sqlite3.connect(DB_NAME)

    connection.execute("""
        INSERT INTO scans
        (scan_time, filename, file_size, sha256, result, indicators)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        scan_time,
        filename,
        file_size,
        sha256,
        result,
        indicators
    ))

    connection.commit()
    connection.close()


def get_scans():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT * FROM scans ORDER BY id DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]
