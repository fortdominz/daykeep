# db.py — DayKeep
# All data storage lives here. This is the only file that reads and writes to daykeep.json.
# Every other file calls functions from here — nothing touches the file directly.
# This isolation means when we migrate to MongoDB later, only this file changes.

import json
import os
import datetime

from models import today


# ─── SETUP ────────────────────────────────────────────────────────────────────

DATA_FILE = "daykeep.json"

EMPTY_DATA = {
    "user": {},
    "goals": [],
    "tasks": [],
    "journal": [],
}


# ─── CORE STORAGE ─────────────────────────────────────────────────────────────

def load_data():
    if not os.path.exists(DATA_FILE):
        return EMPTY_DATA.copy()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─── ID HELPERS ───────────────────────────────────────────────────────────────

def get_next_id(records):
    if not records:
        return 1
    return max(record["id"] for record in records) + 1


# ─── USER PROFILE ─────────────────────────────────────────────────────────────

def get_user():
    # Returns the user profile dictionary, or empty dict if not set up yet.
    data = load_data()
    return data.get("user", {})


def save_user(profile):
    # Saves the user profile.
    data = load_data()
    data["user"] = profile
    save_data(data)


def is_first_run():
    # Returns True if no user profile exists yet.
    user = get_user()
    return not user or not user.get("name")


# ─── GOALS ────────────────────────────────────────────────────────────────────

def get_all_goals():
    data = load_data()
    return data["goals"]


def get_goal_by_id(goal_id):
    goals = get_all_goals()
    for goal in goals:
        if goal["id"] == goal_id:
            return goal
    return None


def add_goal(goal):
    data = load_data()
    goal["id"] = get_next_id(data["goals"])
    data["goals"].append(goal)
    save_data(data)
    return goal


def update_goal(goal_id, updated_fields):
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
    data = load_data()
    original_count = len(data["goals"])
    data["goals"] = [g for g in data["goals"] if g["id"] != goal_id]
    if len(data["goals"]) < original_count:
        save_data(data)
        return True
    return False


