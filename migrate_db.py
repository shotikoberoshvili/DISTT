#!/usr/bin/env python3
"""
ბაზის მიგრაციის სკრიპტი - ახალი სვეტების დასამატებლად
"""

from app import app
from models import db
import sqlite3
import os

def add_created_at_to_comments():
    """დაამატებს created_at სვეტს comments ცხიმურებელს"""
    with app.app_context():
        # მივიღოთ ბაზის ფაილის მდებადება
        db_path = 'instance/database.db'
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # შევამოწმოთ, არსებობს თუ არა უკვე ეს სვეტი
                cursor.execute("PRAGMA table_info(comments)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'created_at' not in columns:
                    print("ვამატებთ created_at სვეტს comments ცხიმურებელს...")
                    
                    # დავამატოთ სვეტი ნულოვანი ნაგულისმპით
                    cursor.execute("""
                        ALTER TABLE comments 
                        ADD COLUMN created_at DATETIME
                    """)
                    
                    # განვაახლოთ არსებული კომენტარებისთვის
                    cursor.execute("""
                        UPDATE comments 
                        SET created_at = datetime('now')
                        WHERE created_at IS NULL
                    """)
                    
                    conn.commit()
                    print("✅ created_at სვეტი წარმატებულია!")
                else:
                    print("✅ created_at სვეტი უკვე არსებობს")
                
            except Exception as e:
                print(f"❌ შეცდომა: {e}")
                conn.rollback()
            finally:
                conn.close()
        else:
            print("❌ ბაზის ფაილი არ არის ნაპოვნი")

def create_new_tables():
    """შექმნას ახალ ცხიმურებლებს"""
    with app.app_context():
        try:
            # შექმნას ახალი ცხიმურებლები
            db.create_all()
            print("✅ ახალი ცხიმურებლები შექმნილია!")
        except Exception as e:
            print(f"❌ შეცდომა: {e}")

if __name__ == "__main__":
    print("🚀 იწყება ბაზის მიგრაცია...")
    add_created_at_to_comments()
    create_new_tables()
    print("✅ მიგრაცია დასრულდა!")
