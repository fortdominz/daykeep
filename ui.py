# ui.py — DayKeep
# Everything visual lives here. Colors, tables, menus, prompts.
# Nothing in this file touches data directly — it only displays what it's given.

import os
import datetime
from models import GOAL_CATEGORIES, GOAL_STATUSES, TASK_CATEGORIES, TASK_STATUSES, MOOD_LABELS


# ─── COLORS ───────────────────────────────────────────────────────────────────

# ANSI escape codes for terminal colors
# We define them as constants so we never type raw codes anywhere else

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

BLACK  = "\033[30m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
PURPLE = "\033[35m"
CYAN   = "\033[36m"
WHITE  = "\033[37m"

BG_BLACK  = "\033[40m"
BG_RED    = "\033[41m"
BG_GREEN  = "\033[42m"
BG_BLUE   = "\033[44m"
BG_PURPLE = "\033[45m"
BG_CYAN   = "\033[46m"


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def colorize(text, color):
    # Wraps text in a color code and resets after
    return f"{color}{text}{RESET}"

def clear_screen():
    # Clears the terminal — works on both Windows and Mac/Linux
    os.system("cls" if os.name == "nt" else "clear")

def print_divider(char="─", width=60, color=DIM):
    # Prints a horizontal divider line
    print(colorize(char * width, color))

def print_header(title, subtitle=""):
    # Prints a clean section header
    clear_screen()
    print()
    print(colorize(f"  DAYKEEP", BOLD + CYAN) + colorize(f"  ·  {title}", BOLD + WHITE))
    if subtitle:
        print(colorize(f"  {subtitle}", DIM))
    print_divider()
    print()

def wait_for_enter(message="  Press Enter to continue..."):
    # Pauses and waits for the user to press Enter
    input(colorize(message, DIM))

def ask(question, default=""):
    # Asks the user a question and returns their answer stripped of whitespace.
    # If they press Enter without typing, returns the default value.
    if default:
        prompt = colorize(f"  {question} ", CYAN) + colorize(f"[{default}]", DIM) + colorize(": ", CYAN)
    else:
        prompt = colorize(f"  {question}: ", CYAN)
    answer = input(prompt).strip()
    return answer if answer else default

def ask_required(question):
    # Keeps asking until the user provides a non-empty answer.
    while True:
        answer = input(colorize(f"  {question}: ", CYAN)).strip()
        if answer:
            return answer
        print(colorize("  This field is required.", RED))

def ask_date(question):
    # Keeps asking until the user provides a valid YYYY-MM-DD date or leaves it blank.
    from models import check_date_format
    while True:
        answer = input(colorize(f"  {question} (YYYY-MM-DD or blank): ", CYAN)).strip()
        if not answer:
            return ""
        if check_date_format(answer):
            return answer
        print(colorize("  Invalid date format. Use YYYY-MM-DD (e.g. 2026-04-15).", RED))

def ask_time(question):
    # Keeps asking until the user provides a valid HH:MM time or leaves it blank.
    from models import check_time_format
    while True:
        answer = input(colorize(f"  {question} (HH:MM or blank): ", CYAN)).strip()
        if not answer:
            return ""
        if check_time_format(answer):
            return answer
        print(colorize("  Invalid time format. Use HH:MM (e.g. 09:30).", RED))


# ─── PICKERS ──────────────────────────────────────────────────────────────────

def pick_from_list(question, options, allow_cancel=True):
    # Shows a numbered list of options and returns the user's choice.
    # Returns None if the user cancels with 0 or q.
    print(colorize(f"  {question}", CYAN))
    print()
    for i, option in enumerate(options, 1):
        print(colorize(f"    {i}.", DIM) + f" {option}")
    if allow_cancel:
        print(colorize("    0.", DIM) + " Cancel")
    print()

    while True:
        answer = input(colorize("  Choice: ", CYAN)).strip().lower()
        if not answer:
            continue
        if allow_cancel and answer in ("0", "q"):
            return None
        try:
            index = int(answer) - 1
            if 0 <= index < len(options):
                return options[index]
        except ValueError:
            pass
        print(colorize("  Invalid choice. Try again.", RED))

def pick_goal_status(allow_cancel=True):
    return pick_from_list("Select a status:", GOAL_STATUSES, allow_cancel)

def pick_goal_category(allow_cancel=True):
    return pick_from_list("Select a category:", GOAL_CATEGORIES, allow_cancel)

def pick_task_status(allow_cancel=True):
    return pick_from_list("Select a status:", TASK_STATUSES, allow_cancel)

def pick_task_category(allow_cancel=True):
    return pick_from_list("Select a category:", TASK_CATEGORIES, allow_cancel)

def pick_mood(allow_cancel=True):
    # Shows mood options and returns the user's choice as a string 1-5
    options = [f"{k} — {v}" for k, v in MOOD_LABELS.items()]
    result = pick_from_list("How did today feel?", options, allow_cancel)
    if result is None:
        return ""
    # Extract just the number from the selected option
    return result.split(" — ")[0]


