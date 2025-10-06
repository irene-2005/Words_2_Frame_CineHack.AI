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

    resp_default = client.get('/projects/default', headers=headers)
    assert resp_default.status_code == 200
    default_project = resp_default.json()
    assert default_project['name']

    # upload a small script
    resp = client.post('/projects/1/upload_script', headers=headers, files={'file': ('script.txt', 'INT. ROOM\nThis is a test scene.')})
    assert resp.status_code == 200
    j = resp.json()
    assert j['filename'] == 'script.txt'

    # analyze
    resp2 = client.post('/projects/1/analyze_script', headers=headers, json={'filename': 'script.txt'})
    assert resp2.status_code == 200
    response_payload = resp2.json()
    scenes = response_payload.get('scenes')
    assert isinstance(scenes, list)
    assert len(scenes) >= 1
    assert all({'scene_no', 'location', 'characters', 'time'} <= set(scene.keys()) for scene in scenes)
    assert 'predicted_budget' in response_payload and response_payload['predicted_budget'] >= 0
    assert 'crew_recommendations' in response_payload
    assert isinstance(response_payload.get('created_scenes'), list)
    snapshot = response_payload.get('snapshot')
    assert snapshot and 'project' in snapshot and 'scriptData' in snapshot

    resp3 = client.get('/projects/1/snapshot', headers=headers)
    assert resp3.status_code == 200
    snapshot_payload = resp3.json()
    assert snapshot_payload['project']['id'] == 1
    assert 'sceneData' in snapshot_payload['scriptData']

    resp_reports = client.get('/projects/1/reports', headers=headers)
    assert resp_reports.status_code == 200
    reports_payload = resp_reports.json()
    assert 'total_scenes' in reports_payload
    assert 'completion_status' in reports_payload
    assert isinstance(reports_payload['completion_status'].get('completion_percentage', 0), (int, float))
