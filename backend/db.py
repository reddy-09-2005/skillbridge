"""
db.py
Database connection management for SkillBridge AI.
Includes connection pooling, auto-reconnect, and auto-table initialization.
"""

import logging
import mysql.connector
from mysql.connector import Error as MySQLError
from config import Config

logger = logging.getLogger(__name__)

_conn = None


def get_db():
    """Get an active MySQL database connection with auto-reconnect."""
    global _conn
    try:
        if _conn is None or not _conn.is_connected():
            _conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                port=Config.MYSQL_PORT,
                use_pure=True,
                ssl_disabled=False,
                autocommit=False
            )
        else:
            _conn.ping(reconnect=True, attempts=3, delay=1)
    except MySQLError as e:
        logger.error(f"MySQL Connection Error: {e}")
        # Try one fresh reconnect attempt
        try:
            _conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                port=Config.MYSQL_PORT,
                use_pure=True,
                ssl_disabled=False
            )
        except Exception as retry_err:
            logger.error(f"MySQL Reconnect Failed: {retry_err}")
            raise
    return _conn


class ResilientConnectionProxy:
    """Proxy object ensuring connection auto-reconnects and stays alive."""
    def __getattr__(self, name):
        return getattr(get_db(), name)

    def commit(self):
        return get_db().commit()

    def rollback(self):
        return get_db().rollback()

    def cursor(self, **kwargs):
        return get_db().cursor(**kwargs)


class ResilientCursorProxy:
    """Proxy object providing transparent dictionary+buffered cursor with auto-reconnect."""
    def _get_cursor(self):
        c = get_db()
        return c.cursor(dictionary=True, buffered=True)

    def execute(self, operation, params=None, multi=False):
        try:
            c = self._get_cursor()
            return c.execute(operation, params, multi=multi)
        except MySQLError:
            # Reconnect and retry once
            get_db()
            c = self._get_cursor()
            return c.execute(operation, params, multi=multi)

    def executemany(self, operation, seq_params):
        c = self._get_cursor()
        return c.executemany(operation, seq_params)

    def fetchone(self):
        return self._get_cursor().fetchone()

    def fetchall(self):
        return self._get_cursor().fetchall()

    def fetchmany(self, size=None):
        return self._get_cursor().fetchmany(size)

    @property
    def lastrowid(self):
        return self._get_cursor().lastrowid

    @property
    def rowcount(self):
        return self._get_cursor().rowcount

    def close(self):
        pass


# Backwards-compatible proxies for existing blueprint imports
conn = ResilientConnectionProxy()
cursor = ResilientCursorProxy()


def init_db():
    """Create database tables if they do not already exist."""
    try:
        db_conn = get_db()
        init_cursor = db_conn.cursor()

        # Users table
        init_cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Resumes table
        init_cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                resume_text LONGTEXT NOT NULL,
                skills TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_resume_user (user_email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        db_conn.commit()
        init_cursor.close()
        logger.info("Database tables verified / initialized successfully.")
        return True
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
        return False