from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Create application context
with app.app_context():
    # Check if user already exists
    existing_user = User.query.filter_by(email='lucas@gmail.com').first()
    if existing_user:
        print("User with email lucas@gmail.com already exists!")
    else:
        # Create new user
        new_user = User(
            username='lucas',
            email='lucas@gmail.com',
            password_hash=generate_password_hash('011326')
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        print("User 'lucas' added successfully!")
