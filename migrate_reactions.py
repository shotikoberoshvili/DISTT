#!/usr/bin/env python3
"""
მიგრაციის სკრიპტი ReplyReaction ცხრილის შესაქმნელად
"""

from ext import db
from models import ReplyReaction

def create_reply_reactions_table():
    """ქმნის ReplyReaction ცხრილს"""
    try:
        # შევქმნათ ცხრილი
        ReplyReaction.__table__.create(db.engine)
        print("✅ ReplyReaction ცხრილი წარმატებით შეიქმნა")
    except Exception as e:
        if "already exists" in str(e):
            print("⚠️  ReplyReaction ცხრილი უკვე არსებობს")
        else:
            print(f"❌ შეცდომა: {e}")

if __name__ == "__main__":
    create_reply_reactions_table()
