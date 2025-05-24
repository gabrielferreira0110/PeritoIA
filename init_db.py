from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Create application context
with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
    
    # Check if user exists
    existing_user = User.query.filter_by(username='lucas').first()
    
    if not existing_user:
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
    else:
        print("User 'lucas' already exists in the database.")
        
    # Print all users for verification
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    for user in users:
        print(f"  - {user.username} ({user.email})")

