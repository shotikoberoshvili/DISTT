from flask import render_template, redirect, flash, request, jsonify 
from werkzeug.security import check_password_hash
from datetime import datetime

from forms import RegisterForm, MentorForm, LoginForm, AskForm, CommentForm, ProfileForm, PostForm, PostCommentForm, MessageForm
from models import Mentor, Comment, User, Rating, Post, PostImage, PostComment, Reaction, Friendship, Message, Notification, CommentReaction, CommentReply, ReplyReaction, PostCommentReaction, PostCommentReply, PostReplyReaction
from ext import app, db, csrf
from flask_login import login_user, logout_user, login_required, current_user
import os

#CRUD create read update delate

@app.route("/delete/<int:mentor_id>", methods=['GET', 'POST'])
@login_required
def delete(mentor_id):
    if current_user.role != "Admin":
        flash("მხოლოდ ადმინს შეუძლია მენტორის წაშლა", "danger")
        return redirect("/")
    
    mentor = Mentor.query.get(mentor_id)
    if not mentor:
        flash("მენტორი ვერ მოიძებნა", "danger")
        return redirect("/tutors")

    db.session.delete(mentor)
    db.session.commit()

    flash("პროდუქტი წარმატებით წაიშალა", "danger")
    return redirect("/tutors")

@app.route('/')
def home():
    # Get posts for feed with priority to friends
    posts_query = Post.query.order_by(Post.created_at.desc())
    
    # If user is logged in, prioritize friends' posts
    if current_user.is_authenticated:
        # Get friends
        friends = []
        accepted_friendships = Friendship.query.filter(
            ((Friendship.requester_id == current_user.id) | (Friendship.addressee_id == current_user.id)) &
            (Friendship.status == 'accepted')
        ).all()
        
        for friendship in accepted_friendships:
            if friendship.requester_id == current_user.id:
                friends.append(friendship.addressee_id)
            else:
                friends.append(friendship.requester_id)
        
        if friends:
            # Get friend posts first, then other posts
            friend_posts = Post.query.filter(Post.user_id.in_(friends)).order_by(Post.created_at.desc()).limit(10).all()
            other_posts = Post.query.filter(~Post.user_id.in_(friends + [current_user.id])).order_by(Post.created_at.desc()).limit(5).all()
            user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).limit(3).all()
            
            posts = friend_posts + other_posts + user_posts
        else:
            posts = posts_query.limit(20).all()
    else:
        posts = posts_query.limit(20).all()
    
    # Create form for post creation
    form = PostForm()
    return render_template('index.html', posts=posts, form=form)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(form.name.data == User.name).first()
        if user and user.check_password(form.password.data):
            login_user(user)

            flash("თქვენ წარმატებით გაიარეთ ავტორიზაცია", "success")
            return redirect("/")
        else:
            flash("მოხდა შეცდომა", "danger")


    return render_template("login.html", form=form)

    
@app.route('/logout')
def logout():

    logout_user()

    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(name=form.name.data, email=form.email.data, phone_number=form.phone_number.data, university=form.university.data, faculty=form.faculty.data, password=form.password.data, role=form.role.data,text=form.text.data, )

        profile_img = form.profile_img.data
        img_location = os.path.join(app.root_path, 'static/images', profile_img.filename)
        profile_img.save(img_location)
        new_user.profile_img = profile_img.filename


        db.session.add(new_user)
        db.session.commit()

        flash("თქვენ წარმატებით დარეგისტრირდით, გაიარეთ ავტორიზაცია", "success")
        return redirect('/login')

    return render_template('reg.html', form=form,)



@app.route('/calendar')
def calendar():
    return render_template('calendar.html')


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = ProfileForm(
        name=current_user.name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        university=current_user.university,
        faculty=current_user.faculty,
        text=current_user.text,
    )

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        current_user.university = form.university.data
        current_user.faculty = form.faculty.data
        current_user.text = form.text.data

        if form.profile_img.data:
            image = form.profile_img.data
            img_location = os.path.join(app.root_path, 'static/images', image.filename)
            image.save(img_location)
            current_user.profile_img = image.filename

        db.session.commit()
        flash("პროფილი წარმატებით განახლდა!", "success")
        return redirect('/account')

    return render_template('account.html', form=form)


