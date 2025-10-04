from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uvicorn

from app.database.database import SessionLocal, engine, Base
from app.models.models import Project, Crew, Task, Finance
from app.crud import crud
from app import schemas

# Ensure all tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CineHack Backend - Irene (backend)")

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