# ─── STATUS BADGES ────────────────────────────────────────────────────────────

def colorize_task_status(status):
    # Returns a color-coded status badge for a task
    colors = {
        "Planned":    BLUE,
        "Complete":   GREEN,
        "Incomplete": RED,
        "Skipped":    YELLOW,
    }
    color = colors.get(status, WHITE)
    return colorize(f"[{status}]", BOLD + color)

def colorize_goal_status(status):
    # Returns a color-coded status badge for a goal
    colors = {
        "Active":    CYAN,
        "Achieved":  GREEN,
        "Abandoned": RED,
    }
    color = colors.get(status, WHITE)
    return colorize(f"[{status}]", BOLD + color)

def colorize_mood(mood):
    # Returns a color-coded mood display
    if not mood:
        return colorize("—", DIM)
    colors = {"1": RED, "2": YELLOW, "3": WHITE, "4": CYAN, "5": GREEN}
    label = MOOD_LABELS.get(mood, "")
    color = colors.get(mood, WHITE)
    return colorize(f"{mood}/5 {label}", color)


# ─── TABLES ───────────────────────────────────────────────────────────────────

def print_tasks_table(tasks, title="Tasks"):
    # Prints a color-coded table of tasks
    if not tasks:
        print(colorize("  No tasks found.", DIM))
        return

    print(colorize(f"  {title}", BOLD + WHITE))
    print()
    print(colorize(f"  {'ID':<4} {'Title':<30} {'Time':<7} {'Category':<12} {'Status'}", DIM))
    print_divider()

    for task in tasks:
        task_id   = colorize(f"{task['id']:<4}", DIM)
        title_col = f"{task['title'][:28]:<30}"
        time_col  = colorize(f"{task.get('scheduled_time', '—'):<7}", DIM)
        cat_col   = colorize(f"{task.get('category', '—')[:10]:<12}", DIM)
        status    = colorize_task_status(task["status"])
        print(f"  {task_id} {title_col} {time_col} {cat_col} {status}")

    print()

def print_goals_table(goals, title="Goals"):
    # Prints a color-coded table of goals
    if not goals:
        print(colorize("  No goals found.", DIM))
        return

    print(colorize(f"  {title}", BOLD + WHITE))
    print()
    print(colorize(f"  {'ID':<4} {'Title':<30} {'Category':<12} {'Target':<12} {'Status'}", DIM))
    print_divider()

    for goal in goals:
        goal_id  = colorize(f"{goal['id']:<4}", DIM)
        title_col = f"{goal['title'][:28]:<30}"
        cat_col  = colorize(f"{goal.get('category', '—')[:10]:<12}", DIM)
        date_col = colorize(f"{goal.get('target_date', '—'):<12}", DIM)
        status   = colorize_goal_status(goal["status"])
        print(f"  {goal_id} {title_col} {cat_col} {date_col} {status}")

    print()

def print_journal_entry(entry):
    # Prints a single journal entry in full
    if not entry:
        print(colorize("  No journal entry found.", DIM))
        return

    print(colorize(f"  Date:  ", DIM) + entry["date"])
    print(colorize(f"  Mood:  ", DIM) + colorize_mood(entry.get("mood", "")))
    print()
    print_divider()
    print()
    print(f"  {entry['content']}")
    print()
    print_divider()


# ─── DETAIL VIEWS ─────────────────────────────────────────────────────────────

def print_task_detail(task, goal_title=""):
    # Prints the full detail view of a single task
    print(colorize("  TASK DETAIL", BOLD + WHITE))
    print_divider()
    print()

    fields = [
        ("ID",             str(task["id"])),
        ("Title",          task["title"]),
        ("Date",           task["date"]),
        ("Status",         colorize_task_status(task["status"])),
        ("Category",       task.get("category") or "—"),
        ("Scheduled Time", task.get("scheduled_time") or "—"),
        ("Routine",        "Yes" if task.get("is_routine") else "No"),
        ("Goal",           goal_title or "—"),
        ("Time Spent",     f"{task.get('time_spent')} min" if task.get("time_spent") else "—"),
        ("Notes",          task.get("notes") or "—"),
        ("Created",        task.get("date_created", "—")),
        ("Last Updated",   task.get("last_updated", "—")),
    ]

    for label, value in fields:
        print(f"  {colorize(f'{label}:', DIM):<28} {value}")

    print()

