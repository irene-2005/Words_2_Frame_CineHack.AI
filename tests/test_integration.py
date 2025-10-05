import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Base, engine, SessionLocal
from app.models.models import User, Project

os.environ['SUPABASE_TESTING'] = '1'

client = TestClient(app)


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # create a project
    db = SessionLocal()
    p = Project(name='Test Project', description='desc', budget=1000000)
    db.add(p)
    db.commit()
    db.close()


def test_upload_and_analyze_flow():
    # create test user via direct DB
    db = SessionLocal()
    u = User(username='testdir', email='dir@example.com', is_admin=True, supabase_id='test:dir@example.com:1')
    db.add(u)
    db.commit()
    db.close()

    token = 'test:dir@example.com:1'
    headers = {'Authorization': f'Bearer {token}'}

    # upload a small script
    resp = client.post('/projects/1/upload_script', headers=headers, files={'file': ('script.txt', 'INT. ROOM\nThis is a test scene.')})
    assert resp.status_code == 200
    j = resp.json()
    assert j['filename'] == 'script.txt'

    # analyze
    resp2 = client.post('/projects/1/analyze_script', headers=headers, json={'filename': 'script.txt'})
    assert resp2.status_code == 200
    created = resp2.json().get('created_scenes')
    assert isinstance(created, list)
    assert len(created) >= 1
