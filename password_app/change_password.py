#!/usr/bin/env python3
"""Change a user's password"""

import sys
sys.path.insert(0, ".")

from app import app, db, User, hash_password

def change_password(username, new_password):
    """Change password for a user"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found.")
            return False
        
        user.password_hash = hash_password(new_password)
        db.session.commit()
        print(f"✅ Password for '{username}' changed successfully!")
        print(f"   New password: {new_password}")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python change_password.py <username> <new_password>")
        print("Example: python change_password.py admin MyNewPass123!@#")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    change_password(username, new_password)
