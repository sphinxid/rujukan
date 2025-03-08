import sqlite3
import os
import time
from datetime import datetime, timedelta
import secrets

class Database:
    def __init__(self, db_path="rujukan.db"):
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize the database with required tables if they don't exist."""
        # Check if database directory exists, create it if not
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        # Create database connection
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create pastes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pastes (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            title TEXT,
            created_at INTEGER NOT NULL,
            expires_at INTEGER,
            delete_token TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"Database initialized at {self.db_path}")
    
    def create_paste(self, content, title="", expiration_days=7):
        """
        Create a new paste in the database.
        
        Args:
            content: The text content of the paste
            title: Optional title for the paste
            expiration_days: Number of days until the paste expires
            
        Returns:
            tuple: (paste_id, delete_token)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate a unique ID and delete token
        paste_id = secrets.token_urlsafe(8)
        delete_token = secrets.token_urlsafe(16)
        
        # Calculate expiration timestamp
        created_at = int(time.time())
        if expiration_days == 0:  # Never expires
            expires_at = None
        else:
            expires_at = int((datetime.now() + timedelta(days=expiration_days)).timestamp())
        
        cursor.execute(
            "INSERT INTO pastes (id, content, title, created_at, expires_at, delete_token) VALUES (?, ?, ?, ?, ?, ?)",
            (paste_id, content, title, created_at, expires_at, delete_token)
        )
        
        conn.commit()
        conn.close()
        
        return paste_id, delete_token
    
    def get_paste(self, paste_id):
        """
        Retrieve a paste by its ID.
        
        Args:
            paste_id: The ID of the paste to retrieve
            
        Returns:
            dict: Paste data or None if not found or expired
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pastes WHERE id = ?", (paste_id,))
        paste = cursor.fetchone()
        
        conn.close()
        
        if paste:
            # Convert to dictionary
            paste_dict = dict(paste)
            
            # Check if paste has expired
            if paste_dict['expires_at'] and paste_dict['expires_at'] < time.time():
                self.delete_paste(paste_id)
                return None
                
            return paste_dict
        
        return None
    
    def get_recent_pastes(self, limit=10):
        """
        Get the most recent pastes.
        
        Args:
            limit: Maximum number of pastes to return
            
        Returns:
            list: List of paste dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        current_time = int(time.time())
        
        # Get non-expired pastes
        cursor.execute(
            "SELECT id, title, created_at FROM pastes WHERE expires_at IS NULL OR expires_at > ? ORDER BY created_at DESC LIMIT ?",
            (current_time, limit)
        )
        
        pastes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return pastes
    
    def delete_paste(self, paste_id, delete_token=None):
        """
        Delete a paste by ID and optional delete token.
        
        Args:
            paste_id: The ID of the paste to delete
            delete_token: If provided, must match the paste's delete token
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if delete_token:
            cursor.execute(
                "DELETE FROM pastes WHERE id = ? AND delete_token = ?",
                (paste_id, delete_token)
            )
        else:
            cursor.execute("DELETE FROM pastes WHERE id = ?", (paste_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def cleanup_expired(self):
        """Remove all expired pastes from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = int(time.time())
        cursor.execute(
            "DELETE FROM pastes WHERE expires_at IS NOT NULL AND expires_at < ?",
            (current_time,)
        )
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
