#!/usr/bin/env python3
"""Create test admin and regular users"""

import sys
sys.path.insert(0, ".")

from app import app, db, User, hash_password

with app.app_context():
    # Create admin user
    admin = User(
        username="admin",
        password_hash=hash_password("Admin123!@#"),
        is_admin=True,
        password_purpose="Admin Account"
    )
    db.session.add(admin)
    
    # Create regular user
    user = User(
        username="testuser",
        password_hash=hash_password("TestUser123!@#"),
        is_admin=False,
        password_purpose="Gmail"
    )
    db.session.add(user)
    
    db.session.commit()
    print("✅ Admin user created: admin / Admin123!@#")
    print("✅ Test user created: testuser / TestUser123!@#")
