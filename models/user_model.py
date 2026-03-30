"""
User model for handling authentication and user data.
"""

import uuid
import hashlib
import sqlite3
from datetime import datetime
from typing import Optional, Dict

from .database import DatabaseManager


class UserModel:
    """Handles user-related database operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_user(username: str, password: str, email: str) -> Optional[str]:
        """Create a new user."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            user_id = str(uuid.uuid4())
            password_hash = UserModel.hash_password(password)
            now = datetime.now()
            
            cursor.execute(
                "INSERT INTO users (user_id, username, password_hash, email, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, password_hash, email, now, now)
            )
            conn.commit()
            return user_id
            
        except sqlite3.IntegrityError:
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def get_user(username: str) -> Optional[Dict]:
        """Get user by username."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials."""
        user = UserModel.get_user(username)
        if user and user['password_hash'] == UserModel.hash_password(password):
            return user
        return None
    
    @staticmethod
    def update_last_login(user_id: str):
        """Update user's last login timestamp."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE user_id = ?",
                (datetime.now(), user_id)
            )
            conn.commit()
        except Exception as e:
            print(f"Error updating last login: {e}")