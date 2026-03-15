# models.py — DayKeep
# Defines what a Goal, Task, and Journal Entry look like.
# All validation lives here. Nothing gets stored that hasn't passed through this file.

import datetime


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

# Goal categories and their sub-categories
GOAL_CATEGORIES = {
    "Academic": ["Homework", "Assignments", "Studying", "Research", "Projects", "Exams", "Other"],
    "Personal": ["Health & Fitness", "Mindfulness", "Hobbies", "Reading", "Self-improvement", "Other"],
    "Career": ["Internships", "Networking", "Portfolio", "Skills", "Job Applications", "Other"],
    "Health": ["Exercise", "Nutrition", "Sleep", "Mental Health", "Medical", "Other"],
    "Financial": ["Saving", "Budgeting", "Income", "Expenses", "Other"],
    "Social": ["Family", "Friends", "Community", "Events", "Other"],
    "Other": [],
}

# Flat list of category names for display
GOAL_CATEGORY_NAMES = list(GOAL_CATEGORIES.keys())

# Goal statuses available when CREATING a goal
GOAL_CREATION_STATUSES = ["Active"]

# Goal statuses available when EDITING an existing goal
GOAL_EDIT_STATUSES = ["Active", "Achieved", "Inactive", "Cancelled"]

# Task categories and their sub-categories
TASK_CATEGORIES = {
    "Class": ["Lecture", "Lab", "Seminar", "Office Hours", "Other"],
    "Meeting": ["Club", "Study Group", "Work", "Advising", "Other"],
    "Routine": ["Morning Routine", "Evening Routine", "Exercise", "Meal", "Prayer", "Other"],
    "Personal": ["Errands", "Self-care", "Reading", "Hobby", "Other"],
    "Work": ["Assignment", "Project", "Research", "Admin", "Other"],
    "Other": [],
}

# Flat list of task category names
TASK_CATEGORY_NAMES = list(TASK_CATEGORIES.keys())

# Task statuses available when CREATING a task
TASK_CREATION_STATUSES = ["Planned"]

# Task statuses available when EDITING a task
TASK_EDIT_STATUSES = ["Planned", "Complete", "Incomplete", "Skipped", "Postponed"]

# Mood ratings for journal entries
MOOD_LABELS = {
    "1": "Rough",
    "2": "Below average",
    "3": "Okay",
    "4": "Good",
    "5": "Great"
}

# Season definitions — month ranges
SEASONS = {
    "Spring": (3, 5),    # March to May
    "Summer": (6, 8),    # June to August
    "Fall":   (9, 11),   # September to November
    "Winter": (12, 2),   # December to February
}

# Navigation commands — recognized on any input screen
NAV_COMMANDS = {
    ".quit": "cancel and exit to main menu",
    ".back": "go back to previous screen",
    ".main": "go to main menu",
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────

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


def current_time():
    # Returns the current time as HH:MM
    return datetime.datetime.now().strftime("%H:%M")


def is_nav_command(text):
    # Returns True if the input is a navigation command
    return text.strip().lower() in NAV_COMMANDS


def get_season_target_date(season_name):
    # Given a season name, returns the first month of that season
    # and the correct year — if the season has passed this year, returns next year.
    # Returns (year, month) tuple.
    import datetime
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    start_month, end_month = SEASONS[season_name]

    # For Winter, the season starts in December — handle year wrap
    if season_name == "Winter":
        if current_month >= 12:
            # Already in winter, use next year for January
            return current_year + 1, 1
        elif current_month <= 2:
            # Still in winter
            return current_year, 1
        else:
            # Winter hasn't come yet this year
            return current_year, 12
    else:
        if current_month > end_month:
            # Season has passed this year
            return current_year + 1, start_month
        else:
            return current_year, start_month


# ─── GOAL ─────────────────────────────────────────────────────────────────────

def create_goal(title, status, description="", category="", subcategory="", target_date="", is_routine=False, routine_time=""):
    # Validates and returns a new goal dictionary.
    # Returns (goal, None) on success or (None, error_message) on failure.

    if not title or not title.strip():
        return None, "Title is required."

    if status not in GOAL_CREATION_STATUSES:
        return None, f"Status must be one of: {', '.join(GOAL_CREATION_STATUSES)}"

    if category and category not in GOAL_CATEGORY_NAMES:
        return None, f"Category must be one of: {', '.join(GOAL_CATEGORY_NAMES)}"

    if target_date and not check_date_format(target_date):
        return None, "Target date must be in YYYY-MM-DD format."

    goal = {
        "id": None,
        "title": title.strip(),
        "description": description.strip(),
        "category": category.strip(),
        "subcategory": subcategory.strip(),
        "target_date": target_date.strip(),
        "status": status,
        "is_routine": is_routine,
        "routine_time": routine_time.strip() if routine_time else "",
        "streak": 0,
        "last_streak_date": "",
        "date_created": now(),
        "last_updated": now(),
    }

    return goal, None


# ─── TASK ─────────────────────────────────────────────────────────────────────

def create_task(title, date, status, category="", subcategory="", goal_id=None,
                scheduled_time="", is_routine=False, notes=None, time_spent=""):
    # Validates and returns a new task dictionary.
    # Returns (task, None) on success or (None, error_message) on failure.

    if not title or not title.strip():
        return None, "Title is required."

    if not date or not date.strip():
        return None, "Date is required."

    if not check_date_format(date):
        return None, "Date must be in YYYY-MM-DD format."

    if status not in TASK_EDIT_STATUSES:
        return None, f"Invalid status."

    if category and category not in TASK_CATEGORY_NAMES:
        return None, f"Category must be one of: {', '.join(TASK_CATEGORY_NAMES)}"

    if scheduled_time and not check_time_format(scheduled_time):
        return None, "Scheduled time must be in HH:MM format."

    if time_spent:
        try:
            int(time_spent)
        except ValueError:
            return None, "Time spent must be a number (minutes)."

    task = {
        "id": None,
        "title": title.strip(),
        "date": date.strip(),
        "category": category.strip(),
        "subcategory": subcategory.strip(),
        "goal_id": goal_id,
        "scheduled_time": scheduled_time.strip(),
        "is_routine": is_routine,
        "status": status,
        "time_spent": time_spent,
        "notes": notes if notes else [],   # notes is now a list, not a string
        "postpone_history": [],            # tracks postpone events
        "date_completed": "",
        "date_created": now(),
        "last_updated": now(),
    }

    return task, None


# ─── JOURNAL ENTRY ────────────────────────────────────────────────────────────

def create_journal_entry(date, content, mood=""):
    # Validates and returns a new journal entry dictionary.
    # Returns (entry, None) on success or (None, error_message) on failure.

    if not date or not date.strip():
        return None, "Date is required."

    if not check_date_format(date):
        return None, "Date must be in YYYY-MM-DD format."

    if not content or not content.strip():
        return None, "Journal entry cannot be empty."

    if mood and mood not in MOOD_LABELS:
        return None, "Mood must be a number from 1 to 5."

    entry = {
        "id": None,
        "date": date.strip(),
        "content": content.strip(),
        "mood": mood,
        "date_created": now(),
        "last_updated": now(),
        "update_history": [],  # list of timestamps every time the entry was saved
    }

    return entry, None


# ─── USER PROFILE ─────────────────────────────────────────────────────────────

def create_user_profile(name):
    # Creates a user profile stored in daykeep.json on first run.
    return {
        "name": name.strip(),
        "date_created": now(),
    }