@app.route('/profiles/<int:profile_id>')
def profile(profile_id):
    user = User.query.get_or_404(profile_id)
    return render_template('profile.html', user=user)

@app.route('/add_mentor', methods=['GET', 'POST'])
@login_required
def add_mentor ():
    form = MentorForm()
    if form.validate_on_submit():
        if current_user.role != "Admin":
            flash("მხოლოდ ადმინს შეუძლია მენტორის დამატება", "danger")
            return redirect("/")

        new_mentor = Mentor(name=form.name.data, subject=form.subject.data, price=form.price.data, text = form.text.data)
        image = form.image.data
        img_location = os.path.join(app.root_path, 'static/images', image.filename)
        image.save(img_location)
        new_mentor.image = image.filename

        db.session.add(new_mentor)
        db.session.commit()

        flash('Mentors successfully added!', 'success')
        return redirect("/tutors")

    return render_template('add_mentor.html', form = form)

@app.route("/edit_mentor/<int:mentor_id>", methods = ['POST', 'GET'])
@login_required
def edit_mentor(mentor_id):
    mentor = Mentor.query.get(mentor_id)
    if current_user.role != "Admin":
        flash("მხოლოდ ადმინს შეუძლია მენტორის რედაქტირება", "danger")
        return redirect("/")

    # დაამატეთ text=mentor.text აქ:
    form = MentorForm(name=mentor.name, subject=mentor.subject, price=mentor.price, text=mentor.text)
    
    if form.validate_on_submit():
        mentor.name = form.name.data
        mentor.subject = form.subject.data
        mentor.price = form.price.data
        mentor.text = form.text.data # ეს უკვე სწორად გიწერიათ

        db.session.commit()
        flash("მენტორის ინფორმაცია წარმატებით განახლდა!", "success")
        return redirect("/tutors")
    return render_template("add_mentor.html", form = form)



@app.route('/tutors')
def tutors():
     mentors = Mentor.query.all()

     mentor_ratings = {}
     for mentor in mentors:
         ratings = mentor.ratings.all() if hasattr(mentor, 'ratings') else []
         count = len(ratings)
         if count:
             avg = round(sum(r.stars for r in ratings) / count, 1)
         else:
             avg = None
         mentor_ratings[mentor.id] = {"avg": avg, "count": count}

     return render_template('tutors.html', mentors=mentors, mentor_ratings=mentor_ratings)
@app.route('/detailed/<int:mentor_id>', methods=['GET', 'POST'])
def detailed(mentor_id):
     mentor = Mentor.query.get(mentor_id)
     comments = Comment.query.filter(Comment.mentor_id == mentor_id)

     form = CommentForm()
     if form.validate_on_submit():
         # მხოლოდ ავტორიზებულ სტუდენტს შეუძლია კომენტარის დამატება
         if not current_user.is_authenticated or current_user.role != "სტუდენტი":
             flash("კომენტარის დასაწერად საჭიროა ავტორიზაცია სტუდენტის როლით.", "danger")
             return redirect(f"/detailed/{mentor_id}")

         new_comment = Comment(text=form.text.data, mentor_id=mentor_id, user_id=current_user.id)
         db.session.add(new_comment)
         db.session.commit()
         flash("კომენტარი წარმატებით დაემატა!", "success")
         return redirect(f"/detailed/{mentor_id}")

     avg_rating = None
     ratings_count = 0
     user_rating = None

     if mentor:
         ratings = mentor.ratings.all() if hasattr(mentor, 'ratings') else []
         ratings_count = len(ratings)
         if ratings_count:
             avg_rating = round(sum(r.stars for r in ratings) / ratings_count, 1)

     if current_user.is_authenticated:
         existing = Rating.query.filter_by(mentor_id=mentor_id, user_id=current_user.id).first()
         if existing:
             user_rating = existing.stars

     return render_template(
         'detailed.html',
         mentor=mentor,
         comments=comments,
         avg_rating=avg_rating,
         ratings_count=ratings_count,
         user_rating=user_rating,
         form=form,
     )


