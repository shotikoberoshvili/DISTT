from ext import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Mentor(db.Model):
    __tablename__ = 'mentors'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    subject = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer(), nullable=True)
    image = db.Column(db.String(), default='default_.jpg')
    text = db.Column(db.String(), nullable=False )

    ratings = db.relationship("Rating", backref="mentor", lazy="dynamic")

class Comment(db.Model):
     __tablename__ = 'comments'

     id = db.Column(db.Integer(), primary_key=True)
     text = db.Column(db.String(), nullable=False)
     mentor_id = db.Column(db.Integer(), db.ForeignKey("mentors.id"))
     user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
     created_at = db.Column(db.DateTime, default=datetime.utcnow)
     
     # რელაციები კომენტარის რეაქციებისთვის
     reactions = db.relationship("CommentReaction", back_populates="comment", lazy="dynamic", cascade="all, delete-orphan")
     replies = db.relationship("CommentReply", back_populates="comment", lazy="dynamic", cascade="all, delete-orphan")

class Rating(db.Model):
     __tablename__ = "ratings"

     id = db.Column(db.Integer(), primary_key=True)
     stars = db.Column(db.Integer(), nullable=False)
     mentor_id = db.Column(db.Integer(), db.ForeignKey("mentors.id"), nullable=False)
     user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)

class User(db.Model,UserMixin) :
     __tablename__ = "users"

     id = db.Column(db.Integer(), primary_key= True)
     name = db.Column(db.String())
     email = db.Column(db.String())
     phone_number = db.Column(db.String())
     university = db.Column(db.String())
     faculty = db.Column(db.String())
     password = db.Column(db.String())
     role = db.Column(db.String())
     profile_img = db.Column(db.String(), default='default.jpg')
     text = db.Column(db.String())
     comments = db.relationship("Comment", backref="user", lazy="dynamic")
     def __init__(self, name, email, phone_number, university, faculty, text, 
                  password=None, role="Guest", profile_img="default.jpg"):
          self.name = name
          self.email = email
          self.phone_number = phone_number
          self.university = university
          self.faculty = faculty
          self.text = text
          self.role = role
          self.profile_img = profile_img
          if password:
              self.password = generate_password_hash(password)

     def check_password(self, password):
          return check_password_hash (self.password, password)



class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship("User", backref="posts")
    images = db.relationship("PostImage", backref="post", lazy="dynamic", cascade="all, delete-orphan")
    comments = db.relationship("PostComment", backref="post", lazy="dynamic", cascade="all, delete-orphan")
    reactions = db.relationship("Reaction", backref="post", lazy="dynamic", cascade="all, delete-orphan")

class PostImage(db.Model):
    __tablename__ = 'post_images'
    id = db.Column(db.Integer(), primary_key=True)
    post_id = db.Column(db.Integer(), db.ForeignKey("posts.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

class PostComment(db.Model):
    __tablename__ = 'post_comments'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer(), db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="post_comments")
    reactions = db.relationship("PostCommentReaction", back_populates="post_comment", lazy="dynamic", cascade="all, delete-orphan")
    replies = db.relationship("PostCommentReply", back_populates="post_comment", lazy="dynamic", cascade="all, delete-orphan")

class Reaction(db.Model):
    __tablename__ = 'reactions'
    id = db.Column(db.Integer(), primary_key=True)
    post_id = db.Column(db.Integer(), db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, support, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="reactions")

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer(), primary_key=True)
    requester_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    addressee_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    requester = db.relationship("User", foreign_keys=[requester_id], backref="sent_requests")
    addressee = db.relationship("User", foreign_keys=[addressee_id], backref="received_requests")

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer(), primary_key=True)
    sender_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # reaction, comment, friend_request, message
    content = db.Column(db.Text, nullable=False)
    related_user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=True)  # ვინ გააკეთა მოქმედება
    post_id = db.Column(db.Integer(), db.ForeignKey("posts.id"), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", foreign_keys=[user_id], backref="notifications")
    related_user = db.relationship("User", foreign_keys=[related_user_id])
    post = db.relationship("Post", backref="notifications")

class CommentReaction(db.Model):
    __tablename__ = 'comment_reactions'
    id = db.Column(db.Integer(), primary_key=True)
    comment_id = db.Column(db.Integer(), db.ForeignKey("comments.id"), nullable=False)  # შეცვლილია post_comments-დან comments
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, laugh, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="comment_reactions")
    comment = db.relationship("Comment", back_populates="reactions")

class PostCommentReaction(db.Model):
    __tablename__ = 'post_comment_reactions'
    id = db.Column(db.Integer(), primary_key=True)
    post_comment_id = db.Column(db.Integer(), db.ForeignKey("post_comments.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, laugh, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="post_comment_reactions")
    post_comment = db.relationship("PostComment", back_populates="reactions")

class PostCommentReply(db.Model):
    __tablename__ = 'post_comment_replies'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    post_comment_id = db.Column(db.Integer(), db.ForeignKey("post_comments.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="post_comment_replies")
    post_comment = db.relationship("PostComment", back_populates="replies")
    reactions = db.relationship("PostReplyReaction", back_populates="post_reply", lazy="dynamic", cascade="all, delete-orphan")

class PostReplyReaction(db.Model):
    __tablename__ = 'post_reply_reactions'
    id = db.Column(db.Integer(), primary_key=True)
    post_reply_id = db.Column(db.Integer(), db.ForeignKey("post_comment_replies.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, laugh, angry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="post_reply_reactions")
    post_reply = db.relationship("PostCommentReply", back_populates="reactions")

class CommentReply(db.Model):
    __tablename__ = 'comment_replies'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    comment_id = db.Column(db.Integer(), db.ForeignKey("comments.id"), nullable=False)  # შეცვლილია post_comments-დან comments
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="comment_replies")
    comment = db.relationship("Comment", back_populates="replies")
    reactions = db.relationship("ReplyReaction", back_populates="reply", lazy="dynamic", cascade="all, delete-orphan")

class ReplyReaction(db.Model):
    __tablename__ = 'reply_reactions'
    id = db.Column(db.Integer(), primary_key=True)
    reply_id = db.Column(db.Integer(), db.ForeignKey("comment_replies.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, laugh, angry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="reply_reactions")
    reply = db.relationship("CommentReply", back_populates="reactions")

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(user_id)
