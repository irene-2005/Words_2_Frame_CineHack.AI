# app/schemas.py
from pydantic import BaseModel
from typing import Optional

# Project
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    budget: Optional[float] = 0.0

class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    budget: Optional[float] = 0.0

    class Config:
        orm_mode = True

# Crew
class CrewCreate(BaseModel):
    name: str
    role: Optional[str] = None

class CrewRead(BaseModel):
    id: int
    name: str
    role: Optional[str] = None

    class Config:
        orm_mode = True

# Task
class TaskCreate(BaseModel):
    title: str
    project_id: int
    crew_id: int

class TaskRead(BaseModel):
    id: int
    title: str
    project_id: int
    crew_id: int

    class Config:
        orm_mode = True

# Finance
class FinanceCreate(BaseModel):
    project_id: int
    amount_spent: float
    description: Optional[str] = None

class FinanceRead(BaseModel):
    id: int
    project_id: int
    amount_spent: float
    description: Optional[str] = None

    class Config:
        orm_mode = True

