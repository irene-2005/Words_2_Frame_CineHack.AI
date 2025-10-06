from typing import Any

from fastapi import Body, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
import joblib
from pathlib import Path, Path as _Path
import uvicorn
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app import ai_integration, auth, auth_supabase, schemas
from app.crud import crud
from app.database.database import Base, SessionLocal, engine
from app.services.project_snapshot import build_project_snapshot, build_project_reports
from app.models.models import Project

# Ensure all tables exist
Base.metadata.create_all(bind=engine)


def _ensure_script_filepath_column() -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("scripts")}
    if "filepath" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE scripts ADD COLUMN filepath VARCHAR"))


_ensure_script_filepath_column()

app = FastAPI(title="CineHack Backend - Irene (backend)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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


def _has_project_access(user: Any, project: Project) -> bool:
    if getattr(user, "is_admin", False):
        return True
    if project.owner_id is None:
        return True
    return getattr(user, "id", None) == project.owner_id


def ensure_project_edit_access(user: Any, project: Project) -> None:
    if not _has_project_access(user, project):
        raise HTTPException(status_code=403, detail="User is not permitted to modify this project")


def ensure_project_view_access(user: Any, project: Project) -> None:
    if not _has_project_access(user, project):
        raise HTTPException(status_code=403, detail="User is not permitted to view this project")

# ---------- Root endpoint ----------
@app.get("/", tags=["root"])
def read_root():
    return {"status": "ok", "message": "CineHack backend running. Open /docs for interactive API docs."}

# ---------- Project endpoints ----------
@app.post("/projects/", response_model=schemas.ProjectRead)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    user=Depends(auth_supabase.get_current_user_from_supabase),
):
    project = crud.create_project(
        db,
        name=payload.name,
        description=payload.description,
        budget=payload.budget,
        owner_id=getattr(user, "id", None),
    )
    crud.ensure_default_crew(db, project.id)
    return project


# Upload script file (client should save file on server and provide path) -- for hackathon, accept filename and assume file placed in ./uploads
@app.post("/projects/{project_id}/upload_script", response_model=schemas.ScriptRead)
async def upload_script(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    ensure_project_edit_access(user, project)
    uploads = Path.cwd() / 'uploads'
    uploads.mkdir(exist_ok=True)
    # sanitize filename
    filename = Path(file.filename).name
    filepath = uploads / filename
    # save uploaded file
    with open(filepath, 'wb') as out_f:
        content = await file.read()
        out_f.write(content)
    # Also save to global scripts
    content_str = content.decode('utf-8', errors='ignore')
    crud.create_global_script(db, filename=filename, content=content_str, uploaded_by=getattr(user, "id", None))
    return crud.create_script(db, project_id=project_id, filename=filename, filepath=str(filepath))


# Trigger AI analysis of an uploaded script
@app.post("/projects/{project_id}/analyze_script")
def analyze_script(project_id: int, filename: str = Body(..., embed=True), db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    uploads = Path.cwd() / 'uploads'
    filepath = uploads / filename
    if not filepath.exists():
        raise HTTPException(status_code=400, detail="Uploaded script file not found on server uploads/ directory")
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    ensure_project_edit_access(user, project)
    try:
        analysis = ai_integration.analyze_and_create(db, project_id=project_id, script_path=str(filepath))
    except ai_integration.ScriptExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    snapshot = build_project_snapshot(db, project)
    response_payload = {**analysis, "snapshot": snapshot}
    # Maintain backwards compatibility with legacy clients expecting created_scenes key
    response_payload.setdefault("created_scenes", analysis.get("created_scene_metadata", []))
    return response_payload


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


@app.get("/projects/{project_id}/snapshot", response_model=schemas.ProjectSnapshot)
def get_project_snapshot(project_id: int, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    ensure_project_view_access(user, project)
    snapshot = build_project_snapshot(db, project)
    return snapshot


@app.get("/projects/{project_id}/reports")
def get_project_reports(project_id: int, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    ensure_project_view_access(user, project)
    return build_project_reports(db, project)


@app.get("/projects/default", response_model=schemas.ProjectRead)
def get_default_project(db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    project = crud.get_or_create_default_project(db, user)
    return project


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

# ---------- Reports endpoints ----------
@app.get("/projects/{project_id}/reports")
def get_project_reports(project_id: int, db: Session = Depends(get_db), user = Depends(auth_supabase.get_current_user_from_supabase)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    ensure_project_view_access(user, project)
    
    # Aggregate data for reports
    scenes = crud.get_scenes_by_project(db, project_id)
    budget = crud.calculate_project_budget(db, project_id)
    crew = crud.get_crew_by_project(db, project_id)
    tasks = crud.get_tasks_by_project(db, project_id)
    finances = crud.get_finances_by_project(db, project_id)
    
    total_spent = sum(f.amount_spent for f in finances)
    remaining_budget = budget - total_spent
    
    report = {
        "project": project.name,
        "total_scenes": len(scenes),
        "total_budget": budget,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "crew_count": len(crew),
        "tasks_count": len(tasks),
        "budget_breakdown": crud.get_budget_per_scene(db, project_id),
        "location_summary": list(crud.summarise_locations(scenes)),
        "completion_status": crud.get_project_completion_status(db, project_id)
    }
    return report

# ---------- Run server ----------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