@app.route('/rate_mentor/<int:mentor_id>', methods=['POST'])
@login_required
def rate_mentor(mentor_id):
     mentor = Mentor.query.get_or_404(mentor_id)

     if current_user.role != "სტუდენტი":
         flash("მხოლოდ სტუდენტს შეუძლია მენტორის შეფასება.", "danger")
         return redirect(f"/detailed/{mentor_id}")

     try:
         stars = int(request.form.get('stars', 0))
     except ValueError:
         stars = 0

     if stars < 1 or stars > 5:
         flash("შეფასება უნდა იყოს 1-დან 5 ვარსკვლავამდე.", "danger")
         return redirect(f"/detailed/{mentor_id}")

     existing = Rating.query.filter_by(mentor_id=mentor_id, user_id=current_user.id).first()
     if existing:
         existing.stars = stars
     else:
         new_rating = Rating(stars=stars, mentor_id=mentor_id, user_id=current_user.id)
         db.session.add(new_rating)

     db.session.commit()
     flash("შენი შეფასება შენახულია!", "success")
     return redirect(f"/detailed/{mentor_id}")


# Social Media Routes

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    print("DEBUG: Create post route accessed")
    form = PostForm()
    print(f"DEBUG: Form method: {request.method}")
    
    if request.method == 'POST':
        print(f"DEBUG: Form data: {request.form}")
        print(f"DEBUG: Form validate: {form.validate_on_submit()}")
        
    if form.validate_on_submit():
        print("DEBUG: Form validation passed")
        new_post = Post(content=form.content.data, user_id=current_user.id)
        db.session.add(new_post)
        db.session.flush()  # Get the post ID
        
        print(f"DEBUG: Post created with ID: {new_post.id}")
        
        if form.images.data:
            image = form.images.data
            filename = f"post_{new_post.id}_{image.filename}"
            img_location = os.path.join(app.root_path, 'static/images', filename)
            image.save(img_location)
            
            post_image = PostImage(post_id=new_post.id, image_path=filename)
            db.session.add(post_image)
            print(f"DEBUG: Image saved: {filename}")
        
        db.session.commit()
        flash("პოსტი წარმატებით გაზიარდა!", "success")
        print("DEBUG: Post saved successfully")
        return redirect("/")
    else:
        if request.method == 'POST':
            print(f"DEBUG: Form errors: {form.errors}")
    
    return render_template('create_post.html', form=form)

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash("მხოლოდ საკუთარი პოსტის რედაქტირება შეგიძლიათ", "danger")
        return redirect("/")
    
    form = PostForm(content=post.content)
    if form.validate_on_submit():
        post.content = form.content.data
        post.updated_at = datetime.utcnow()
        
        if form.images.data:
            image = form.images.data
            filename = f"post_{post.id}_{image.filename}"
            img_location = os.path.join(app.root_path, 'static/images', filename)
            image.save(img_location)
            
            post_image = PostImage(post_id=post.id, image_path=filename)
            db.session.add(post_image)
        
        db.session.commit()
        flash("პოსტი წარმატებით განახლდა!", "success")
        return redirect("/")
    
    # Return template for GET request
    return render_template('edit_post.html', form=form, post=post)

