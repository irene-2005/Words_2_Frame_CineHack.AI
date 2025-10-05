#!/usr/bin/env python
"""Bootstrap admin from a Supabase token. Supports SUPABASE_TESTING.

Usage:
  python scripts/bootstrap_admin_from_token.py --token "test:dir@example.com:1"
"""
import argparse
import os
import sys
sys.path.insert(0, r"c:\Users\athir\Words2Frame\Words_2_Frame_CineHack.AI")
from app.database.database import SessionLocal, engine, Base
from app.models.models import User
from app.auth_supabase import verify_supabase_token


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', required=True, help='Supabase access token')
    args = parser.parse_args()

    os.environ.setdefault('SUPABASE_TESTING', '1')
    info = verify_supabase_token(args.token)
    supabase_id = info.get('id')
    email = info.get('email')
    username = info.get('user_metadata', {}).get('full_name') or email.split('@')[0]

    db = SessionLocal()
    try:
        u = db.query(User).filter(User.supabase_id == supabase_id).first()
        if not u:
            # try by email
            u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(username=username, email=email, supabase_id=supabase_id, is_admin=True)
            db.add(u)
            db.commit()
            print('Created admin user', username)
            return
        u.is_admin = True
        u.supabase_id = supabase_id
        db.commit()
        print('Marked existing user as admin:', u.username)
    finally:
        db.close()

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    main()
