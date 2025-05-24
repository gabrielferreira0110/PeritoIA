from app import app, db
import os

# Path to the corrupted database
db_path = os.path.join('instance', 'perito_ia.db')

# Check if database file exists and remove it
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Removed corrupted database: {db_path}")
    except Exception as e:
        print(f"Error removing database: {e}")

# Create application context
with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
    
    # Now let's add the user
    from models import User
    from werkzeug.security import generate_password_hash
    
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
