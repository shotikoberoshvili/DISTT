from app import app
from models import db, User

with app.app_context():
    # Only create admin user if it doesn't exist
    admin = User.query.filter_by(email='admin@admin.com').first()
    if not admin:
        admin = User(
            name='admin',
            email='admin@admin.com', 
            phone_number='000000000',
            university='Admin University',
            faculty='Administration',
            password='adminpass',
            text='System administrator',
            role='Admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully!")
    else:
        print("✅ Admin user already exists!")
