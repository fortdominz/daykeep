"""
DayKeep — FastAPI Backend
Serves all data to the React frontend.
All data persistence still lives in db.py — nothing changes there.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
import csv
import datetime

import db
from models import today, now, check_date_format

app = FastAPI(title="DayKeep API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:4173",
        "https://daykeepai.dominioneze.dev",
    ],
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

@app.get("/api/user")
def get_user():
    return db.get_user()

@app.put("/api/user")
def save_user(profile: UserProfile):
    if not profile.name.strip():
        raise HTTPException(status_code=400, detail="Name is required.")
    user = {
        "name": profile.name.strip(),
        "date_created": now(),
    }
    db.save_user(user)
    return user


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard():
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
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Title is required.")
    if body.target_date and not check_date_format(body.target_date):
        raise HTTPException(status_code=400, detail="Target date must be YYYY-MM-DD.")
    goal = {
        "id": None,
        "title": body.title.strip(),
        "description": (body.description or "").strip(),
        "category": (body.category or "").strip(),
        "subcategory": (body.subcategory or "").strip(),
        "target_date": (body.target_date or "").strip(),
        "status": body.status or "Active",
        "is_routine": body.is_routine or False,
        "routine_time": (body.routine_time or "").strip(),
        "streak": 0,
        "last_streak_date": "",
        "date_created": now(),
        "last_updated": now(),
    }
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

VALID_STATUSES = ["Planned", "Complete", "Incomplete", "Skipped", "Postponed", "Abandoned: needs update"]

class TaskCreate(BaseModel):
    title: str
    date: Optional[str] = None
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
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Title is required.")
    task_date = body.date or today()
    if not check_date_format(task_date):
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD.")
    task = {
        "id": None,
        "title": body.title.strip(),
        "date": task_date,
        "category": (body.category or "").strip(),
        "subcategory": (body.subcategory or "").strip(),
        "goal_id": body.goal_id,
        "scheduled_time": (body.scheduled_time or "").strip(),
        "is_routine": body.is_routine or False,
        "status": body.status or "Planned",
        "time_spent": "",
        "notes": [],
        "postpone_history": [],
        "date_completed": "",
        "date_created": now(),
        "last_updated": now(),
    }
    return db.add_task(task)

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    task = db.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}

    if updates.get("status") == "Complete" and not task.get("date_completed"):
        updates["date_completed"] = now()

    db.update_task(task_id, updates)

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
# NOTE: The models.py function stores journal text as "content" (not "text").
# Mood is stored as a string "1"–"5" to match MOOD_LABELS keys in models.py.

class JournalCreate(BaseModel):
    text: str           # frontend sends "text"; we store as "content"
    mood: Optional[int] = None
    date: Optional[str] = None

class JournalUpdate(BaseModel):
    text: Optional[str] = None
    mood: Optional[int] = None

@app.get("/api/journal")
def get_journal():
    entries = db.get_all_journal_entries()
    return sorted(entries, key=lambda e: e.get("date", ""), reverse=True)

@app.get("/api/journal/today")
def get_todays_journal():
    # Returns ALL entries for today (multiple allowed)
    all_entries = db.get_all_journal_entries()
    today_str = today()
    return [e for e in all_entries if e.get("date") == today_str]

@app.get("/api/journal/{entry_id}")
def get_journal_entry(entry_id: int):
    entry = db.get_journal_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.post("/api/journal", status_code=201)
def create_journal_endpoint(body: JournalCreate):
    entry_date = body.date or today()

    if not check_date_format(entry_date):
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD.")

    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Entry cannot be empty.")

    # mood stored as string to match MOOD_LABELS keys ("1"–"5")
    mood_str = str(body.mood) if body.mood else ""

    entry = {
        "id": None,
        "date": entry_date,
        "content": body.text.strip(),   # stored as "content" per models.py
        "mood": mood_str,
        "date_created": now(),
        "last_updated": now(),
        "update_history": [],
    }
    return db.add_journal_entry(entry)

@app.put("/api/journal/{entry_id}")
def update_journal_entry(entry_id: int, body: JournalUpdate):
    entry = db.get_journal_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    updates = {}
    if body.text is not None:
        updates["content"] = body.text.strip()   # update "content", not "text"
    if body.mood is not None:
        updates["mood"] = str(body.mood)         # store as string

    if updates:
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
