from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uvicorn

from app.database.database import SessionLocal, engine, Base
from app.models.models import Project, Crew, Task, Finance
from app.crud import crud
from app import schemas
from app import auth
from app import auth_supabase
from fastapi import UploadFile, File, Body
from pathlib import Path
from app import ai_integration
import json
from pathlib import Path as _Path
import joblib

# Ensure all tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CineHack Backend - Irene (backend)")
from app import worker


@app.on_event("startup")
def startup_event():
    try:
        worker.start_worker()
    except Exception:
        pass


@app.on_event("shutdown")
def shutdown_event():
    try:
        worker.stop_worker()
    except Exception:
        pass

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Root endpoint ----------
@app.get("/", tags=["root"])
def read_root():
    return {"status": "ok", "message": "CineHack backend running. Open /docs for interactive API docs."}

# ---------- Project endpoints ----------
@app.post("/projects/", response_model=schemas.ProjectRead)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, name=payload.name, description=payload.description, budget=payload.budget)


# Upload script file (client should save file on server and provide path) -- for hackathon, accept filename and assume file placed in ./uploads
@app.post("/projects/{project_id}/upload_script", response_model=schemas.ScriptRead)
async def upload_script(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    uploads = Path.cwd() / 'uploads'
    uploads.mkdir(exist_ok=True)
    # sanitize filename
    filename = Path(file.filename).name
    filepath = uploads / filename
    # save uploaded file
    with open(filepath, 'wb') as out_f:
        content = await file.read()
        out_f.write(content)
    # require admin in local mapping
    if not getattr(user, 'is_admin', False):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    return crud.create_script(db, project_id=project_id, filename=filename, filepath=str(filepath))


# Trigger AI analysis of an uploaded script
@app.post("/projects/{project_id}/analyze_script")
def analyze_script(project_id: int, filename: str = Body(..., embed=True), db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    uploads = Path.cwd() / 'uploads'
    filepath = uploads / filename
    if not filepath.exists():
        raise HTTPException(status_code=400, detail="Uploaded script file not found on server uploads/ directory")
    if not getattr(user, 'is_admin', False):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    created = ai_integration.analyze_and_create(db, project_id=project_id, script_path=str(filepath))
    return {"created_scenes": created}


# User management
@app.post("/users/", response_model=schemas.UserRead)
def create_user(payload: schemas.UserCreateWithPassword, db: Session = Depends(get_db)):
    return crud.create_user_with_password(db, username=payload.username, email=payload.email, password=payload.password, is_admin=False)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: dict, db: Session = Depends(get_db)):
    # form_data should contain username and password
    username = form_data.get('username')
    password = form_data.get('password')
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")
    from app.models.models import User as UserModel
    u = db.query(UserModel).filter(UserModel.username == username).first()
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not auth.verify_password(password, u.password_hash or ""):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": u.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Scenes listing
@app.get("/projects/{project_id}/scenes", response_model=list[schemas.SceneRead])
def get_scenes(project_id: int, db: Session = Depends(get_db)):
    return crud.get_scenes_by_project(db, project_id)


@app.post("/projects/{project_id}/assign_tasks_ai")
def assign_tasks_ai(project_id: int, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    # require admin
    if not getattr(user, 'is_admin', False):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    # load task assigner model if present
    model_path = _Path.cwd() / 'ai' / 'models' / 'task_assigner.pkl'
    if model_path.exists():
        try:
            model = joblib.load(model_path)
        except Exception:
            model = None
    else:
        model = None

    scenes = crud.get_scenes_by_project(db, project_id)
    crews = crud.get_crews(db)
    crew_names = [c.name for c in crews]
    assignments = []
    for s in scenes:
        # simple features
        X = [[s.word_count or 0, 0.1, 1]]
        assigned = None
        if model is not None:
            try:
                pred = model.predict(X)
                idx = int(pred[0]) % max(1, len(crew_names))
                assigned = crew_names[idx]
            except Exception:
                assigned = crew_names[0] if crew_names else None
        else:
            assigned = crew_names[0] if crew_names else None
        assignments.append({'scene_id': s.id, 'assigned': assigned})
    return {'assignments': assignments}


@app.put("/todos/{todo_id}", response_model=schemas.ToDoRead)
def update_todo(todo_id: int, payload: dict, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    # allow director (admin) or assigned crew to update
    t = crud.get_todo_by_id(db, todo_id)
    if not t:
        raise HTTPException(status_code=404, detail='ToDo not found')
    if not getattr(user, 'is_admin', False):
        # no further checks for now
        pass
    updated = crud.update_todo(db, todo_id, **payload)
    return updated


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    if not getattr(user, 'is_admin', False):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    ok = crud.delete_todo(db, todo_id)
    return {"deleted": ok}


@app.put("/scenes/{scene_id}", response_model=schemas.SceneRead)
def update_scene(scene_id: int, payload: dict, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    s = crud.get_scene_by_id(db, scene_id)
    if not s:
        raise HTTPException(status_code=404, detail='Scene not found')
    if not getattr(user, 'is_admin', False):
        pass
    updated = crud.update_scene(db, scene_id, **payload)
    return updated


@app.post("/projects/{project_id}/reminders")
def create_reminder(project_id: int, payload: schemas.ReminderCreate, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    if not getattr(user, 'is_admin', False):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    r = crud.create_reminder(db, project_id=project_id, remind_date=payload.remind_date, message=payload.message)
    return r


@app.get("/projects/{project_id}/calendar")
def get_calendar(project_id: int, db: Session = Depends(get_db)):
    schedules = crud.get_schedule_by_project(db, project_id)
    reminders = crud.get_reminders_by_project(db, project_id)
    return {"schedules": [ {"task": s.task, "dates": json.loads(s.dates_json or '[]')} for s in schedules], "reminders": [ {"date": r.remind_date, "message": r.message} for r in reminders]}


@app.get("/projects/{project_id}/budget_alert")
def budget_alert(project_id: int, db: Session = Depends(get_db)):
    # reuse budget_status computation
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scenes = crud.get_scenes_by_project(db, project_id)
    actors = crud.get_actors_by_project(db, project_id)
    props = crud.get_properties_by_project(db, project_id)
    scene_total = sum((s.predicted_budget or 0.0) for s in scenes)
    actor_total = sum((a.cost or 0.0) for a in actors)
    prop_total = sum((p.cost or 0.0) for p in props)
    total = scene_total + actor_total + prop_total
    exceeded = total > (project.budget or 0.0)
    return {"exceeded": exceeded, "project_budget": project.budget, "estimated_total": total}


# ToDos
@app.post("/projects/{project_id}/todos", response_model=schemas.ToDoRead)
def add_todo(project_id: int, payload: schemas.ToDoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, project_id=project_id, title=payload.title, description=payload.description, is_post_production=payload.is_post_production)

@app.get("/projects/{project_id}/todos", response_model=list[schemas.ToDoRead])
def list_todos(project_id: int, db: Session = Depends(get_db)):
    return crud.get_todos_by_project(db, project_id)


# Actors / Properties
@app.post("/projects/{project_id}/actors", response_model=schemas.ActorRead)
def add_actor(project_id: int, payload: schemas.ActorCreate, db: Session = Depends(get_db)):
    return crud.create_actor(db, project_id=project_id, name=payload.name, cost=payload.cost)

@app.post("/projects/{project_id}/properties", response_model=schemas.PropertyRead)
def add_property(project_id: int, payload: schemas.PropertyCreate, db: Session = Depends(get_db)):
    return crud.create_property(db, project_id=project_id, name=payload.name, cost=payload.cost)


# Create schedule entry
@app.post("/projects/{project_id}/schedule")
def create_schedule(project_id: int, payload: dict, db: Session = Depends(get_db)):
    # payload expected: {task: str, dates: ["YYYY-MM-DD", ...]}
    dates_json = json.dumps(payload.get('dates', []))
    entry = crud.create_schedule_entry(db, project_id=project_id, task=payload.get('task', ''), dates_json=dates_json)
    return {"id": entry.id}


# Budget check: compute sum of predicted scene budgets + actor/property costs and compare to project budget
@app.get("/projects/{project_id}/budget_status")
def budget_status(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scenes = crud.get_scenes_by_project(db, project_id)
    actors = crud.get_actors_by_project(db, project_id)
    props = crud.get_properties_by_project(db, project_id)
    scene_total = sum((s.predicted_budget or 0.0) for s in scenes)
    actor_total = sum((a.cost or 0.0) for a in actors)
    prop_total = sum((p.cost or 0.0) for p in props)
    total = scene_total + actor_total + prop_total
    over = total > (project.budget or 0.0)
    return {"project_budget": project.budget, "estimated_total": total, "over_budget": over}

@app.get("/projects/", response_model=list[schemas.ProjectRead])
def read_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)

@app.get("/projects/{project_id}", response_model=schemas.ProjectRead)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}/budget", response_model=schemas.ProjectRead)
def update_project_budget(project_id: int, new_budget: float, db: Session = Depends(get_db)):
    project = crud.update_project_budget(db, project_id, new_budget)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# ---------- Crew endpoints ----------
@app.post("/crews/", response_model=schemas.CrewRead)
def create_crew(payload: schemas.CrewCreate, db: Session = Depends(get_db)):
    return crud.create_crew(db, name=payload.name, role=payload.role)

@app.get("/crews/", response_model=list[schemas.CrewRead])
def read_crews(db: Session = Depends(get_db)):
    return crud.get_crews(db)

# ---------- Task endpoints ----------
@app.post("/tasks/", response_model=schemas.TaskRead)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    if not crud.get_project_by_id(db, payload.project_id):
        raise HTTPException(status_code=400, detail="Project does not exist")
    if not crud.get_crew_by_id(db, payload.crew_id):
        raise HTTPException(status_code=400, detail="Crew does not exist")
    return crud.create_task(db, title=payload.title, project_id=payload.project_id, crew_id=payload.crew_id)

@app.get("/tasks/", response_model=list[schemas.TaskRead])
def read_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)

# ---------- Finance endpoints ----------
@app.post("/finances/", response_model=schemas.FinanceRead)
def create_finance(payload: schemas.FinanceCreate, db: Session = Depends(get_db)):
    if not crud.get_project_by_id(db, payload.project_id):
        raise HTTPException(status_code=400, detail="Project does not exist")
    return crud.create_finance(db, project_id=payload.project_id, amount_spent=payload.amount_spent, description=payload.description)

@app.get("/finances/", response_model=list[schemas.FinanceRead])
def read_finances(db: Session = Depends(get_db)):
    return crud.get_finances(db)

# ---------- Run server ----------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
