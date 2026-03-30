"""
Content model for managing generated content and history.
"""

import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from .database import DatabaseManager


class ContentModel:
    """Handles content-related database operations."""
    
    @staticmethod
    def save_content(
        client_id: str,
        content_data: Dict,
        content_type: str,
        platform: str,
        topic: str
    ) -> bool:
        """Save generated content to history."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            content_id = str(uuid.uuid4())
            content_json = json.dumps(content_data)
            now = datetime.now()
            
            cursor.execute(
                "INSERT INTO content_history VALUES (?, ?, ?, ?, ?, ?, ?)",
                (content_id, client_id, content_json, content_type, platform, topic, now)
            )
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving content: {e}")
            return False
    
    @staticmethod
    def get_content_history(client_id: str, limit: int = 50) -> List[Dict]:
        """Get content history for a client."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT content_data, content_type, platform, topic, created_at 
                   FROM content_history 
                   WHERE client_id = ? 
                   ORDER BY created_at DESC 
                   LIMIT ?""",
                (client_id, limit)
            )
            rows = cursor.fetchall()
            
            return [
                {
                    "data": json.loads(row[0]),
                    "type": row[1],
                    "platform": row[2],
                    "topic": row[3],
                    "created_at": row[4]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting content history: {e}")
            return []
    
    @staticmethod
    def save_calendar_post(
        client_id: str,
        post_data: Dict,
        post_date: str,
        month: str,
        year: int,
        day: int
    ) -> bool:
        """Save a calendar post."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            post_id = str(uuid.uuid4())
            post_json = json.dumps(post_data)
            now = datetime.now()
            
            cursor.execute(
                "INSERT INTO calendar_posts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (post_id, client_id, post_json, post_date, month, year, day, now)
            )
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving calendar post: {e}")
            return False
    
    @staticmethod
    def get_calendar_posts(client_id: str, month: str, year: int) -> Dict[int, Dict]:
        """Get calendar posts for a specific month."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT post_data, day FROM calendar_posts WHERE client_id = ? AND month = ? AND year = ?",
                (client_id, month, year)
            )
            rows = cursor.fetchall()
            
            return {row[1]: json.loads(row[0]) for row in rows}
            
        except Exception as e:
            print(f"Error getting calendar posts: {e}")
            return {}
    
    @staticmethod
    def get_all_calendar_posts(client_id: str) -> List:
        """Get all calendar posts for a client."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT post_data, post_date, month, year, day FROM calendar_posts WHERE client_id = ? ORDER BY post_date",
                (client_id,)
            )
            rows = cursor.fetchall()
            
            return rows
            
        except Exception as e:
            print(f"Error getting all calendar posts: {e}")
            return []
    
    @staticmethod
    def save_performance_metrics(
        client_id: str,
        platform: str,
        impressions: int,
        likes: int,
        comments: int,
        shares: int,
        date: str
    ) -> bool:
        """Save performance metrics."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            metric_id = str(uuid.uuid4())
            
            cursor.execute(
                "INSERT INTO performance_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (metric_id, client_id, platform, impressions, likes, comments, shares, date)
            )
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving metrics: {e}")
            return False
    
    @staticmethod
    def get_performance_metrics(client_id: str, days: int = 30) -> List:
        """Get performance metrics for the last N days."""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            cursor.execute(
                """SELECT platform, date, impressions, likes, comments, shares 
                   FROM performance_metrics 
                   WHERE client_id = ? AND date >= ? 
                   ORDER BY date""",
                (client_id, cutoff_date)
            )
            rows = cursor.fetchall()
            
            return rows
            
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return []