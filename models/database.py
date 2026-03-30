"""
Database connection and base manager for SQLite operations.
Handles all database connections and table creation with thread-safe connections.
"""

import sqlite3
from pathlib import Path
import logging
from typing import Optional, List, Dict, Any
import threading
import os

from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and basic operations with thread-local storage."""
    
    _thread_local = threading.local()
    
    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Get a database connection for the current thread."""
        # Create a new connection for this thread if it doesn't exist
        if not hasattr(cls._thread_local, 'connection') or cls._thread_local.connection is None:
            cls._thread_local.connection = sqlite3.connect(str(DATABASE_PATH))
            cls._thread_local.connection.row_factory = sqlite3.Row
        return cls._thread_local.connection
    
    @classmethod
    def close_connection(cls):
        """Close the database connection for the current thread."""
        if hasattr(cls._thread_local, 'connection') and cls._thread_local.connection:
            cls._thread_local.connection.close()
            cls._thread_local.connection = None
    
    @classmethod
    def execute_query(cls, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return results."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return [dict(row) for row in cursor.fetchall()]
    
    @classmethod
    def execute_many(cls, query: str, params_list: List[tuple]) -> bool:
        """Execute multiple queries."""
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            return False
    
    @classmethod
    def execute_script(cls, script: str) -> bool:
        """Execute a SQL script."""
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return False


def init_database():
    """Initialize database tables."""
    try:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                client_data TEXT NOT NULL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Content history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_history (
                content_id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                content_data TEXT NOT NULL,
                content_type TEXT,
                platform TEXT,
                topic TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        ''')
        
        # Calendar posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_posts (
                post_id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                post_data TEXT NOT NULL,
                post_date DATE,
                month TEXT,
                year INTEGER,
                day INTEGER,
                created_at TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                platform TEXT,
                impressions INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                date DATE,
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    finally:
        pass