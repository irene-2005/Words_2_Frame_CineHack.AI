# app/schemas.py
from typing import Any, Dict, Optional

from pydantic import BaseModel

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
        from_attributes = True

# Crew
class CrewCreate(BaseModel):
    name: str
    role: Optional[str] = None

class CrewRead(BaseModel):
    id: int
    name: str
    role: Optional[str] = None

    class Config:
        from_attributes = True

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
        from_attributes = True

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
        from_attributes = True


# User
class UserCreate(BaseModel):
    username: str
    email: Optional[str]

class UserCreateWithPassword(UserCreate):
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: Optional[str]
    is_admin: bool

    class Config:
        from_attributes = True


# Auth tokens
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# Script upload / analysis
class ScriptUpload(BaseModel):
    project_id: int
    filename: str

class ScriptRead(BaseModel):
    id: int
    project_id: int
    filename: str

    class Config:
        from_attributes = True


# Scene and Scene analysis
class SceneCreate(BaseModel):
    project_id: int
    index: int
    heading: Optional[str]
    description: Optional[str]

class SceneRead(BaseModel):
    id: int
    project_id: int
    index: int
    heading: Optional[str]
    description: Optional[str]
    word_count: Optional[int]
    predicted_budget: Optional[float]
    suggested_location: Optional[str]
    progress_status: Optional[str]

    class Config:
        from_attributes = True


# ToDo
class ToDoCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    is_post_production: Optional[bool] = False

class ToDoRead(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    is_post_production: bool
    status: str

    class Config:
        from_attributes = True


# Actor / Property
class ActorCreate(BaseModel):
    project_id: int
    name: str
    cost: float = 0.0

class PropertyCreate(BaseModel):
    project_id: int
    name: str
    cost: float = 0.0

class ActorRead(BaseModel):
    id: int
    project_id: int
    name: str
    cost: float

    class Config:
        from_attributes = True

class PropertyRead(BaseModel):
    id: int
    project_id: int
    name: str
    cost: float

    class Config:
        from_attributes = True


# Schedule/Reminder
class ScheduleEntryRead(BaseModel):
    id: int
    project_id: int
    task: str
    dates_json: Optional[str]

    class Config:
        from_attributes = True

class ReminderCreate(BaseModel):
    project_id: int
    remind_date: str
    message: str

class ReminderRead(BaseModel):
    id: int
    project_id: int
    remind_date: str
    message: str
    sent: bool

    class Config:
        from_attributes = True


class ProjectSnapshot(BaseModel):
    project: Dict[str, Any]
    scriptData: Dict[str, Any]

