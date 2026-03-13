# main.py — DayKeep
# All screens and app flow live here. This is the entry point.
# It ties everything together — db.py for data, models.py for validation, ui.py for display.

import sys
import db
import models
import ui


# ─── TODAY'S TASKS ────────────────────────────────────────────────────────────

def screen_todays_tasks():
    while True:
        ui.print_header("Today's Tasks", models.today())
        tasks = db.get_tasks_for_today()
        ui.print_tasks_table(tasks, title="Today's Tasks")

        print(ui.colorize("  a", ui.BOLD + ui.CYAN) + ui.colorize("  Add a task", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back to main menu", ui.WHITE))
        print()

        if tasks:
            print(ui.colorize("  Or type a task ID to open it.", ui.DIM))
            print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        if choice == "b":
            break
        elif choice == "a":
            screen_add_task()
        elif choice.isdigit():
            screen_task_detail(int(choice))
        else:
            continue


def screen_task_detail(task_id):
    while True:
        ui.print_header("Task Detail")
        task = db.get_task_by_id(task_id)

        if not task:
            print(ui.colorize("  Task not found.", ui.RED))
            ui.wait_for_enter()
            break

        # Look up the goal title if the task is linked to one
        goal_title = ""
        if task.get("goal_id"):
            goal = db.get_goal_by_id(task["goal_id"])
            if goal:
                goal_title = goal["title"]

        ui.print_task_detail(task, goal_title)

        print(ui.colorize("  u", ui.BOLD + ui.CYAN) + ui.colorize("  Update this task", ui.WHITE))
        print(ui.colorize("  d", ui.BOLD + ui.CYAN) + ui.colorize("  Delete this task", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        if choice == "b":
            break
        elif choice == "u":
            screen_update_task(task_id)
        elif choice == "d":
            screen_delete_task(task_id)
            break
        else:
            continue


def screen_add_task():
    ui.print_header("Add a Task")

    # Title — required
    title = ui.ask_required("Task title")

    # Date — defaults to today
    date_input = ui.ask("Date", default=models.today())
    if not date_input or not models.check_date_format(date_input):
        date_input = models.today()

    # Scheduled time — optional
    scheduled_time = ui.ask_time("Scheduled time")

    # Category — optional picker
    print()
    category = ui.pick_task_category(allow_cancel=True) or ""

    # Routine — optional
    print()
    is_routine_input = ui.ask("Is this a routine task? (y/n)", default="n").lower()
    is_routine = is_routine_input == "y"

    # Goal link — optional
    goals = db.get_all_goals()
    active_goals = [g for g in goals if g["status"] == "Active"]
    goal_id = None

    if active_goals:
        print()
        print(ui.colorize("  Link to a goal? (optional)", ui.CYAN))
        print()
        goal_options = [f"{g['id']}. {g['title']}" for g in active_goals]
        goal_options.append("No goal")
        selection = ui.pick_from_list("Select a goal:", goal_options, allow_cancel=True)
        if selection and selection != "No goal":
            # Extract the ID from the selection string
            try:
                goal_id = int(selection.split(".")[0])
            except ValueError:
                goal_id = None

    # Notes — optional
    print()
    notes = ui.ask("Notes (optional)")

    # Status — defaults to Planned
    status = "Planned"

    # Create and save the task
    task, error = models.create_task(
        title=title,
        date=date_input,
        status=status,
        category=category,
        goal_id=goal_id,
        scheduled_time=scheduled_time,
        is_routine=is_routine,
        notes=notes,
    )

    if error:
        print(ui.colorize(f"  Error: {error}", ui.RED))
        ui.wait_for_enter()
        return

    db.add_task(task)
    print()
    print(ui.colorize("  ✓ Task added.", ui.GREEN))
    ui.wait_for_enter()


def screen_update_task(task_id):
    ui.print_header("Update Task")
    task = db.get_task_by_id(task_id)

    if not task:
        print(ui.colorize("  Task not found.", ui.RED))
        ui.wait_for_enter()
        return

    print(ui.colorize("  Leave a field blank to keep the current value.", ui.DIM))
    print()

    # Title
    new_title = ui.ask("Title", default=task["title"])
    if not new_title.strip():
        new_title = task["title"]

    # Scheduled time
    print()
    new_time = input(ui.colorize(f"  Scheduled time [{task.get('scheduled_time') or 'none'}]: ", ui.CYAN)).strip()
    if not new_time:
        new_time = task.get("scheduled_time", "")

    # Status picker
    print()
    new_status = ui.pick_task_status(allow_cancel=True) or task["status"]

    # Notes
    print()
    new_notes = ui.ask("Notes", default=task.get("notes", ""))

    updated_fields = {
        "title": new_title,
        "scheduled_time": new_time,
        "status": new_status,
        "notes": new_notes,
    }

    db.update_task(task_id, updated_fields)
    print()
    print(ui.colorize("  ✓ Task updated.", ui.GREEN))
    ui.wait_for_enter()


def screen_delete_task(task_id):
    ui.print_header("Delete Task")
    task = db.get_task_by_id(task_id)

    if not task:
        print(ui.colorize("  Task not found.", ui.RED))
        ui.wait_for_enter()
        return

    print(ui.colorize(f"  Delete \"{task['title']}\"?", ui.WHITE))
    print()
    confirm = input(ui.colorize("  Type YES to confirm: ", ui.RED)).strip()

    if confirm == "YES":
        db.delete_task(task_id)
        print(ui.colorize("  ✓ Task deleted.", ui.GREEN))
    else:
        print(ui.colorize("  Cancelled.", ui.DIM))

    ui.wait_for_enter()


# ─── GOALS ────────────────────────────────────────────────────────────────────

def screen_goals():
    while True:
        ui.print_header("Goals")
        goals = db.get_all_goals()
        ui.print_goals_table(goals)

        print(ui.colorize("  a", ui.BOLD + ui.CYAN) + ui.colorize("  Add a goal", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back to main menu", ui.WHITE))
        print()

        if goals:
            print(ui.colorize("  Or type a goal ID to open it.", ui.DIM))
            print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        if choice == "b":
            break
        elif choice == "a":
            screen_add_goal()
        elif choice.isdigit():
            screen_goal_detail(int(choice))
        else:
            continue


def screen_goal_detail(goal_id):
    while True:
        ui.print_header("Goal Detail")
        goal = db.get_goal_by_id(goal_id)

        if not goal:
            print(ui.colorize("  Goal not found.", ui.RED))
            ui.wait_for_enter()
            break

        ui.print_goal_detail(goal)

        print(ui.colorize("  u", ui.BOLD + ui.CYAN) + ui.colorize("  Update this goal", ui.WHITE))
        print(ui.colorize("  d", ui.BOLD + ui.CYAN) + ui.colorize("  Delete this goal", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        if choice == "b":
            break
        elif choice == "u":
            screen_update_goal(goal_id)
        elif choice == "d":
            screen_delete_goal(goal_id)
            break
        else:
            continue


def screen_add_goal():
    ui.print_header("Add a Goal")

    title = ui.ask_required("Goal title")

    print()
    category = ui.pick_goal_category(allow_cancel=True) or ""

    print()
    status = ui.pick_goal_status(allow_cancel=True) or "Active"

    print()
    target_date = ui.ask_date("Target date")

    print()
    description = ui.ask("Description (optional)")

    goal, error = models.create_goal(
        title=title,
        status=status,
        description=description,
        category=category,
        target_date=target_date,
    )

    if error:
        print(ui.colorize(f"  Error: {error}", ui.RED))
        ui.wait_for_enter()
        return

    db.add_goal(goal)
    print()
    print(ui.colorize("  ✓ Goal added.", ui.GREEN))
    ui.wait_for_enter()


def screen_update_goal(goal_id):
    ui.print_header("Update Goal")
    goal = db.get_goal_by_id(goal_id)

    if not goal:
        print(ui.colorize("  Goal not found.", ui.RED))
        ui.wait_for_enter()
        return

    print(ui.colorize("  Leave a field blank to keep the current value.", ui.DIM))
    print()

    new_title = ui.ask("Title", default=goal["title"])
    if not new_title.strip():
        new_title = goal["title"]

    print()
    new_status = ui.pick_goal_status(allow_cancel=True) or goal["status"]

    print()
    new_category = ui.pick_goal_category(allow_cancel=True) or goal.get("category", "")

    print()
    new_target = input(ui.colorize(f"  Target date [{goal.get('target_date') or 'none'}]: ", ui.CYAN)).strip()
    if not new_target:
        new_target = goal.get("target_date", "")

    print()
    new_description = ui.ask("Description", default=goal.get("description", ""))

    updated_fields = {
        "title": new_title,
        "status": new_status,
        "category": new_category,
        "target_date": new_target,
        "description": new_description,
    }

    db.update_goal(goal_id, updated_fields)
    print()
    print(ui.colorize("  ✓ Goal updated.", ui.GREEN))
    ui.wait_for_enter()


def screen_delete_goal(goal_id):
    ui.print_header("Delete Goal")
    goal = db.get_goal_by_id(goal_id)

    if not goal:
        print(ui.colorize("  Goal not found.", ui.RED))
        ui.wait_for_enter()
        return

    print(ui.colorize(f"  Delete \"{goal['title']}\"?", ui.WHITE))
    print()
    confirm = input(ui.colorize("  Type YES to confirm: ", ui.RED)).strip()

    if confirm == "YES":
        db.delete_goal(goal_id)
        print(ui.colorize("  ✓ Goal deleted.", ui.GREEN))
    else:
        print(ui.colorize("  Cancelled.", ui.DIM))

    ui.wait_for_enter()


# ─── JOURNAL ──────────────────────────────────────────────────────────────────

def screen_journal():
    while True:
        ui.print_header("Journal")

        entry = db.get_todays_journal_entry()

        if entry:
            print(ui.colorize("  Today's entry:", ui.BOLD + ui.WHITE))
            print()
            ui.print_journal_entry(entry)
            print(ui.colorize("  e", ui.BOLD + ui.CYAN) + ui.colorize("  Edit today's entry", ui.WHITE))
        else:
            print(ui.colorize("  No entry for today yet.", ui.DIM))
            print()
            print(ui.colorize("  w", ui.BOLD + ui.CYAN) + ui.colorize("  Write today's entry", ui.WHITE))

        print(ui.colorize("  p", ui.BOLD + ui.CYAN) + ui.colorize("  Past entries", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back to main menu", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        if choice == "b":
            break
        elif choice in ("w", "e"):
            screen_write_journal(entry)
        elif choice == "p":
            screen_past_journal_entries()
        else:
            continue


def screen_write_journal(existing_entry=None):
    ui.print_header("Journal Entry", models.today())

    print(ui.colorize("  Write your entry below. Press Enter twice when done.", ui.DIM))
    print()

    lines = []
    empty_line_count = 0

    while empty_line_count < 1:
        line = input("  ")
        if line == "":
            empty_line_count += 1
        else:
            empty_line_count = 0
            lines.append(line)

    content = "\n".join(lines).strip()

    if not content:
        print(ui.colorize("  Nothing written. Entry not saved.", ui.DIM))
        ui.wait_for_enter()
        return

    print()
    mood = ui.pick_mood(allow_cancel=True)

    if existing_entry:
        db.update_journal_entry(existing_entry["id"], {
            "content": content,
            "mood": mood,
        })
        print()
        print(ui.colorize("  ✓ Entry updated.", ui.GREEN))
    else:
        entry, error = models.create_journal_entry(
            date=models.today(),
            content=content,
            mood=mood,
        )
        if error:
            print(ui.colorize(f"  Error: {error}", ui.RED))
            ui.wait_for_enter()
            return
        db.add_journal_entry(entry)
        print()
        print(ui.colorize("  ✓ Entry saved.", ui.GREEN))

    ui.wait_for_enter()


def screen_past_journal_entries():
    ui.print_header("Past Journal Entries")

    entries = db.get_all_journal_entries()

    if not entries:
        print(ui.colorize("  No journal entries yet.", ui.DIM))
        ui.wait_for_enter()
        return

    # Sort entries newest first
    entries = sorted(entries, key=lambda e: e["date"], reverse=True)

    print(ui.colorize(f"  {'ID':<4} {'Date':<14} {'Mood':<16} Preview", ui.DIM))
    ui.print_divider()

    for entry in entries:
        entry_id = ui.colorize(f"{entry['id']:<4}", ui.DIM)
        date_col = f"{entry['date']:<14}"
        mood_col = f"{ui.colorize_mood(entry.get('mood', '')):<16}"
        preview  = entry["content"][:40].replace("\n", " ") + ("..." if len(entry["content"]) > 40 else "")
        print(f"  {entry_id} {date_col} {mood_col} {preview}")

    print()
    print(ui.colorize("  Type an entry ID to read it, or b to go back.", ui.DIM))
    print()

    choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

    if choice == "b" or not choice:
        return
    elif choice.isdigit():
        entry = db.get_journal_entry_by_id(int(choice))
        if entry:
            ui.print_header("Journal Entry", entry["date"])
            ui.print_journal_entry(entry)
            ui.wait_for_enter()
        else:
            print(ui.colorize("  Entry not found.", ui.RED))
            ui.wait_for_enter()


# ─── ALL TASKS ────────────────────────────────────────────────────────────────

def screen_all_tasks():
    ui.print_header("All Tasks")
    tasks = db.get_all_tasks()

    if not tasks:
        print(ui.colorize("  No tasks yet.", ui.DIM))
        ui.wait_for_enter()
        return

    # Sort by date, newest first
    tasks = sorted(tasks, key=lambda t: t["date"], reverse=True)
    ui.print_tasks_table(tasks, title="All Tasks")

    print(ui.colorize("  Type a task ID to open it, or press Enter to go back.", ui.DIM))
    print()

    choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

    if choice.isdigit():
        screen_task_detail(int(choice))


# ─── HELP ─────────────────────────────────────────────────────────────────────

def screen_help():
    ui.print_header("Help")
    ui.print_help()
    ui.wait_for_enter()


# ─── MAIN MENU & ENTRY POINT ──────────────────────────────────────────────────

def show_startup():
    # Gathers all data needed for the startup summary and displays it
    ui.clear_screen()
    summary  = db.get_todays_summary()
    upcoming = db.get_upcoming_tasks(hours=2)
    overdue  = db.get_overdue_tasks()
    goals    = db.get_all_goals()
    ui.print_startup_summary(summary, upcoming, overdue, goals)


def show_main_menu():
    while True:
        ui.print_header("Main Menu")
        ui.print_main_menu()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        screens = {
            "1": screen_todays_tasks,
            "2": screen_goals,
            "3": screen_journal,
            "4": screen_all_tasks,
            "h": screen_help,
        }

        if choice == "q":
            ui.clear_screen()
            print(ui.colorize("\n  Keep your day. Keep your word.\n", ui.DIM))
            sys.exit(0)
        elif choice in screens:
            screens[choice]()
        else:
            continue


def run():
    show_startup()
    ui.wait_for_enter("  Press Enter to open the menu...")
    show_main_menu()


# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run()