def update_goal_streak(goal_id):
    # Called when a routine task linked to this goal is marked complete.
    # If the last streak date was yesterday, increment streak.
    # If it was today already, do nothing.
    # If it was earlier or empty, reset streak to 1.
    data = load_data()
    today_str = today()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    for i, goal in enumerate(data["goals"]):
        if goal["id"] == goal_id:
            last_date = goal.get("last_streak_date", "")
            if last_date == today_str:
                # Already updated today
                return
            elif last_date == yesterday_str:
                # Continuing the streak
                data["goals"][i]["streak"] = goal.get("streak", 0) + 1
            else:
                # Streak broken or starting fresh
                data["goals"][i]["streak"] = 1
            data["goals"][i]["last_streak_date"] = today_str
            data["goals"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            return


def get_goals_with_endangered_streaks():
    # Returns goals whose streak is active but hasn't been updated today.
    # These are the ones at risk of being broken if the user doesn't act.
    goals = get_all_goals()
    today_str = today()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    endangered = []

    for goal in goals:
        streak = goal.get("streak", 0)
        last_date = goal.get("last_streak_date", "")
        # Only flag goals with an active streak that haven't been updated today
        if streak > 0 and last_date == yesterday_str:
            endangered.append(goal)

    return endangered


# ─── TASKS ────────────────────────────────────────────────────────────────────

def get_all_tasks():
    data = load_data()
    return data["tasks"]


def get_tasks_for_date(date_string):
    tasks = get_all_tasks()
    return [t for t in tasks if t["date"] == date_string]


def get_tasks_for_today():
    return get_tasks_for_date(today())


def get_task_by_id(task_id):
    tasks = get_all_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def add_task(task):
    data = load_data()
    task["id"] = get_next_id(data["tasks"])
    data["tasks"].append(task)
    save_data(data)
    return task


def update_task(task_id, updated_fields):
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
    data = load_data()
    original_count = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    if len(data["tasks"]) < original_count:
        save_data(data)
        return True
    return False


def add_note_to_task(task_id, note_text):
    # Adds a new note to a task's notes list.
    # Notes stack — they never overwrite each other.
    data = load_data()
    for i, task in enumerate(data["tasks"]):
        if task["id"] == task_id:
            if not isinstance(data["tasks"][i].get("notes"), list):
                data["tasks"][i]["notes"] = []
            data["tasks"][i]["notes"].append({
                "text": note_text.strip(),
                "added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            data["tasks"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            return True
    return False


def delete_note_from_task(task_id, note_index):
    # Deletes a specific note by its index in the notes list.
    data = load_data()
    for i, task in enumerate(data["tasks"]):
        if task["id"] == task_id:
            notes = data["tasks"][i].get("notes", [])
            if 0 <= note_index < len(notes):
                notes.pop(note_index)
                data["tasks"][i]["notes"] = notes
                data["tasks"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_data(data)
                return True
    return False


def postpone_task(task_id, new_date, new_time=""):
    # Records a postpone event in the task's history and updates the date/time.
    data = load_data()
    for i, task in enumerate(data["tasks"]):
        if task["id"] == task_id:
            # Record the postpone event in history
            postpone_event = {
                "postponed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "original_date": task["date"],
                "original_time": task.get("scheduled_time", ""),
                "new_date": new_date,
                "new_time": new_time,
            }
            if not isinstance(data["tasks"][i].get("postpone_history"), list):
                data["tasks"][i]["postpone_history"] = []
            data["tasks"][i]["postpone_history"].append(postpone_event)

            # Update the task to the new date/time
            data["tasks"][i]["date"] = new_date
            data["tasks"][i]["scheduled_time"] = new_time
            data["tasks"][i]["status"] = "Planned"
            data["tasks"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            return True
    return False


def check_and_flag_stale_tasks():
    # Checks all tasks from previous days that are still on Planned status
    # and updates them to Not Updated.
    data = load_data()
    today_str = today()
    changed = False

    for i, task in enumerate(data["tasks"]):
        if task["status"] == "Planned" and task["date"] < today_str:
            data["tasks"][i]["status"] = "Abandoned: needs update"
            data["tasks"][i]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changed = True

    if changed:
        save_data(data)


# ─── JOURNAL ──────────────────────────────────────────────────────────────────

def get_all_journal_entries():
    data = load_data()
    return data["journal"]


def get_journal_entry_by_date(date_string):
    entries = get_all_journal_entries()
    for entry in entries:
        if entry["date"] == date_string:
            return entry
    return None


def get_todays_journal_entry():
    return get_journal_entry_by_date(today())


def get_journal_entry_by_id(entry_id):
    entries = get_all_journal_entries()
    for entry in entries:
        if entry["id"] == entry_id:
            return entry
    return None


def add_journal_entry(entry):
    data = load_data()
    entry["id"] = get_next_id(data["journal"])
    data["journal"].append(entry)
    save_data(data)
    return entry


def update_journal_entry(entry_id, updated_fields):
    data = load_data()
    for i, entry in enumerate(data["journal"]):
        if entry["id"] == entry_id:
            for field, value in updated_fields.items():
                data["journal"][i][field] = value
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["journal"][i]["last_updated"] = timestamp
            # Append to update history
            if not isinstance(data["journal"][i].get("update_history"), list):
                data["journal"][i]["update_history"] = []
            data["journal"][i]["update_history"].append(timestamp)
            save_data(data)
            return True
    return False


def delete_journal_entry(entry_id):
    data = load_data()
    original_count = len(data["journal"])
    data["journal"] = [e for e in data["journal"] if e["id"] != entry_id]
    if len(data["journal"]) < original_count:
        save_data(data)
        return True
    return False


# ─── ACCOUNTABILITY HELPERS ───────────────────────────────────────────────────

def get_completion_rate(date_string):
    tasks = get_tasks_for_date(date_string)
    if not tasks:
        return 0
    completed = len([t for t in tasks if t["status"] == "Complete"])
    return round((completed / len(tasks)) * 100, 1)


def get_todays_summary():
    tasks = get_tasks_for_today()
    total = len(tasks)
    completed = len([t for t in tasks if t["status"] == "Complete"])
    incomplete = len([t for t in tasks if t["status"] == "Incomplete"])
    skipped = len([t for t in tasks if t["status"] == "Skipped"])
    planned = len([t for t in tasks if t["status"] == "Planned"])
    postponed = len([t for t in tasks if t["status"] == "Postponed"])
    not_updated = len([t for t in tasks if t["status"] == "Not Updated"])

    return {
        "total": total,
        "completed": completed,
        "incomplete": incomplete,
        "skipped": skipped,
        "planned": planned,
        "postponed": postponed,
        "not_updated": not_updated,
        "completion_rate": get_completion_rate(today()),
    }


def get_routine_tasks():
    tasks = get_all_tasks()
    return [t for t in tasks if t.get("is_routine") == True]


def get_upcoming_tasks(hours=2):
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
            if 0 <= minutes_until <= hours * 60:
                upcoming.append((task, int(minutes_until)))
        except ValueError:
            continue

    upcoming.sort(key=lambda x: x[1])
    return upcoming


def get_overdue_tasks():
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


# ─── ROUTINE GOALS & AUTO-GENERATION ─────────────────────────────────────────

def get_routine_goals():
    # Returns all active goals marked as routine.
    goals = get_all_goals()
    return [g for g in goals if g.get("is_routine") and g["status"] == "Active"]


def auto_generate_routine_tasks():
    # On startup, checks every routine goal and creates today's task if it
    # doesn't already exist. Returns a list of newly created task titles.
    from models import create_task
    routine_goals = get_routine_goals()
    today_str = today()
    generated = []

    for goal in routine_goals:
        # Check if a routine task linked to this goal already exists for today
        todays_tasks = get_tasks_for_today()
        already_exists = any(
            t.get("goal_id") == goal["id"] and t.get("is_routine")
            for t in todays_tasks
        )

        if not already_exists:
            # Auto-generate the task using the goal's title and routine time
            task, error = create_task(
                title=goal["title"],
                date=today_str,
                status="Planned",
                category=goal.get("category", ""),
                subcategory=goal.get("subcategory", ""),
                goal_id=goal["id"],
                scheduled_time=goal.get("routine_time", ""),
                is_routine=True,
                notes=[],
            )
            if not error:
                add_task(task)
                generated.append(goal["title"])

    return generated


# ─── ANALYTICS ────────────────────────────────────────────────────────────────

def get_analytics():
    # Gathers cross-app analytics data for the analytics dashboard.
    all_tasks = get_all_tasks()
    all_goals = get_all_goals()

    total_tasks    = len(all_tasks)
    completed      = len([t for t in all_tasks if t["status"] == "Complete"])
    incomplete     = len([t for t in all_tasks if t["status"] == "Incomplete"])
    skipped        = len([t for t in all_tasks if t["status"] == "Skipped"])
    postponed      = len([t for t in all_tasks if t["status"] == "Postponed"])
    abandoned      = len([t for t in all_tasks if t["status"] == "Abandoned: needs update"])
    planned        = len([t for t in all_tasks if t["status"] == "Planned"])

    overall_rate = round((completed / total_tasks) * 100, 1) if total_tasks else 0

    # Streak leaderboard — top goals by streak
    goals_with_streaks = sorted(
        [g for g in all_goals if g.get("streak", 0) > 0],
        key=lambda g: g["streak"],
        reverse=True
    )

    # Most productive day of the week — which day has the most completions
    day_counts = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    for task in all_tasks:
        if task["status"] == "Complete" and task.get("date"):
            try:
                d = datetime.datetime.strptime(task["date"], "%Y-%m-%d").weekday()
                day_counts[d] += 1
            except ValueError:
                continue

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    best_day = day_names[max(day_counts, key=day_counts.get)] if any(day_counts.values()) else "Not enough data"

    # Journal entries count
    data = load_data()
    journal_count = len(data.get("journal", []))

    return {
        "total_tasks":        total_tasks,
        "completed":          completed,
        "incomplete":         incomplete,
        "skipped":            skipped,
        "postponed":          postponed,
        "abandoned":          abandoned,
        "planned":            planned,
        "overall_rate":       overall_rate,
        "goals_with_streaks": goals_with_streaks,
        "best_day":           best_day,
        "journal_count":      journal_count,
        "total_goals":        len(all_goals),
        "active_goals":       len([g for g in all_goals if g["status"] == "Active"]),
        "achieved_goals":     len([g for g in all_goals if g["status"] == "Achieved"]),
    }


def get_abandoned_tasks():
    # Returns all tasks with "Abandoned: needs update" status.
    tasks = get_all_tasks()
    return [t for t in tasks if t["status"] == "Abandoned: needs update"]