from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    budget = Column(Float)
    tasks = relationship("Task", back_populates="project")

class Crew(Base):
    __tablename__ = "crews"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    tasks = relationship("Task", back_populates="crew")

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
