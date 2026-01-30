from ext import app, db
from models import PostComment, PostCommentReply, PostCommentReaction

def check_database():
    """Check database contents and relationships"""
    with app.app_context():
        print("=== DATABASE CHECK ===")
        
        # Check PostComments
        post_comments = PostComment.query.all()
        print(f"PostComments count: {len(post_comments)}")
        
        for comment in post_comments[:3]:  # Show first 3
            print(f"  Comment {comment.id}: {comment.content[:50]}...")
            print(f"    Reactions count: {comment.reactions.count()}")
            print(f"    Replies count: {comment.replies.count()}")
        
        # Check PostCommentReactions
        reactions = PostCommentReaction.query.all()
        print(f"PostCommentReactions count: {len(reactions)}")
        
        for reaction in reactions[:3]:  # Show first 3
            print(f"  Reaction {reaction.id}: {reaction.reaction_type} by user {reaction.user_id} on comment {reaction.post_comment_id}")
        
        # Check PostCommentReplies
        replies = PostCommentReply.query.all()
        print(f"PostCommentReplies count: {len(replies)}")
        
        for reply in replies[:3]:  # Show first 3
            print(f"  Reply {reply.id}: {reply.content[:50]}... by user {reply.user_id} on comment {reply.post_comment_id}")
            print(f"    Reactions count: {reply.reactions.count()}")

if __name__ == "__main__":
    check_database()
