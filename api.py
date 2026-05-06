"""
DayKeep — FastAPI Backend
Serves all data to the React frontend.
All data persistence still lives in db.py — nothing changes there.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import io
import csv
import datetime

# Import the existing data layer directly
import db
from models import (
    create_goal, create_task, create_journal_entry, create_user_profile, today
)

app = FastAPI(title="DayKeep API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "https://daykeepai.dominioneze.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── HEALTH ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "date": today()}


# ─── USER ─────────────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    name: str
    timezone: Optional[str] = ""

@app.get("/api/user")
def get_user():
    return db.get_user()

@app.put("/api/user")
def save_user(profile: UserProfile):
    from models import create_user_profile
    user, error = create_user_profile(name=profile.name)
    if error:
        raise HTTPException(status_code=400, detail=error)
    db.save_user(user)
    return user


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard():
    """Single call for the home screen — today's summary, upcoming, overdue, endangered streaks."""
    db.check_and_flag_stale_tasks()
    db.auto_generate_routine_tasks()
    summary = db.get_todays_summary()
    tasks_today = db.get_tasks_for_today()
    upcoming = db.get_upcoming_tasks(hours=2)
    overdue = db.get_overdue_tasks()
    endangered = db.get_goals_with_endangered_streaks()
    abandoned = db.get_abandoned_tasks()

    return {
        "summary": summary,
        "tasks_today": tasks_today,
        "upcoming": [{"task": t, "minutes_until": m} for t, m in upcoming],
        "overdue": overdue,
        "endangered_streaks": endangered,
        "abandoned_count": len(abandoned),
    }


# ─── GOALS ────────────────────────────────────────────────────────────────────

class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = ""
    subcategory: Optional[str] = ""
    target_date: Optional[str] = ""
    status: Optional[str] = "Active"
    is_routine: Optional[bool] = False
    routine_time: Optional[str] = ""

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None
    is_routine: Optional[bool] = None
    routine_time: Optional[str] = None

@app.get("/api/goals")
def get_goals():
    return db.get_all_goals()

@app.get("/api/goals/{goal_id}")
def get_goal(goal_id: int):
    goal = db.get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.post("/api/goals", status_code=201)
