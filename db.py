# db.py — DayKeep
# All data storage lives here. This is the only file that reads and writes to daykeep.json.
# Every other file calls functions from here — nothing touches the file directly.
# This isolation means when we migrate to MongoDB later, only this file changes.

import json
import os
import datetime

from models import today


# ─── SETUP ────────────────────────────────────────────────────────────────────

# The name of the file where all data is stored
DATA_FILE = "daykeep.json"

# The structure of the data file — three separate lists, one per data type
EMPTY_DATA = {
    "goals": [],
    "tasks": [],
    "journal": [],
}


# ─── CORE STORAGE ─────────────────────────────────────────────────────────────

def load_data():
    # Reads the data file and returns everything in it.
    # If the file doesn't exist yet, returns the empty structure.
    if not os.path.exists(DATA_FILE):
        return EMPTY_DATA.copy()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    # Writes the full data dictionary back to the file.
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─── ID HELPERS ───────────────────────────────────────────────────────────────

def get_next_id(records):
    # Takes a list of records and returns the next available ID.
    # If the list is empty, starts at 1.
    if not records:
        return 1
    return max(record["id"] for record in records) + 1


# ─── GOALS ────────────────────────────────────────────────────────────────────

def get_all_goals():
    # Returns the full list of goals.
    data = load_data()
    return data["goals"]


def get_goal_by_id(goal_id):
    # Returns a single goal by its ID, or None if not found.
    goals = get_all_goals()
    for goal in goals:
        if goal["id"] == goal_id:
            return goal
    return None


def add_goal(goal):
    # Assigns an ID to the goal and saves it.
    # Returns the saved goal.
    data = load_data()
    goal["id"] = get_next_id(data["goals"])
    data["goals"].append(goal)
    save_data(data)
    return goal


