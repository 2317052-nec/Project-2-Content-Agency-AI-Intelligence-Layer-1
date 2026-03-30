"""
Client model for managing client profiles and data.
"""

import uuid
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

from .database import DatabaseManager


class ClientModel:
    """Handles client-related database operations."""
    
    @staticmethod
    def generate_client_id(company_name: str) -> str:
        """Generate a unique client ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name_hash = hashlib.md5(company_name.encode()).hexdigest()[:6]
        return f"CLIENT_{name_hash}_{timestamp}"
    
    @staticmethod
    def save_client(user_id: str, client_data: Dict) -> bool:
        """Save a client to the database."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            client_id = client_data.get('client_id')
            client_json = json.dumps(client_data)
            now = datetime.now()
            
            cursor.execute(
                "INSERT INTO clients (client_id, user_id, client_data, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (client_id, user_id, client_json, now, now)
            )
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving client: {e}")
            return False
    
    @staticmethod
    def get_clients(user_id: str) -> List[Dict]:
        """Get all clients for a user."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT client_data FROM clients WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            
            return [json.loads(row[0]) for row in rows]
            
        except Exception as e:
            print(f"Error getting clients: {e}")
            return []
    
    @staticmethod
    def get_client_by_id(client_id: str) -> Optional[Dict]:
        """Get a specific client by ID."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT client_data FROM clients WHERE client_id = ?",
                (client_id,)
            )
            row = cursor.fetchone()
            
            return json.loads(row[0]) if row else None
            
        except Exception as e:
            print(f"Error getting client: {e}")
            return None
    
    @staticmethod
    def update_client(client_id: str, client_data: Dict) -> bool:
        """Update an existing client."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            client_json = json.dumps(client_data)
            now = datetime.now()
            
            cursor.execute(
                "UPDATE clients SET client_data = ?, updated_at = ? WHERE client_id = ?",
                (client_json, now, client_id)
            )
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating client: {e}")
            return False
    
    @staticmethod
    def delete_client(client_id: str) -> bool:
        """Delete a client and all related data."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
            cursor.execute("DELETE FROM content_history WHERE client_id = ?", (client_id,))
            cursor.execute("DELETE FROM calendar_posts WHERE client_id = ?", (client_id,))
            cursor.execute("DELETE FROM performance_metrics WHERE client_id = ?", (client_id,))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting client: {e}")
            return False