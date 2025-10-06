from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    budget = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tasks = relationship("Task", back_populates="project")
    scenes = relationship("Scene", back_populates="project")
    actors = relationship("Actor", back_populates="project")
    properties = relationship("Property", back_populates="project")
    crew_members = relationship("Crew", back_populates="project")
    todos = relationship("ToDo", back_populates="project")
    schedule_entries = relationship("ScheduleEntry", back_populates="project")
    reminders = relationship("Reminder", back_populates="project")
    scripts = relationship("Script", back_populates="project", order_by="desc(Script.uploaded_at)")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    supabase_id = Column(String, unique=True, index=True, nullable=True)
    is_admin = Column(Boolean, default=False)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Crew(Base):
    __tablename__ = "crews"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    tasks = relationship("Task", back_populates="crew")
    project = relationship("Project", back_populates="crew_members")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))
    crew_id = Column(Integer, ForeignKey("crews.id"))
    project = relationship("Project", back_populates="tasks")
    crew = relationship("Crew", back_populates="tasks")


class Finance(Base):
    __tablename__ = "finances"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    amount_spent = Column(Float)
    description = Column(String)


class Script(Base):
    __tablename__ = "scripts"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String)
    filepath = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", back_populates="scripts")


class Scene(Base):
    __tablename__ = "scenes"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True)
    index = Column(Integer)
    heading = Column(String)
    description = Column(Text)
    word_count = Column(Integer, default=0)
    predicted_budget = Column(Float, default=0.0)
    suggested_location = Column(String, nullable=True)
    progress_status = Column(String, default="todo")  # todo, in_progress, done
    assigned_crew_id = Column(Integer, ForeignKey("crews.id"), nullable=True)
    project = relationship("Project", back_populates="scenes")


class ToDo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    is_post_production = Column(Boolean, default=False)
    status = Column(String, default="pending")
    assigned_crew_id = Column(Integer, ForeignKey("crews.id"), nullable=True)
    project = relationship("Project", back_populates="todos")


class Actor(Base):
    __tablename__ = "actors"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    cost = Column(Float, default=0.0)
    payment_due = Column(String, nullable=True)
    project = relationship("Project", back_populates="actors")


class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    cost = Column(Float, default=0.0)
    project = relationship("Project", back_populates="properties")


class ScheduleEntry(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    task = Column(String)
    dates_json = Column(Text)  # JSON string of dates
    project = relationship("Project", back_populates="schedule_entries")


class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    remind_date = Column(String)
    message = Column(String)
    sent = Column(Boolean, default=False)
    project = relationship("Project", back_populates="reminders")


class GlobalScript(Base):
    __tablename__ = "global_scripts"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
