from ext import app, db
from models import Comment, CommentReply

def test_reply_functionality():
    """Test reply functionality"""
    with app.app_context():
        print("=== TESTING REPLY FUNCTIONALITY ===")
        
        # Check if we have any comments
        comments = Comment.query.all()
        print(f"Found {len(comments)} comments")
        
        if comments:
            comment = comments[0]
            print(f"Testing with comment {comment.id}: {comment.text[:50]}...")
            
            # Check replies
            replies = CommentReply.query.filter_by(comment_id=comment.id).all()
            print(f"Comment has {len(replies)} replies")
            
            for reply in replies:
                print(f"  Reply: {reply.content[:50]}... by user {reply.user_id}")
            
            # Test creating a reply
            if len(replies) == 0:
                print("Creating test reply...")
                test_reply = CommentReply(
                    content="Test reply content",
                    comment_id=comment.id,
                    user_id=1  # Assuming user with ID 1 exists
                )
                db.session.add(test_reply)
                try:
                    db.session.commit()
                    print("Test reply created successfully!")
                except Exception as e:
                    print(f"Error creating test reply: {e}")
                    db.session.rollback()
        else:
            print("No comments found to test with")

if __name__ == "__main__":
    test_reply_functionality()
