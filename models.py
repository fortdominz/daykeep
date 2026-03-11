# models.py — DayKeep
# Defines what a Goal, Task, and Journal Entry look like.
# All validation lives here. Nothing gets stored that hasn't passed through this file.

import datetime


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

# The categories a goal can belong to
GOAL_CATEGORIES = ["Academic", "Personal", "Career", "Health", "Other"]

# The possible statuses a goal can have
GOAL_STATUSES = ["Active", "Achieved", "Abandoned"]

# The categories a task can belong to
TASK_CATEGORIES = ["Class", "Meeting", "Routine", "Personal", "Work", "Other"]

# The possible statuses a task can have
TASK_STATUSES = ["Planned", "Complete", "Incomplete", "Skipped"]

# Mood ratings for journal entries — 1 is rough, 5 is great
MOOD_LABELS = {
    "1": "Rough",
    "2": "Below average",
    "3": "Okay",
    "4": "Good",
    "5": "Great"
}


# ─── HELPER ───────────────────────────────────────────────────────────────────

def check_date_format(date_string):
    # Returns True if the date is a valid YYYY-MM-DD string, False otherwise
    try:
        datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def check_time_format(time_string):
    # Returns True if the time is a valid HH:MM string, False otherwise
    try:
        datetime.datetime.strptime(time_string, "%H:%M")
        return True
    except ValueError:
        return False


def today():
    # Returns today's date as a YYYY-MM-DD string
    return datetime.date.today().strftime("%Y-%m-%d")


def now():
    # Returns the current date and time as a readable string
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ─── GOAL ─────────────────────────────────────────────────────────────────────

def create_goal(title, status, description="", category="", target_date=""):
    # Validates and returns a new goal dictionary.
    # Returns (goal, None) on success or (None, error_message) on failure.

    # title is required
    if not title or not title.strip():
        return None, "Title is required."

    # status must be valid
    if status not in GOAL_STATUSES:
        return None, f"Status must be one of: {', '.join(GOAL_STATUSES)}"

    # category must be valid if provided
    if category and category not in GOAL_CATEGORIES:
        return None, f"Category must be one of: {', '.join(GOAL_CATEGORIES)}"

    # target_date must be valid format if provided
    if target_date and not check_date_format(target_date):
        return None, "Target date must be in YYYY-MM-DD format."

    goal = {
        "id": None,           # assigned by db.py
        "title": title.strip(),
        "description": description.strip(),
        "category": category.strip(),
        "target_date": target_date.strip(),
        "status": status,
        "date_created": now(),
        "last_updated": now(),
    }

    return goal, None


# ─── TASK ─────────────────────────────────────────────────────────────────────

def create_task(title, date, status, category="", goal_id=None,
                scheduled_time="", is_routine=False,
                time_spent="", notes=""):
    # Validates and returns a new task dictionary.
    # Returns (task, None) on success or (None, error_message) on failure.

    # title is required
    if not title or not title.strip():
        return None, "Title is required."

    # date is required and must be valid
    if not date or not date.strip():
        return None, "Date is required."
    if not check_date_format(date):
        return None, "Date must be in YYYY-MM-DD format."

    # status must be valid
    if status not in TASK_STATUSES:
        return None, f"Status must be one of: {', '.join(TASK_STATUSES)}"

    # category must be valid if provided
    if category and category not in TASK_CATEGORIES:
        return None, f"Category must be one of: {', '.join(TASK_CATEGORIES)}"

    # scheduled_time must be valid format if provided
    if scheduled_time and not check_time_format(scheduled_time):
        return None, "Scheduled time must be in HH:MM format."

    # time_spent must be a number if provided
    if time_spent:
        try:
            int(time_spent)
        except ValueError:
            return None, "Time spent must be a number (minutes)."

    task = {
        "id": None,           # assigned by db.py
        "title": title.strip(),
        "date": date.strip(),
        "category": category.strip(),
        "goal_id": goal_id,
        "scheduled_time": scheduled_time.strip(),
        "is_routine": is_routine,
        "status": status,
        "time_spent": time_spent,
        "notes": notes.strip(),
        "date_created": now(),
        "last_updated": now(),
    }

    return task, None


# ─── JOURNAL ENTRY ────────────────────────────────────────────────────────────

def create_journal_entry(date, content, mood=""):
    # Validates and returns a new journal entry dictionary.
    # Returns (entry, None) on success or (None, error_message) on failure.

    # date is required and must be valid
    if not date or not date.strip():
        return None, "Date is required."
    if not check_date_format(date):
        return None, "Date must be in YYYY-MM-DD format."

    # content is required
    if not content or not content.strip():
        return None, "Journal entry cannot be empty."

    # mood must be 1-5 if provided
    if mood and mood not in MOOD_LABELS:
        return None, "Mood must be a number from 1 to 5."

    entry = {
        "id": None,           # assigned by db.py
        "date": date.strip(),
        "content": content.strip(),
        "mood": mood,
        "date_created": now(),
        "last_updated": now(),
    }

    return entry, None