#!/usr/bin/env python3
"""
Create post comment reply and reaction tables
"""

from app import app
from models import db, PostCommentReply, PostReplyReaction

def create_tables():
    """Create the missing post comment tables"""
    with app.app_context():
        try:
            # Create the new tables
            PostCommentReply.__table__.create(db.engine, checkfirst=True)
            PostReplyReaction.__table__.create(db.engine, checkfirst=True)
            print("✅ Post comment reply and reaction tables created successfully!")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_tables()
