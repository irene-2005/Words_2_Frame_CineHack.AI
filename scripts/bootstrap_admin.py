#!/usr/bin/env python
"""Bootstrap or mark a user as admin.

Usage:
    python scripts/bootstrap_admin.py --username director
    python scripts/bootstrap_admin.py --supabase-id <id>
"""
import argparse
from app.database.database import SessionLocal, engine, Base
from app.models.models import User
from app.crud import crud


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', help='username to mark as admin')
    parser.add_argument('--supabase-id', dest='supabase_id', help='supabase_id to mark as admin')
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.username:
            u = db.query(User).filter(User.username == args.username).first()
        elif args.supabase_id:
            u = db.query(User).filter(User.supabase_id == args.supabase_id).first()
        else:
            print('Provide --username or --supabase-id')
            return
        if not u:
            print('User not found')
            return
        u.is_admin = True
        db.commit()
        print(f'User {u.username} marked as admin')
    finally:
        db.close()

if __name__ == '__main__':
    # ensure tables
    Base.metadata.create_all(bind=engine)
    main()