@app.route('/delete_post/<int:post_id>', methods=['GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Only allow user to delete their own posts
    if post.user_id != current_user.id:
        flash("მხოლოდ საკუთარი პოსტის წაშლა შეგიძლიათ", "danger")
        return redirect("/")
    
    db.session.delete(post)
    db.session.commit()
    flash("პოსტი წარმატებით წაიშალა", "success")
    return redirect("/")

@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    print(f"DEBUG: Adding comment to post {post_id}")
    post = Post.query.get_or_404(post_id)
    
    # Handle form submission
    content = request.form.get('content', '').strip()
    
    print(f"DEBUG: Comment content: '{content}'")
    
    if not content:
        flash("კომენტარი ცარიელია", "danger")
        return redirect("/")
    
    new_comment = PostComment(
        content=content,
        post_id=post_id,
        user_id=current_user.id
    )
    db.session.add(new_comment)
    
    # Create notification for post owner (if not commenting on own post)
    if post.user_id != current_user.id:
        notification_content = f"{current_user.name}-მა დაუჭირა კომენტარი თქვენს პოსტზე"
        notification = Notification(
            user_id=post.user_id,
            type="comment",
            content=notification_content,
            related_user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(notification)
    
    db.session.commit()
    print(f"DEBUG: Comment saved successfully with ID: {new_comment.id}")
    
    flash("კომენტარი წარმატებით დაემატა!", "success")
    return redirect("/")

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = PostComment.query.get_or_404(comment_id)
    
    # Only allow user to delete their own comments
    if comment.user_id != current_user.id:
        flash("მხოლოდ საკუთარი კომენტარის წაშლა შეგიძლიათ", "danger")
        return redirect("/")
    
    db.session.delete(comment)
    db.session.commit()
    
    flash("კომენტარი წარმატებით წაიშალა", "success")
    return redirect("/")

@app.route('/react/<int:post_id>/<string:reaction_type>', methods=['POST'])
@login_required
def react_post(post_id, reaction_type):
    print(f"DEBUG: Reacting to post {post_id} with {reaction_type}")
    post = Post.query.get_or_404(post_id)
    
    # Check if user already reacted
    existing_reaction = Reaction.query.filter_by(
        post_id=post_id, 
        user_id=current_user.id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Remove reaction if same type
            db.session.delete(existing_reaction)
            action = "removed"
        else:
            # Change reaction type
            existing_reaction.reaction_type = reaction_type
            action = "changed"
    else:
        # Add new reaction
        new_reaction = Reaction(
            post_id=post_id,
            user_id=current_user.id,
            reaction_type=reaction_type
        )
        db.session.add(new_reaction)
        action = "added"
    
    # Create notification for post owner (if not reacting to own post)
    if post.user_id != current_user.id:
        notification_content = f"{current_user.name}-მა {action} რეაქცია თქვენს პოსტზე"
        notification = Notification(
            user_id=post.user_id,
            type="reaction",
            content=notification_content,
            related_user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(notification)
    
    db.session.commit()
    print(f"DEBUG: Reaction {action} successfully")
    
    return redirect("/")

@app.route('/react_comment/<int:comment_id>/<string:reaction_type>', methods=['POST'])
@login_required
def react_comment(comment_id, reaction_type):
    print(f"DEBUG: Reacting to comment {comment_id} with {reaction_type}")
    print(f"DEBUG: Request from: {request.referrer}")
    
    comment = PostComment.query.get_or_404(comment_id)
    print(f"DEBUG: Found comment: {comment.content}")
    
    # Check if user already reacted
    existing_reaction = PostCommentReaction.query.filter_by(
        post_comment_id=comment_id, 
        user_id=current_user.id
    ).first()
    
    print(f"DEBUG: Existing reaction: {existing_reaction}")
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Remove reaction if same type
            db.session.delete(existing_reaction)
            action = "removed"
        else:
            # Change reaction type
            existing_reaction.reaction_type = reaction_type
            action = "changed"
    else:
        # Add new reaction
        new_reaction = PostCommentReaction(
            post_comment_id=comment_id,
            user_id=current_user.id,
            reaction_type=reaction_type
        )
        db.session.add(new_reaction)
        action = "added"
    
    print(f"DEBUG: Action: {action}")
    
    # Create notification for comment owner (if not reacting to own comment)
    if comment.user_id != current_user.id:
        notification_content = f"{current_user.name}-მა {action} რეაქცია თქვენს კომენტარზე"
        notification = Notification(
            user_id=comment.user_id,
            type="comment_reaction",
            content=notification_content,
            related_user_id=current_user.id,
            post_id=comment.post_id
        )
        db.session.add(notification)
    
    try:
        db.session.commit()
        print(f"DEBUG: Successfully committed reaction")
        # Check the count after commit
        reaction_count = comment.reactions.count()
        print(f"DEBUG: Total reactions for comment {comment_id}: {reaction_count}")
    except Exception as e:
        print(f"DEBUG: Error committing reaction: {e}")
        db.session.rollback()
    
    # Check if we came from detailed page (mentor comments) or main page (post comments)
    if request.referrer and '/detailed/' in request.referrer:
        # This is a mentor comment, should redirect back to detailed page
        mentor_id = comment.mentor_id if hasattr(comment, 'mentor_id') else None
        if mentor_id:
            print(f"DEBUG: Redirecting to detailed page for mentor {mentor_id}")
            return redirect(f"/detailed/{mentor_id}")
    
    print(f"DEBUG: Redirecting to home page")
    return redirect("/")

@app.route('/react_reply/<int:reply_id>/<string:reaction_type>', methods=['POST'])
@login_required
def react_reply(reply_id, reaction_type):
    reply = PostCommentReply.query.get_or_404(reply_id)
    
    # Check if user already reacted
    existing_reaction = PostReplyReaction.query.filter_by(
        post_reply_id=reply_id, 
        user_id=current_user.id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Remove reaction if same type
            db.session.delete(existing_reaction)
            action = "წაიშალა"
        else:
            # Change reaction type
            existing_reaction.reaction_type = reaction_type
            action = "შეიცვალა"
    else:
        # Add new reaction
        new_reaction = PostReplyReaction(
            post_reply_id=reply_id,
            user_id=current_user.id,
            reaction_type=reaction_type
        )
        db.session.add(new_reaction)
        action = "დაემატა"
    
    # Create notification for reply owner (if not reacting to own reply)
    if reply.user_id != current_user.id:
        notification_content = f"{current_user.name}-მა {action} რეაქცია თქვენს პასუხზე"
        notification = Notification(
            user_id=reply.user_id,
            type="reply_reaction",
            content=notification_content,
            related_user_id=current_user.id,
            post_id=reply.post_comment.post_id
        )
        db.session.add(notification)
    
    db.session.commit()
@login_required
def react_mentor_comment(comment_id, reaction_type):
    print(f"DEBUG: Reacting to mentor comment {comment_id} with {reaction_type}")
    
    # Check if user is student
    if current_user.role != 'სტუდენტი':
        flash("მხოლოდ სტუდენტებს შეუძლიათ რეაქციის გამოხატვა", "danger")
        return redirect(f"/detailed/{comment.mentor_id}")
    
    comment = Comment.query.get_or_404(comment_id)
    print(f"DEBUG: Found mentor comment: {comment.text}")
    
    # Check if user already reacted
    existing_reaction = CommentReaction.query.filter_by(
        comment_id=comment_id, 
        user_id=current_user.id
    ).first()
    
    print(f"DEBUG: Existing reaction: {existing_reaction}")
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Remove reaction if same type
            db.session.delete(existing_reaction)
            action = "removed"
        else:
            # Change reaction type
            existing_reaction.reaction_type = reaction_type
            action = "შეიცვალა"
    else:
        # Add new reaction
        new_reaction = CommentReaction(
            comment_id=comment_id,
            user_id=current_user.id,
            reaction_type=reaction_type
        )
        db.session.add(new_reaction)
        action = "დაემატა"
    
    print(f"DEBUG: Action: {action}")
    
    # Create notification for comment owner (if not reacting to own comment)
    if comment.user_id != current_user.id:
        notification_content = f"{current_user.name}-მა {action} რეაქცია თქვენს კომენტარზე"
        notification = Notification(
            user_id=comment.user_id,
            type="comment_reaction",
            content=notification_content,
            related_user_id=current_user.id
        )
        db.session.add(notification)
    
    try:
        db.session.commit()
        print(f"DEBUG: Successfully committed mentor comment reaction")
        # Check the count after commit
        reaction_count = comment.reactions.count()
        print(f"DEBUG: Total reactions for mentor comment {comment_id}: {reaction_count}")
    except Exception as e:
        print(f"DEBUG: Error committing mentor comment reaction: {e}")
        db.session.rollback()
    
    return redirect(f"/detailed/{comment.mentor_id}")

@app.route('/reply_mentor_comment/<int:comment_id>', methods=['POST'])
@login_required
def reply_mentor_comment(comment_id):
    print(f"DEBUG: Replying to mentor comment {comment_id}")
    comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content', '').strip()
    
    print(f"DEBUG: Reply content: {content}")
    
    if not content:
        flash("პასუხი ცარიელია", "danger")
        return redirect(f"/detailed/{comment.mentor_id}")
    
    new_reply = CommentReply(
        content=content,
        comment_id=comment_id,
        user_id=current_user.id
    )
    db.session.add(new_reply)
    
    print(f"DEBUG: Added mentor reply to database")
    
    # Create notification for comment owner (if not replying to own comment)
    if comment.user_id != current_user.id:
        notification_content = f"{current_user.name}-მა გაუწერა პასუხი თქვენს კომენტარზე"
        notification = Notification(
            user_id=comment.user_id,
            type="comment_reply",
            content=notification_content,
            related_user_id=current_user.id
        )
        db.session.add(notification)
    
    try:
        db.session.commit()
        print(f"DEBUG: Successfully committed mentor reply")
        # Check the count after commit
        reply_count = comment.replies.count()
        print(f"DEBUG: Total replies for mentor comment {comment_id}: {reply_count}")
        flash("პასუხი წარმატებით დაემატა!", "success")
    except Exception as e:
        print(f"DEBUG: Error committing mentor reply: {e}")
        db.session.rollback()
        flash("შეცდომა პასუხის დამატებისას", "danger")
    
    return redirect(f"/detailed/{comment.mentor_id}")

@app.route('/reply_comment/<int:comment_id>', methods=['POST'])
@login_required
def reply_comment(comment_id):
    print(f"DEBUG: Replying to comment {comment_id}")
    print(f"DEBUG: Request from: {request.referrer}")
    
    comment = PostComment.query.get_or_404(comment_id)
    content = request.form.get('content', '').strip()
    
    print(f"DEBUG: Reply content: {content}")
    
    if not content:
        flash("პასუხი ცარიელია", "danger")
        # Check where to redirect back
        if request.referrer and '/detailed/' in request.referrer:
            mentor_id = comment.mentor_id if hasattr(comment, 'mentor_id') else None
            if mentor_id:
                return redirect(f"/detailed/{mentor_id}")
        return redirect("/")
    
    new_reply = PostCommentReply(
        content=content,
        post_comment_id=comment_id,
        user_id=current_user.id
    )
    db.session.add(new_reply)
    
    print(f"DEBUG: Added reply to database")
    
    # Create notification for comment owner (if not replying to own comment)
    if comment.user_id != current_user.id:
        notification_content = f"{current_user.name}-მა გაუწერა პასუხი თქვენს კომენტარზე"
        notification = Notification(
            user_id=comment.user_id,
            type="comment_reply",
            content=notification_content,
            related_user_id=current_user.id,
            post_id=comment.post_id
        )
        db.session.add(notification)
    
    try:
        db.session.commit()
        print(f"DEBUG: Successfully committed reply")
        # Check the count after commit
        reply_count = comment.replies.count()
        print(f"DEBUG: Total replies for comment {comment_id}: {reply_count}")
        flash("პასუხი წარმატებით დაემატა!", "success")
    except Exception as e:
        print(f"DEBUG: Error committing reply: {e}")
        db.session.rollback()
        flash("შეცდომა პასუხის დამატებისას", "danger")
    
    # Check where to redirect back
    if request.referrer and '/detailed/' in request.referrer:
        mentor_id = comment.mentor_id if hasattr(comment, 'mentor_id') else None
        if mentor_id:
            print(f"DEBUG: Redirecting to detailed page for mentor {mentor_id}")
            return redirect(f"/detailed/{mentor_id}")
    
    print(f"DEBUG: Redirecting to home page")
    return redirect("/")

@app.route('/send_friend_request/<int:user_id>', methods=['GET'])
@login_required
def send_friend_request(user_id):
    if user_id == current_user.id:
        flash("თავის თავს მეგობრობის გაგზავნა არ შეგიძლიათ", "danger")
        return redirect("/")
    
    existing_request = Friendship.query.filter_by(
        requester_id=current_user.id,
        addressee_id=user_id
    ).first()
    
    if existing_request:
        flash("მოთხოვნა უკვე გაგზავნილია", "warning")
    else:
        new_request = Friendship(
            requester_id=current_user.id,
            addressee_id=user_id,
            status='pending'
        )
        db.session.add(new_request)
        
        # Create notification for the user receiving the request
        notification_content = f"{current_user.name}-მა გაგზავნა მეგობრობის მოთხოვნა"
        notification = Notification(
            user_id=user_id,
            type="friend_request",
            content=notification_content,
            related_user_id=current_user.id
        )
        db.session.add(notification)
        
        db.session.commit()
        flash("მეგობრობის მოთხოვნა გაგზავნილია!", "success")
    
    return redirect(f"/profile/{user_id}")

@app.route('/respond_friend_request/<int:request_id>/<string:response>', methods=['GET'])
@login_required
def respond_friend_request(request_id, response):
    friendship = Friendship.query.get_or_404(request_id)
    
    if friendship.addressee_id != current_user.id:
        flash("არასწორი მოთხოვნა", "danger")
        return redirect("/settings")
    
    if response == 'accept':
        friendship.status = 'accepted'
        
        # Create notification for the requester
        notification_content = f"{current_user.name}-მა დაადასტურა თქვენი მეგობრობის მოთხოვნა"
        notification = Notification(
            user_id=friendship.requester_id,
            type="friend_request",
            content=notification_content,
            related_user_id=current_user.id
        )
        db.session.add(notification)
        
        flash("მეგობრობის მოთხოვნა მიღებულია!", "success")
    else:
        db.session.delete(friendship)
        flash("მეგობრობის მოთხოვნა უარყოფილია", "info")
    
    db.session.commit()
    return redirect("/settings")

# Notifications routes
@app.route('/notifications', methods=['GET'])
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(50).all()
    
    # Mark notifications as read
    for notification in user_notifications:
        if not notification.is_read:
            notification.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/notifications/count', methods=['GET'])
@login_required
def notifications_count():
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': unread_count})

@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/messages')
@login_required
def messages():
    received_messages = Message.query.filter_by(receiver_id=current_user.id)\
        .order_by(Message.created_at.desc()).all()
    sent_messages = Message.query.filter_by(sender_id=current_user.id)\
        .order_by(Message.created_at.desc()).all()
    
    return render_template('messages.html', 
                         received_messages=received_messages,
                         sent_messages=sent_messages)

@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
@csrf.exempt  # გამოვიყენოთ AJAX-სთვის გამოსაღება
def chat(user_id):
    other_user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            new_message = Message(
                sender_id=current_user.id,
                receiver_id=user_id,
                content=content
            )
            db.session.add(new_message)
            
            # Create notification for receiver
            notification_content = f"{current_user.name}-მა გამოგიგზავნათ შეტყობინება"
            notification = Notification(
                user_id=user_id,
                type="message",
                content=notification_content,
                related_user_id=current_user.id
            )
            db.session.add(notification)
            
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'შეტყობინება ცარიელია'})
    
    # GET request - show chat
    chat_messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at).all()
    
    # Mark messages as read
    for message in chat_messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
    db.session.commit()
    
    form = MessageForm()
    return render_template('chat.html', other_user=other_user, 
                         chat_messages=chat_messages, form=form)

@app.route('/profile/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id)\
        .order_by(Post.created_at.desc()).all()
    
    # Get received requests for current user
    received_requests = []
    if current_user.is_authenticated:
        received_requests = Friendship.query.filter_by(
            addressee_id=current_user.id, 
            status='pending'
        ).all()
    
    # Check friendship status
    friendship_status = None
    if current_user.is_authenticated and current_user.id != user_id:
        friendship = Friendship.query.filter(
            ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == user_id)) |
            ((Friendship.requester_id == user_id) & (Friendship.addressee_id == current_user.id))
        ).first()
        
        if friendship:
            if friendship.status == 'pending':
                if friendship.requester_id == current_user.id:
                    friendship_status = 'sent'
                else:
                    friendship_status = 'received'
            elif friendship.status == 'accepted':
                friendship_status = 'friends'
        else:
            friendship_status = 'none'
    
    return render_template('user_profile.html', user=user, posts=posts, 
                         friendship_status=friendship_status, received_requests=received_requests)

@app.route('/settings')
@login_required
def settings():
    # Get friend requests
    received_requests = Friendship.query.filter_by(
        addressee_id=current_user.id, 
        status='pending'
    ).all()
    
    # Get friends
    friends = []
    accepted_friendships = Friendship.query.filter(
        ((Friendship.requester_id == current_user.id) | (Friendship.addressee_id == current_user.id)) &\
        (Friendship.status == 'accepted')
    ).all()
    
    for friendship in accepted_friendships:
        if friendship.requester_id == current_user.id:
            friends.append(friendship.addressee)
        else:
            friends.append(friendship.requester)
    
    # Get user's posts
    user_posts = Post.query.filter_by(user_id=current_user.id)\
        .order_by(Post.created_at.desc()).all()
    
    return render_template('settings.html', 
                         received_requests=received_requests,
                         friends=friends,
                         user_posts=user_posts)
