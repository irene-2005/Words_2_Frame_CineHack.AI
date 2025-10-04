# app/crud/crud.py
from sqlalchemy.orm import Session
from app.models.models import Project, Crew, Task, Finance

# PROJECT
def create_project(db: Session, name: str, description: str, budget: float):
    project = Project(name=name, description=description, budget=budget)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_projects(db: Session):
    return db.query(Project).all()

def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def update_project_budget(db: Session, project_id: int, new_budget: float):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.budget = new_budget
        db.commit()
        db.refresh(project)
    return project

# CREW
def create_crew(db: Session, name: str, role: str):
    crew = Crew(name=name, role=role)
    db.add(crew)
    db.commit()
    db.refresh(crew)
    return crew

def get_crews(db: Session):
    return db.query(Crew).all()

def get_crew_by_id(db: Session, crew_id: int):
    return db.query(Crew).filter(Crew.id == crew_id).first()

# TASK
def create_task(db: Session, title: str, project_id: int, crew_id: int):
    task = Task(title=title, project_id=project_id, crew_id=crew_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks(db: Session):
    return db.query(Task).all()

# FINANCE
def create_finance(db: Session, project_id: int, amount_spent: float, description: str):
    finance = Finance(project_id=project_id, amount_spent=amount_spent, description=description)
    db.add(finance)
    db.commit()
    db.refresh(finance)
    return finance

def get_finances(db: Session):
    return db.query(Finance).all()