def update_goal(goal_id, updated_fields):
    # Finds the goal with the given ID and updates only the fields provided.
    # Returns True if the goal was found and updated, False if not found.
    data = load_data()
    for i, goal in enumerate(data["goals"]):
        if goal["id"] == goal_id:
            for field, value in updated_fields.items():
                data["goals"][i][field] = value
            data["goals"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            return True
    return False


def delete_goal(goal_id):
    # Removes the goal with the given ID.
    # Returns True if deleted, False if not found.
    data = load_data()
    original_count = len(data["goals"])
    data["goals"] = [g for g in data["goals"] if g["id"] != goal_id]
    if len(data["goals"]) < original_count:
        save_data(data)
        return True
    return False


# ─── TASKS ────────────────────────────────────────────────────────────────────

def get_all_tasks():
    # Returns the full list of tasks.
    data = load_data()
    return data["tasks"]


def get_tasks_for_date(date_string):
    # Returns all tasks for a specific date (YYYY-MM-DD).
    tasks = get_all_tasks()
    return [t for t in tasks if t["date"] == date_string]


def get_tasks_for_today():
    # Returns all tasks for today.
    return get_tasks_for_date(today())


def get_task_by_id(task_id):
    # Returns a single task by its ID, or None if not found.
    tasks = get_all_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def add_task(task):
    # Assigns an ID to the task and saves it.
    # Returns the saved task.
    data = load_data()
    task["id"] = get_next_id(data["tasks"])
    data["tasks"].append(task)
    save_data(data)
    return task


def update_task(task_id, updated_fields):
    # Finds the task with the given ID and updates only the fields provided.
    # Returns True if found and updated, False if not found.
    data = load_data()
    for i, task in enumerate(data["tasks"]):
        if task["id"] == task_id:
            for field, value in updated_fields.items():
                data["tasks"][i][field] = value
            data["tasks"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            return True
    return False


def delete_task(task_id):
    # Removes the task with the given ID.
    # Returns True if deleted, False if not found.
    data = load_data()
    original_count = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    if len(data["tasks"]) < original_count:
        save_data(data)
        return True
    return False


# ─── JOURNAL ──────────────────────────────────────────────────────────────────

def get_all_journal_entries():
    # Returns the full list of journal entries.
    data = load_data()
    return data["journal"]


def get_journal_entry_by_date(date_string):
    # Returns the journal entry for a specific date, or None if none exists.
    # Only one entry per day is allowed.
    entries = get_all_journal_entries()
    for entry in entries:
        if entry["date"] == date_string:
            return entry
    return None


def get_todays_journal_entry():
    # Returns today's journal entry, or None if none exists yet.
    return get_journal_entry_by_date(today())


def get_journal_entry_by_id(entry_id):
    # Returns a single journal entry by its ID, or None if not found.
    entries = get_all_journal_entries()
    for entry in entries:
        if entry["id"] == entry_id:
            return entry
    return None


def add_journal_entry(entry):
    # Assigns an ID to the entry and saves it.
    # Returns the saved entry.
    data = load_data()
    entry["id"] = get_next_id(data["journal"])
    data["journal"].append(entry)
    save_data(data)
    return entry


def update_journal_entry(entry_id, updated_fields):
    # Finds the entry with the given ID and updates only the fields provided.
    # Returns True if found and updated, False if not found.
    data = load_data()
    for i, entry in enumerate(data["journal"]):
        if entry["id"] == entry_id:
            for field, value in updated_fields.items():
                data["journal"][i][field] = value
            data["journal"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            return True
    return False


def delete_journal_entry(entry_id):
    # Removes the journal entry with the given ID.
    # Returns True if deleted, False if not found.
    data = load_data()
    original_count = len(data["journal"])
    data["journal"] = [e for e in data["journal"] if e["id"] != entry_id]
    if len(data["journal"]) < original_count:
        save_data(data)
        return True
    return False


# ─── ACCOUNTABILITY HELPERS ───────────────────────────────────────────────────

def get_completion_rate(date_string):
    # Returns the completion rate for a specific day as a percentage.
    # Only counts tasks that were Planned, Complete, Incomplete, or Skipped.
    # Returns 0 if there are no tasks for that day.
    tasks = get_tasks_for_date(date_string)
    if not tasks:
        return 0
    completed = len([t for t in tasks if t["status"] == "Complete"])
    return round((completed / len(tasks)) * 100, 1)


def get_todays_summary():
    # Returns a summary dictionary for today.
    # Includes total tasks, completed, incomplete, skipped, and completion rate.
    tasks = get_tasks_for_today()
    total = len(tasks)
    completed = len([t for t in tasks if t["status"] == "Complete"])
    incomplete = len([t for t in tasks if t["status"] == "Incomplete"])
    skipped = len([t for t in tasks if t["status"] == "Skipped"])
    planned = len([t for t in tasks if t["status"] == "Planned"])

    return {
        "total": total,
        "completed": completed,
        "incomplete": incomplete,
        "skipped": skipped,
        "planned": planned,
        "completion_rate": get_completion_rate(today()),
    }


def get_routine_tasks():
    # Returns all tasks marked as routines.
    tasks = get_all_tasks()
    return [t for t in tasks if t.get("is_routine") == True]


def get_upcoming_tasks(hours=2):
    # Returns tasks scheduled within the next X hours from now.
    # Used for the startup time-aware summary.
    now = datetime.datetime.now()
    upcoming = []
    todays_tasks = get_tasks_for_today()

    for task in todays_tasks:
        if not task.get("scheduled_time"):
            continue
        try:
            task_time = datetime.datetime.strptime(
                f"{today()} {task['scheduled_time']}", "%Y-%m-%d %H:%M"
            )
            minutes_until = (task_time - now).total_seconds() / 60
            # Only include tasks that are coming up within the window and haven't passed
            if 0 <= minutes_until <= hours * 60:
                upcoming.append((task, int(minutes_until)))
        except ValueError:
            continue

    # Sort by soonest first
    upcoming.sort(key=lambda x: x[1])
    return upcoming


def get_overdue_tasks():
    # Returns tasks from today that had a scheduled time that has already passed
    # and are still marked as Planned.
    now = datetime.datetime.now()
    overdue = []
    todays_tasks = get_tasks_for_today()

    for task in todays_tasks:
        if task["status"] != "Planned":
            continue
        if not task.get("scheduled_time"):
            continue
        try:
            task_time = datetime.datetime.strptime(
                f"{today()} {task['scheduled_time']}", "%Y-%m-%d %H:%M"
            )
            if task_time < now:
                overdue.append(task)
        except ValueError:
            continue

    return overdue