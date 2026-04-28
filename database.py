"""
database.py
-----------
Handles MySQL database connectivity for the maacess-ai-service.
Reads connection parameters from environment variables (via .env).
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_connection():
    """
    Create and return a MySQL database connection using environment variables.

    Returns:
        mysql.connector.connection.MySQLConnection: An active DB connection.

    Raises:
        RuntimeError: If the connection cannot be established.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"[DB] Connected to MySQL Server version: {db_info}")
            print(f"[DB] Database: '{os.getenv('DB_DATABASE')}'")
            return connection

    except Error as e:
        raise RuntimeError(f"[DB] Failed to connect to MySQL: {e}") from e


def close_connection(connection):
    """
    Safely close a MySQL database connection.

    Args:
        connection: The active MySQL connection object.
    """
    if connection and connection.is_connected():
        connection.close()
        print("[DB] Connection closed.")
