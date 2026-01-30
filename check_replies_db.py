from ext import app, db
from models import Comment, CommentReply, PostComment, PostCommentReply

def check_replies_in_database():
    """Check if there are any replies in the database"""
    with app.app_context():
        print("=== CHECKING REPLIES IN DATABASE ===")
        
        # Check mentor comments and their replies
        mentor_comments = Comment.query.all()
        print(f"Found {len(mentor_comments)} mentor comments")
        
        for comment in mentor_comments[:3]:  # Show first 3
            reply_count = comment.replies.count()
            print(f"  Comment {comment.id}: '{comment.text[:30]}...' has {reply_count} replies")
            
            if reply_count > 0:
                replies = comment.replies.all()
                for reply in replies:
                    print(f"    Reply: '{reply.content[:30]}...' by user {reply.user_id}")
        
        # Check post comments and their replies
        post_comments = PostComment.query.all()
        print(f"\nFound {len(post_comments)} post comments")
        
        for comment in post_comments[:3]:  # Show first 3
            reply_count = comment.replies.count()
            print(f"  Post Comment {comment.id}: '{comment.content[:30]}...' has {reply_count} replies")
            
            if reply_count > 0:
                replies = comment.replies.all()
                for reply in replies:
                    print(f"    Reply: '{reply.content[:30]}...' by user {reply.user_id}")
        
        # Check total counts
        total_mentor_replies = CommentReply.query.count()
        total_post_replies = PostCommentReply.query.count()
        
        print(f"\nTotal mentor replies in database: {total_mentor_replies}")
        print(f"Total post replies in database: {total_post_replies}")

if __name__ == "__main__":
    check_replies_in_database()
