# app/crud/crud.py
from sqlalchemy.orm import Session
from app.models.models import Project, Crew, Task, Finance
from app.models.models import User, Script, Scene, ToDo, Actor, Property, ScheduleEntry, Reminder

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


# USER
def create_user(db: Session, username: str, email: str, is_admin: bool = False):
    u = User(username=username, email=email, is_admin=is_admin)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def create_user_with_password(db: Session, username: str, email: str, password: str, is_admin: bool = False):
    # avoid circular import at module load
    from app.auth import get_password_hash
    pw = get_password_hash(password)
    u = User(username=username, email=email, is_admin=is_admin, password_hash=pw)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


# SCRIPTS
def create_script(db: Session, project_id: int, filename: str, filepath: str):
    s = Script(project_id=project_id, filename=filename, filepath=filepath)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# SCENES
def create_scene(db: Session, project_id: int, index: int, heading: str = None, description: str = None):
    s = Scene(project_id=project_id, index=index, heading=heading, description=description)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def get_scenes_by_project(db: Session, project_id: int):
    return db.query(Scene).filter(Scene.project_id == project_id).all()


def get_scene_by_id(db: Session, scene_id: int):
    return db.query(Scene).filter(Scene.id == scene_id).first()


def update_scene(db: Session, scene_id: int, **kwargs):
    scene = get_scene_by_id(db, scene_id)
    if not scene:
        return None
    for k, v in kwargs.items():
        if hasattr(scene, k):
            setattr(scene, k, v)
    db.commit()
    db.refresh(scene)
    return scene


# TODOS
def create_todo(db: Session, project_id: int, title: str, description: str = None, is_post_production: bool = False):
    t = ToDo(project_id=project_id, title=title, description=description, is_post_production=is_post_production)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

def get_todos_by_project(db: Session, project_id: int):
    return db.query(ToDo).filter(ToDo.project_id == project_id).all()


def get_todo_by_id(db: Session, todo_id: int):
    return db.query(ToDo).filter(ToDo.id == todo_id).first()


def update_todo(db: Session, todo_id: int, **kwargs):
    t = get_todo_by_id(db, todo_id)
    if not t:
        return None
    for k, v in kwargs.items():
        if hasattr(t, k):
            setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


def delete_todo(db: Session, todo_id: int):
    t = get_todo_by_id(db, todo_id)
    if not t:
        return False
    db.delete(t)
    db.commit()
    return True


# ACTORS / PROPERTIES
def create_actor(db: Session, project_id: int, name: str, cost: float = 0.0):
    a = Actor(project_id=project_id, name=name, cost=cost)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

def create_property(db: Session, project_id: int, name: str, cost: float = 0.0):
    p = Property(project_id=project_id, name=name, cost=cost)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# SCHEDULE / REMINDERS
def create_schedule_entry(db: Session, project_id: int, task: str, dates_json: str):
    s = ScheduleEntry(project_id=project_id, task=task, dates_json=dates_json)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def create_reminder(db: Session, project_id: int, remind_date: str, message: str):
    r = Reminder(project_id=project_id, remind_date=remind_date, message=message)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def get_schedule_by_project(db: Session, project_id: int):
    return db.query(ScheduleEntry).filter(ScheduleEntry.project_id == project_id).all()


def get_reminders_by_project(db: Session, project_id: int):
    return db.query(Reminder).filter(Reminder.project_id == project_id).all()


def get_actors_by_project(db: Session, project_id: int):
    return db.query(Actor).filter(Actor.project_id == project_id).all()


def get_properties_by_project(db: Session, project_id: int):
    return db.query(Property).filter(Property.project_id == project_id).all()
