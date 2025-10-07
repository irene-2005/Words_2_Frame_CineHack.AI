"""Utility helpers to transform database rows into frontend-ready payloads."""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from app.crud import crud
from app.models.models import Actor, Crew, Finance, Project, Scene, Script, ToDo


CHARACTER_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]{2,}\b")
LOCATION_SPLIT_PATTERN = re.compile(r"\b(INT\.|EXT\.)\s*(.*)")


@dataclass
class SceneSummary:
    id: int
    index: int
    heading: Optional[str]
    description: Optional[str]
    word_count: int
    predicted_budget: float
    suggested_location: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        location_guess = self.suggested_location
        heading_text = self.heading or f"Scene {self.index}"
        if not location_guess and self.heading:
            match = LOCATION_SPLIT_PATTERN.search(self.heading)
            if match:
                location_guess = match.group(2).strip().title()
        characters = extract_characters(self.description)
        props = extract_props(self.description)
        return {
            "id": self.id,
            "scene": heading_text,
            "index": self.index,
            "location": location_guess or "Unknown",
            "type": derive_scene_type(self.heading),
            "summary": build_scene_summary(self.description),
            "characters": characters,
            "props": props,
            "predictedBudget": float(self.predicted_budget or 0.0),
            "wordCount": self.word_count,
            "progressStatus": "todo",
        }


def extract_characters(description: Optional[str]) -> List[str]:
    if not description:
        return []
    tokens = {token for token in CHARACTER_PATTERN.findall(description)}
    return sorted(tokens)


def extract_props(description: Optional[str]) -> List[str]:
    if not description:
        return []
    props: Counter = Counter()
    for line in description.splitlines():
        if line.isupper() and len(line.split()) <= 4:
            continue
        for match in CHARACTER_PATTERN.findall(line):
            if len(match) > 3 and not match.endswith("S"):
                props[match.title()] += 1
    return [name for name, _ in props.most_common(5)]


def derive_scene_type(heading: Optional[str]) -> Optional[str]:
    if not heading:
        return None
    heading = heading.upper()
    if heading.startswith("INT"):
        return "INT"
    if heading.startswith("EXT"):
        return "EXT"
    return None


def build_scene_summary(description: Optional[str]) -> Optional[str]:
    if not description:
        return None
    clean = " ".join(description.split())
    return clean[:260] + ("..." if len(clean) > 260 else "")


def build_crew_payload(crew: Iterable[Crew]) -> List[Dict[str, Any]]:
    return [
        {
            "id": member.id,
            "name": member.name,
            "role": member.role,
        }
        for member in crew
    ]


