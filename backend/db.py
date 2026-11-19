"""
db.py
Database connection management for SkillBridge AI.
Includes connection pooling, auto-reconnect, and auto-table initialization.
"""

import logging
import threading
import mysql.connector
from mysql.connector import Error as MySQLError
from config import Config

logger = logging.getLogger(__name__)

_conn = None


def get_db():
    """Get an active MySQL database connection with safe auto-reconnect."""
    global _conn
    need_connect = False

    if _conn is None:
        need_connect = True
    else:
        try:
            if not _conn.is_connected():
                need_connect = True
            else:
                _conn.ping(reconnect=True, attempts=1, delay=0)
        except Exception as e:
            logger.warning(f"MySQL connection check failed ({e}), reconnecting...")
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None
            need_connect = True

    if need_connect:
        try:
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
        except Exception as err:
            logger.error(f"MySQL Connection Error: {err}")
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
    def __init__(self):
        self._local = threading.local()

    def _get_cursor(self):
        active_conn = get_db()
        cursor_obj = getattr(self._local, "cursor", None)
        stored_conn = getattr(self._local, "conn", None)

        if cursor_obj is None or stored_conn is not active_conn:
            cursor_obj = active_conn.cursor(dictionary=True, buffered=True)
            self._local.cursor = cursor_obj
            self._local.conn = active_conn
        return cursor_obj

    def execute(self, operation, params=None):
        try:
            cursor_obj = self._get_cursor()
            if params is not None:
                return cursor_obj.execute(operation, params)
            return cursor_obj.execute(operation)
        except Exception as e:
            logger.warning(f"Query execution failed, reconnecting and retrying: {e}")
            active_conn = get_db()
            cursor_obj = active_conn.cursor(dictionary=True, buffered=True)
            self._local.cursor = cursor_obj
            self._local.conn = active_conn
            if params is not None:
                return cursor_obj.execute(operation, params)
            return cursor_obj.execute(operation)

    def executemany(self, operation, seq_params):
        try:
            cursor_obj = self._get_cursor()
            return cursor_obj.executemany(operation, seq_params)
        except Exception as e:
            logger.warning(f"Query executemany failed, reconnecting and retrying: {e}")
            active_conn = get_db()
            cursor_obj = active_conn.cursor(dictionary=True, buffered=True)
            self._local.cursor = cursor_obj
            self._local.conn = active_conn
            return cursor_obj.executemany(operation, seq_params)

    def fetchone(self):
        cursor_obj = self._get_cursor()
        return cursor_obj.fetchone()

    def fetchall(self):
        cursor_obj = self._get_cursor()
        return cursor_obj.fetchall()

    def fetchmany(self, size=None):
        cursor_obj = self._get_cursor()
        if size is not None:
            return cursor_obj.fetchmany(size)
        return cursor_obj.fetchmany()

    @property
    def lastrowid(self):
        cursor_obj = self._get_cursor()
        return cursor_obj.lastrowid

    @property
    def rowcount(self):
        cursor_obj = self._get_cursor()
        return cursor_obj.rowcount

    def close(self):
        cursor_obj = getattr(self._local, "cursor", None)
        if cursor_obj:
            try:
                cursor_obj.close()
            except Exception:
                pass
            self._local.cursor = None
            self._local.conn = None


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