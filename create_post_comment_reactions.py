#!/usr/bin/env python3
"""
Create post_comment_reactions table
"""

from app import app
from models import db
import sqlite3
import os

def create_post_comment_reactions_table():
    """Create the post_comment_reactions table"""
    with app.app_context():
        db_path = 'instance/database.db'
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_comment_reactions'")
                if not cursor.fetchone():
                    print("Creating post_comment_reactions table...")
                    
                    cursor.execute("""
                        CREATE TABLE post_comment_reactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            post_comment_id INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
                            reaction_type VARCHAR(20) NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (post_comment_id) REFERENCES post_comments (id),
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    """)
                    
                    conn.commit()
                    print("✅ post_comment_reactions table created successfully!")
                else:
                    print("✅ post_comment_reactions table already exists")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                conn.rollback()
            finally:
                conn.close()
        else:
            print("❌ Database file not found")

if __name__ == "__main__":
    create_post_comment_reactions_table()