def print_goal_detail(goal):
    # Prints the full detail view of a single goal
    print(colorize("  GOAL DETAIL", BOLD + WHITE))
    print_divider()
    print()

    fields = [
        ("ID",          str(goal["id"])),
        ("Title",       goal["title"]),
        ("Status",      colorize_goal_status(goal["status"])),
        ("Category",    goal.get("category") or "—"),
        ("Target Date", goal.get("target_date") or "—"),
        ("Description", goal.get("description") or "—"),
        ("Created",     goal.get("date_created", "—")),
        ("Last Updated",goal.get("last_updated", "—")),
    ]

    for label, value in fields:
        print(f"  {colorize(f'{label}:', DIM):<28} {value}")

    print()


# ─── STARTUP SUMMARY ──────────────────────────────────────────────────────────

def print_startup_summary(summary, upcoming, overdue, goals):
    # Prints the daily summary shown when the app first opens
    today_str = datetime.date.today().strftime("%A, %B %d %Y")
    print()
    print(colorize(f"  📅  {today_str}", BOLD + WHITE))
    print()

    # Today's task summary
    if summary["total"] == 0:
        print(colorize("  No tasks planned for today.", DIM))
    else:
        print(colorize(f"  Today's tasks: ", DIM) +
              colorize(f"{summary['completed']} complete", GREEN) + "  " +
              colorize(f"{summary['planned']} planned", BLUE) + "  " +
              colorize(f"{summary['incomplete']} incomplete", RED) + "  " +
              colorize(f"{summary['skipped']} skipped", YELLOW))
        print(colorize(f"  Completion rate: ", DIM) +
              colorize(f"{summary['completion_rate']}%", BOLD + (GREEN if summary['completion_rate'] >= 70 else YELLOW if summary['completion_rate'] >= 40 else RED)))

    print()

    # Overdue alerts
    if overdue:
        print(colorize(f"  ⚠  {len(overdue)} overdue task(s):", BOLD + RED))
        for task in overdue:
            print(colorize(f"    · {task['title']} — was scheduled at {task['scheduled_time']}", RED))
        print()

    # Upcoming in next 2 hours
    if upcoming:
        print(colorize("  ⏰  Coming up:", BOLD + YELLOW))
        for task, minutes in upcoming:
            print(colorize(f"    · {task['title']} at {task['scheduled_time']} — in {minutes} min", YELLOW))
        print()

    # Active goals
    active_goals = [g for g in goals if g["status"] == "Active"]
    if active_goals:
        print(colorize(f"  🎯  Active goals: ", DIM) + colorize(str(len(active_goals)), BOLD + CYAN))
        for goal in active_goals[:3]:
            print(colorize(f"    · {goal['title']}", CYAN))
        if len(active_goals) > 3:
            print(colorize(f"    · ...and {len(active_goals) - 3} more", DIM))
        print()

    print_divider()


# ─── MENUS ────────────────────────────────────────────────────────────────────

def print_main_menu():
    # Prints the main menu options
    print(colorize("  MAIN MENU", BOLD + WHITE))
    print()
    options = [
        ("1", "Today's Tasks",     "plan, log, and manage today"),
        ("2", "Goals",             "set and track your goals"),
        ("3", "Journal",           "write and read journal entries"),
        ("4", "All Tasks",         "browse tasks across all dates"),
        ("h", "Help",              "how to use DayKeep"),
        ("q", "Quit",              "exit the app"),
    ]
    for key, label, desc in options:
        print(f"  {colorize(key, BOLD + CYAN)}  {colorize(label, WHITE):<22} {colorize(desc, DIM)}")
    print()

def print_help():
    # Prints the full help reference
    sections = [
        ("TODAY'S TASKS", [
            ("1 → Today",        "View and manage all tasks for today"),
            ("Add task",         "Plan a new task — title, time, category, goal link"),
            ("Mark complete",    "Type the task ID and update its status"),
            ("Overdue alerts",   "Shown on startup for missed scheduled tasks"),
            ("Upcoming",         "Tasks within the next 2 hours shown on startup"),
        ]),
        ("GOALS", [
            ("2 → Goals",        "View all your goals"),
            ("Add goal",         "Set a new goal with category and target date"),
            ("Link to task",     "Connect any task to a goal when adding or editing"),
            ("Statuses",         "Active, Achieved, Abandoned"),
        ]),
        ("JOURNAL", [
            ("3 → Journal",      "Open today's journal entry or browse past entries"),
            ("Write entry",      "Free writing — no structure required"),
            ("Mood rating",      "Rate your day 1 (Rough) to 5 (Great)"),
            ("One per day",      "Only one journal entry allowed per day"),
        ]),
        ("GENERAL", [
            ("h",                "Open this help screen"),
            ("q",                "Quit the app"),
            ("0 or q",           "Cancel any picker or form mid-way"),
        ]),
    ]

    print(colorize("  DAYKEEP — HELP", BOLD + CYAN))
    print_divider()
    print()

    for section_title, items in sections:
        print(colorize(f"  {section_title}", BOLD + WHITE))
        print()
        for key, desc in items:
            print(f"  {colorize(key, CYAN):<32} {desc}")
        print()
        print_divider()
        print()