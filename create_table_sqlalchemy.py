#!/usr/bin/env python3
"""
Create post_comment_reactions table using SQLAlchemy
"""

from app import app
from models import db, PostCommentReaction

def create_table():
    """Create the post_comment_reactions table using SQLAlchemy"""
    with app.app_context():
        try:
            # Create only the PostCommentReaction table
            PostCommentReaction.__table__.create(db.engine, checkfirst=True)
            print("✅ post_comment_reactions table created successfully!")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_table()
