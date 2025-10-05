import os
import sys
# ensure repo root is importable when running this script directly
sys.path.insert(0, r"c:\Users\athir\Words2Frame\Words_2_Frame_CineHack.AI")
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Base, engine
from app.models.models import User, Project
from app.database.database import SessionLocal

os.environ['SUPABASE_TESTING'] = '1'

Base.metadata.create_all(bind=engine)
# ensure project exists
db = SessionLocal()
if not db.query(Project).filter(Project.id == 1).first():
    p = Project(name='Test Project', description='desc', budget=1000000)
    db.add(p)
    db.commit()
# create user
if not db.query(User).filter(User.supabase_id == 'test:dir@example.com:1').first():
    u = User(username='testdir', email='dir@example.com', is_admin=True, supabase_id='test:dir@example.com:1')
    db.add(u)
    db.commit()
    db.refresh(u)
    print('created user', u.id)

client = TestClient(app)
headers = {'Authorization': 'Bearer test:dir@example.com:1'}
resp = client.post('/projects/1/upload_script', headers=headers, files={'file': ('script.txt', 'INT. ROOM\nThis is a test scene.')})
print('status', resp.status_code)
print('body', resp.text)

if resp.status_code >= 500:
    # get server exceptions if present
    try:
        print('server exc', resp.json())
    except Exception:
        pass
