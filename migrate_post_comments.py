from ext import app, db
from models import PostComment, PostCommentReply, PostCommentReaction, Comment, CommentReply, CommentReaction

def migrate_post_comments():
    """Migrate old comment system to new post comment system"""
    with app.app_context():
        print("Starting migration...")
        
        # Check if we need to migrate
        old_comments = Comment.query.all()
        if not old_comments:
            print("No old comments found. Migration not needed.")
            return
        
        print(f"Found {len(old_comments)} old comments to migrate")
        
        for old_comment in old_comments:
            # Create new post comment
            new_post_comment = PostComment(
                content=old_comment.text,
                post_id=old_comment.mentor_id,  # This might need adjustment based on your data
                user_id=old_comment.user_id,
                created_at=old_comment.created_at
            )
            db.session.add(new_post_comment)
            db.session.flush()  # Get the ID
            
            # Migrate reactions
            for old_reaction in old_comment.reactions:
                new_reaction = PostCommentReaction(
                    post_comment_id=new_post_comment.id,
                    user_id=old_reaction.user_id,
                    reaction_type=old_reaction.reaction_type,
                    created_at=old_reaction.created_at
                )
                db.session.add(new_reaction)
            
            # Migrate replies
            for old_reply in old_comment.replies:
                new_reply = PostCommentReply(
                    content=old_reply.content,
                    post_comment_id=new_post_comment.id,
                    user_id=old_reply.user_id,
                    created_at=old_reply.created_at
                )
                db.session.add(new_reply)
                db.session.flush()  # Get the ID
                
                # Migrate reply reactions
                for old_reply_reaction in old_reply.reactions:
                    new_reply_reaction = PostReplyReaction(
                        post_reply_id=new_reply.id,
                        user_id=old_reply_reaction.user_id,
                        reaction_type=old_reply_reaction.reaction_type,
                        created_at=old_reply_reaction.created_at
                    )
                    db.session.add(new_reply_reaction)
        
        try:
            db.session.commit()
            print("Migration completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_post_comments()