def create_goal_endpoint(body: GoalCreate):
    goal, error = create_goal(
        title=body.title,
        description=body.description,
        category=body.category,
        subcategory=body.subcategory,
        target_date=body.target_date,
        status=body.status,
        is_routine=body.is_routine,
        routine_time=body.routine_time,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db.add_goal(goal)

@app.put("/api/goals/{goal_id}")
def update_goal(goal_id: int, body: GoalUpdate):
    goal = db.get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    db.update_goal(goal_id, updates)
    return db.get_goal_by_id(goal_id)

@app.delete("/api/goals/{goal_id}")
def delete_goal(goal_id: int):
    if not db.delete_goal(goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"deleted": True}


# ─── TASKS ────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    date: Optional[str] = None          # defaults to today
    category: Optional[str] = ""
    subcategory: Optional[str] = ""
    goal_id: Optional[int] = None
    scheduled_time: Optional[str] = ""
    is_routine: Optional[bool] = False
    status: Optional[str] = "Planned"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    goal_id: Optional[int] = None
    scheduled_time: Optional[str] = None
    is_routine: Optional[bool] = None
    status: Optional[str] = None
    time_spent: Optional[str] = None
    date_completed: Optional[str] = None

class NoteCreate(BaseModel):
    text: str

class PostponeBody(BaseModel):
    new_date: str
    new_time: Optional[str] = ""

@app.get("/api/tasks")
def get_tasks(date: Optional[str] = None):
    if date:
        return db.get_tasks_for_date(date)
    return db.get_all_tasks()

@app.get("/api/tasks/today")
def get_tasks_today():
    db.check_and_flag_stale_tasks()
    return db.get_tasks_for_today()

@app.get("/api/tasks/overdue")
def get_overdue():
    return db.get_overdue_tasks()

@app.get("/api/tasks/upcoming")
def get_upcoming(hours: int = 2):
    result = db.get_upcoming_tasks(hours=hours)
    return [{"task": t, "minutes_until": m} for t, m in result]

@app.get("/api/tasks/abandoned")
def get_abandoned():
    return db.get_abandoned_tasks()

@app.get("/api/tasks/{task_id}")
def get_task(task_id: int):
    task = db.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks", status_code=201)
def create_task_endpoint(body: TaskCreate):
    task_date = body.date or today()
    task, error = create_task(
        title=body.title,
        date=task_date,
        status=body.status,
        category=body.category,
        subcategory=body.subcategory,
        goal_id=body.goal_id,
        scheduled_time=body.scheduled_time,
        is_routine=body.is_routine,
        notes=[],
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db.add_task(task)

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    task = db.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}

    # Auto-set date_completed when marking complete
    if updates.get("status") == "Complete" and not updates.get("date_completed"):
        updates["date_completed"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db.update_task(task_id, updates)

    # If task is linked to a routine goal, update the streak
    updated_task = db.get_task_by_id(task_id)
    if updates.get("status") == "Complete" and updated_task.get("goal_id") and updated_task.get("is_routine"):
        db.update_goal_streak(updated_task["goal_id"])

    return db.get_task_by_id(task_id)

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    if not db.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}

@app.post("/api/tasks/{task_id}/notes", status_code=201)
def add_note(task_id: int, body: NoteCreate):
    if not db.add_note_to_task(task_id, body.text):
        raise HTTPException(status_code=404, detail="Task not found")
    return db.get_task_by_id(task_id)

@app.delete("/api/tasks/{task_id}/notes/{note_index}")
def delete_note(task_id: int, note_index: int):
    if not db.delete_note_from_task(task_id, note_index):
        raise HTTPException(status_code=404, detail="Task or note not found")
    return db.get_task_by_id(task_id)

@app.post("/api/tasks/{task_id}/postpone")
def postpone_task(task_id: int, body: PostponeBody):
    if not db.postpone_task(task_id, body.new_date, body.new_time):
        raise HTTPException(status_code=404, detail="Task not found")
    return db.get_task_by_id(task_id)


# ─── JOURNAL ──────────────────────────────────────────────────────────────────

class JournalCreate(BaseModel):
    text: str
    mood: Optional[int] = None          # 1-5
    season: Optional[str] = ""
    date: Optional[str] = None          # defaults to today

class JournalUpdate(BaseModel):
    text: Optional[str] = None
    mood: Optional[int] = None

@app.get("/api/journal")
def get_journal():
    entries = db.get_all_journal_entries()
    return sorted(entries, key=lambda e: e.get("date", ""), reverse=True)

@app.get("/api/journal/today")
def get_todays_journal():
    entry = db.get_todays_journal_entry()
    return entry or {}

@app.get("/api/journal/{entry_id}")
def get_journal_entry(entry_id: int):
    entry = db.get_journal_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.post("/api/journal", status_code=201)
def create_journal_endpoint(body: JournalCreate):
    entry_date = body.date or today()

    # Don't allow duplicate entries for the same date
    existing = db.get_journal_entry_by_date(entry_date)
    if existing:
        raise HTTPException(status_code=409, detail="Entry for this date already exists. Use PUT to update it.")

    entry, error = create_journal_entry(
        text=body.text,
        mood=body.mood,
        season=body.season,
        date=entry_date,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db.add_journal_entry(entry)

@app.put("/api/journal/{entry_id}")
def update_journal_entry(entry_id: int, body: JournalUpdate):
    entry = db.get_journal_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    db.update_journal_entry(entry_id, updates)
    return db.get_journal_entry_by_id(entry_id)

@app.delete("/api/journal/{entry_id}")
def delete_journal_entry(entry_id: int):
    if not db.delete_journal_entry(entry_id):
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"deleted": True}


# ─── ANALYTICS ────────────────────────────────────────────────────────────────

@app.get("/api/analytics")
def get_analytics():
    return db.get_analytics()


# ─── EXPORT ───────────────────────────────────────────────────────────────────

@app.get("/api/export/tasks")
def export_tasks():
    tasks = db.get_all_tasks()
    fields = [
        "id", "title", "date", "status", "category", "subcategory",
        "scheduled_time", "is_routine", "goal_id", "time_spent",
        "date_completed", "date_created", "last_updated"
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for task in tasks:
        writer.writerow({field: task.get(field, "") for field in fields})

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=daykeep_tasks.csv"}
    )

@app.get("/api/export/goals")
def export_goals():
    goals = db.get_all_goals()
    fields = [
        "id", "title", "status", "category", "subcategory",
        "target_date", "is_routine", "routine_time", "streak",
        "last_streak_date", "description", "date_created", "last_updated"
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for goal in goals:
        writer.writerow({field: goal.get(field, "") for field in fields})

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=daykeep_goals.csv"}
    )