def build_budget_payload(scenes: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    per_scene = [
        {
            "scene": scene["scene"],
            "total": scene["predictedBudget"],
        }
        for scene in scenes
    ]
    total = sum(item["total"] for item in per_scene)
    return {
        "total": total,
        "perScene": per_scene,
    }


def build_reports_payload(scenes: List[Dict[str, Any]], actors: Iterable[Actor]) -> Dict[str, Any]:
    locations = {scene["location"] for scene in scenes}
    characters = set()
    for scene in scenes:
        characters.update(scene.get("characters", []))
    most_used = next(iter(characters), None)
    actor_names = [actor.name for actor in actors]
    if actor_names:
        most_used = actor_names[0]
    return {
        "sceneCount": len(scenes),
        "locations": len(locations),
        "characters": len(characters),
        "mostUsedCharacter": most_used,
        "estimatedBudget": f"₹ {int(sum(scene['predictedBudget'] for scene in scenes)):,}",
    }


def build_production_board(scenes: List[Dict[str, Any]], todos: Iterable[ToDo]) -> Dict[str, List[Dict[str, Any]]]:
    board = {
        "Pre-Production": [],
        "Production": [],
        "Post-Production": [],
    }
    for todo in todos:
        bucket = "Post-Production" if todo.is_post_production else "Pre-Production"
        board[bucket].append(
            {
                "id": todo.id,
                "title": todo.title,
                "scene": infer_scene_from_title(todo.title),
                "status": todo.status,
                "assignedTo": None,
            }
        )
    for scene in scenes:
        board["Production"].append(
            {
                "id": f"scene-{scene['id']}",
                "title": scene["scene"],
                "scene": scene["scene"],
                "status": scene.get("progressStatus", "todo"),
                "assignedTo": None,
            }
        )
    return board


def infer_scene_from_title(title: str) -> Optional[str]:
    match = re.search(r"Scene\s+\d+", title, flags=re.IGNORECASE)
    return match.group(0) if match else None


def build_schedule_payload(entries: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    schedule = []
    for entry in entries:
        dates = json.loads(entry["dates_json"] or "[]")
        for date in dates:
            schedule.append(
                {
                    "id": entry["id"],
                    "date": date,
                    "scene": entry["task"],
                    "location": entry.get("location"),
                    "cast": entry.get("cast", []),
                }
            )
    return schedule


def build_script_data(
    project: Project,
    script: Optional[Script],
    scenes: Iterable[Scene],
    todos: Iterable[ToDo],
    crew: Iterable[Crew],
    actors: Iterable[Actor],
    schedule_entries: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    scene_summaries = [
        SceneSummary(
            id=scene.id,
            index=scene.index,
            heading=scene.heading,
            description=scene.description,
            word_count=scene.word_count or 0,
            predicted_budget=scene.predicted_budget or 0.0,
            suggested_location=scene.suggested_location,
        ).to_dict()
        for scene in scenes
    ]
    budget = build_budget_payload(scene_summaries)
    crew_payload = build_crew_payload(crew)
    reports = build_reports_payload(scene_summaries, actors)
    production_board = build_production_board(scene_summaries, todos)
    schedule = build_schedule_payload(schedule_entries)
    uploaded_script = None
    if script:
        uploaded_script = {
            "name": script.filename,
            "id": script.id,
            "uploadedAt": script.uploaded_at.isoformat() if script.uploaded_at else None,
        }
    return {
        "projectId": project.id,
        "uploadedScript": uploaded_script,
        "sceneData": scene_summaries,
        "budget": budget,
        "crew": crew_payload,
        "actors": [
            {
                "id": actor.id,
                "name": actor.name,
                "role": "Cast",
                "cost": actor.cost,
            }
            for actor in actors
        ],
        "scheduleData": schedule,
        "productionBoard": production_board,
        "reports": reports,
    }


def build_project_snapshot(db: Session, project: Project) -> Dict[str, Any]:
    script = crud.get_latest_script(db, project.id)
    scenes = list(crud.get_scenes_by_project(db, project.id))
    todos = list(crud.get_todos_by_project(db, project.id))
    crew = list(crud.get_crews_by_project(db, project.id))
    actors = list(crud.get_actors_by_project(db, project.id))
    schedule_entries = [
        {
            "id": entry.id,
            "dates_json": entry.dates_json,
            "task": entry.task,
        }
        for entry in crud.get_schedule_by_project(db, project.id)
    ]

    script_data = build_script_data(
        project=project,
        script=script,
        scenes=scenes,
        todos=todos,
        crew=crew,
        actors=actors,
        schedule_entries=schedule_entries,
    )

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "budget": project.budget,
        },
        "scriptData": script_data,
    }


def build_project_reports(db: Session, project: Project) -> Dict[str, Any]:
    scenes = list(crud.get_scenes_by_project(db, project.id))
    todos = list(crud.get_todos_by_project(db, project.id))
    crew = list(crud.get_crews_by_project(db, project.id))
    project_tasks = list(crud.get_tasks_by_project(db, project.id))
    finances = db.query(Finance).filter(Finance.project_id == project.id).all()

    total_budget = float(project.budget or 0.0)
    total_spent = sum(float(finance.amount_spent or 0.0) for finance in finances)
    remaining_budget = max(total_budget - total_spent, 0.0)

    tasks_total = len(todos)
    tasks_completed = sum(
        1
        for todo in todos
        if (todo.status or "").strip().lower() in {"done", "complete", "completed"}
    )
    completion_percentage = (
        (tasks_completed / tasks_total) * 100.0 if tasks_total else 0.0
    )

    budget_breakdown = crud.get_budget_per_scene(db, project.id)
    location_summary = list(dict.fromkeys(crud.summarise_locations(scenes)))

    return {
        "project": project.name,
        "total_scenes": len(scenes),
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "crew_count": len(crew),
        "tasks_count": len(project_tasks),
        "budget_breakdown": budget_breakdown,
        "location_summary": location_summary,
        "completion_status": {
            "tasks_total": tasks_total,
            "tasks_completed": tasks_completed,
            "completion_percentage": completion_percentage,
        },
    }
