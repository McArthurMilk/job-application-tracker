"""Database helper functions for the Job Application Tracker."""
import os
import mysql.connector

# Change these to match your MySQL setup (or set them as environment variables).
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "YOUR_PASSWORD"),
    "database": os.environ.get("DB_NAME", "job_tracker"),
}


def get_db():
    """Open a new connection to the job_tracker database."""
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=None, one=False):
    """Run a SELECT and return the rows as dictionaries (or a single row if one=True)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=None):
    """Run an INSERT, UPDATE or DELETE and save the change."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    cursor.close()
    conn.close()
