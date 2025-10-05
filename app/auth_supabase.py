import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import requests
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.crud import crud

# Configure: SUPABASE_URL and SUPABASE_KEY should be provided as env vars in production
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_supabase_token(token: str):
    # Testing mode: accept a simple token format and return synthetic user info
    if os.environ.get('SUPABASE_TESTING'):
        # token format: test:<email>:<id>
        if token.startswith('test:'):
            parts = token.split(':', 2)
            if len(parts) == 3:
                # return the full token as the supabase id so it maps to created test users
                return {'id': token, 'email': parts[1], 'user_metadata': {'full_name': parts[1].split('@')[0]}}
        # otherwise treat token as email and use token string as id
        return {'id': token, 'email': token, 'user_metadata': {'full_name': token.split('@')[0]}}

    # Use the Supabase userinfo endpoint
    if not SUPABASE_URL:
        raise HTTPException(status_code=500, detail="SUPABASE_URL not configured on server")
    url = f"{SUPABASE_URL}/auth/v1/user"
    headers = {"Authorization": f"Bearer {token}", "apikey": SUPABASE_KEY or ""}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Supabase token")
    return r.json()


def get_current_user_from_supabase(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    info = verify_supabase_token(token)
    # info contains 'id' and 'email' among others
    supabase_id = info.get('id')
    email = info.get('email')
    username = info.get('user_metadata', {}).get('full_name') or email.split('@')[0]
    # map to local user; create if missing
    user = db.query.__self__
    from app.models.models import User as UserModel
    u = db.query(UserModel).filter(UserModel.supabase_id == supabase_id).first()
    if not u:
        # create local user
        u = crud.create_user(db, username=username, email=email)
        # patch supabase_id
        u.supabase_id = supabase_id
        db.commit()
        db.refresh(u)
    return u
