#!/usr/bin/env python3
"""
Interactive script to set a user's password safely for ArtForge
"""
import sys
import os
sys.path.insert(0, '/app/src')

import bcrypt
from art_forge.database import SessionLocal
from art_forge.models.user import User

def set_password(username, password):
    """Set password for a user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User {username} not found")
            return False
        
        # Use bcrypt directly (ArtForge already uses bcrypt directly)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Store the hash as a string
        user.hashed_password = hashed.decode('utf-8')
        db.commit()
        
        print(f"Password set successfully for user: {user.username}")
        print(f"Password length: {len(password)} characters")
        return True
        
    except Exception as e:
        print(f"Error setting password: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_password_interactive.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    set_password(username, password)
