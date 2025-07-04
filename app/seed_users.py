import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models import User
from app.database import db

def seed_users():
    """Function to insert test users into the database"""
    
    # Test users list
    test_users = [
        {
            'name': 'Juan Pérez',
            'email': 'juan@ejemplo.com',
            'password': 'password123'
        },
        {
            'name': 'María García',
            'email': 'maria@ejemplo.com',
            'password': 'password123'
        },
        {
            'name': 'Carlos López',
            'email': 'carlos@ejemplo.com',
            'password': 'password123'
        }
    ]
    
    with app.app_context():
        # Check if users already exist
        existing_users = User.query.all()
        if existing_users:
            print(f"Already exist {len(existing_users)} users in the database.")
            print("Existing users:")
            for user in existing_users:
                print(f"- {user.name} ({user.email})")
            return
        
        # Create test users
        created_users = []
        for user_data in test_users:
            user = User(
                name=user_data['name'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            
            db.session.add(user)
            created_users.append(user)
        
        # Save to database
        db.session.commit()
        
        print("✅ Test users created successfully:")
        for user in created_users:
            print(f"- {user.name} ({user.email}) - ID: {user.id}")
        
        print("\n📝 Access credentials:")
        print("Email: juan@ejemplo.com | Password: password123")
        print("Email: maria@ejemplo.com | Password: password123")
        print("Email: carlos@ejemplo.com | Password: password123")

if __name__ == "__main__":
    seed_users() 