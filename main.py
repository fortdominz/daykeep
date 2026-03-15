# main.py — DayKeep
# All screens and app flow live here. This is the entry point.
# It ties everything together — db.py for data, models.py for validation, ui.py for display.

import sys
import db
import models
import ui


# ─── NAVIGATION HELPER ────────────────────────────────────────────────────────

# These signals tell the calling screen what to do next.
NAV_BACK = "__BACK__"
NAV_MAIN = "__MAIN__"
NAV_QUIT = "__QUIT__"

def handle_nav(value):
    # Converts a nav command string into a signal constant.
    if value is None:
        return None
    v = str(value).strip().lower()
    if v == ".quit":
        return NAV_QUIT
    if v == ".back":
        return NAV_BACK
    if v == ".main":
        return NAV_MAIN
    return None


def is_nav(value):
    return value in (NAV_BACK, NAV_MAIN, NAV_QUIT)


# ─── TODAY'S TASKS ────────────────────────────────────────────────────────────

def screen_todays_tasks():
    while True:
        ui.print_header("Today's Tasks", models.today())
        tasks = db.get_tasks_for_today()
        ui.print_tasks_table(tasks, title="Today's Tasks")
        ui.print_nav_hint()

        print(ui.colorize("  a", ui.BOLD + ui.CYAN) + ui.colorize("  Add a task", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back to main menu", ui.WHITE))
        print()

        if tasks:
            print(ui.colorize("  Or type a task ID to open it.", ui.DIM))
            print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav in (NAV_QUIT, NAV_MAIN, NAV_BACK):
            return nav

        if choice == "b":
            return NAV_BACK
        elif choice == "a":
            result = screen_add_task()
            if result == NAV_MAIN:
                return NAV_MAIN
        elif choice.isdigit():
            result = screen_task_detail(int(choice))
            if result == NAV_MAIN:
                return NAV_MAIN


def screen_task_detail(task_id):
    while True:
        ui.print_header("Task Detail")
        task = db.get_task_by_id(task_id)

        if not task:
            print(ui.colorize("  Task not found.", ui.RED))
            ui.wait_for_enter()
            return NAV_BACK

        goal_title = ""
        if task.get("goal_id"):
            goal = db.get_goal_by_id(task["goal_id"])
            if goal:
                goal_title = goal["title"]

        ui.print_task_detail(task, goal_title)
        ui.print_nav_hint()

        print(ui.colorize("  u", ui.BOLD + ui.CYAN) + ui.colorize("  Update this task", ui.WHITE))
        print(ui.colorize("  n", ui.BOLD + ui.CYAN) + ui.colorize("  Manage notes", ui.WHITE))
        print(ui.colorize("  p", ui.BOLD + ui.CYAN) + ui.colorize("  Postpone this task", ui.WHITE))
        print(ui.colorize("  d", ui.BOLD + ui.CYAN) + ui.colorize("  Delete this task", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav:
            return nav

        if choice == "b":
            return NAV_BACK
        elif choice == "u":
            result = screen_update_task(task_id)
            if is_nav(result):
                return result
        elif choice == "n":
            result = screen_manage_notes(task_id)
            if is_nav(result):
                return result
        elif choice == "p":
            result = screen_postpone_task(task_id)
            if is_nav(result):
                return result
        elif choice == "d":
            result = screen_delete_task(task_id)
            if is_nav(result):
                return result
            return NAV_BACK


def screen_add_task():
    ui.print_header("Add a Task")
    ui.print_nav_hint()

    title = ui.ask_required("Task title")
    nav = handle_nav(title)
    if nav:
        return nav

    date_input = ui.ask("Date", default=models.today())
    nav = handle_nav(date_input)
    if nav:
        return nav
    if not date_input or not models.check_date_format(date_input):
        date_input = models.today()

    scheduled_time = ui.ask_time("Scheduled time")
    nav = handle_nav(scheduled_time)
    if nav:
        return nav

    print()
    category = ui.pick_task_category(allow_cancel=True)
    nav = handle_nav(category)
    if nav:
        return nav
    category = category or ""

    subcategory = ""
    if category and category in models.TASK_CATEGORIES:
        print()
        subcategory = ui.pick_task_subcategory(category, allow_cancel=True) or ""
        nav = handle_nav(subcategory)
        if nav:
            return nav

    print()
    is_routine_input = ui.ask("Is this a routine task? (y/n)", default="n").lower()
    is_routine = is_routine_input == "y"

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
        nav = handle_nav(selection)
        if nav:
            return nav
        if selection and selection != "No goal":
            try:
                goal_id = int(selection.split(".")[0])
            except ValueError:
                goal_id = None

    print()
    notes_input = ui.ask("First note (optional)")
    initial_notes = []
    if notes_input and not handle_nav(notes_input):
        initial_notes = [{"text": notes_input.strip(), "added": models.now()}]

    task, error = models.create_task(
        title=title,
        date=date_input,
        status="Planned",
        category=category,
        subcategory=subcategory,
        goal_id=goal_id,
        scheduled_time=scheduled_time,
        is_routine=is_routine,
        notes=initial_notes,
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
    ui.print_nav_hint()

    if not task:
        print(ui.colorize("  Task not found.", ui.RED))
        ui.wait_for_enter()
        return NAV_BACK

    print(ui.colorize("  Leave a field blank or type . to keep the current value.", ui.DIM))
    print()

    new_title = ui.ask("Title", default=task["title"])
    nav = handle_nav(new_title)
    if nav:
        return nav
    if not new_title.strip():
        new_title = task["title"]

    print()
    new_time = input(ui.colorize(f"  Scheduled time [{task.get('scheduled_time') or 'none'}]: ", ui.CYAN)).strip()
    nav = handle_nav(new_time)
    if nav:
        return nav
    if not new_time:
        new_time = task.get("scheduled_time", "")

    print()
    new_status = ui.pick_task_status(editing=True, allow_cancel=True) or task["status"]
    nav = handle_nav(new_status)
    if nav:
        return nav

    # If marking complete, record the completion date
    date_completed = task.get("date_completed", "")
    if new_status == "Complete" and not date_completed:
        date_completed = models.now()

    # If linked to a routine goal and marked complete, update streak
    if new_status == "Complete" and task.get("is_routine") and task.get("goal_id"):
        db.update_goal_streak(task["goal_id"])

    updated_fields = {
        "title": new_title,
        "scheduled_time": new_time,
        "status": new_status,
        "date_completed": date_completed,
    }

    db.update_task(task_id, updated_fields)
    print()
    print(ui.colorize("  ✓ Task updated.", ui.GREEN))
    ui.wait_for_enter()


def screen_manage_notes(task_id):
    # Lets the user add a new note or delete existing ones individually.
    while True:
        ui.print_header("Manage Notes")
        task = db.get_task_by_id(task_id)
        ui.print_nav_hint()

        if not task:
            print(ui.colorize("  Task not found.", ui.RED))
            ui.wait_for_enter()
            return NAV_BACK

        notes = task.get("notes", [])
        if not isinstance(notes, list):
            notes = []

        ui.print_notes_list(notes)

        print(ui.colorize("  a", ui.BOLD + ui.CYAN) + ui.colorize("  Add a new note", ui.WHITE))
        if notes:
            print(ui.colorize("  d", ui.BOLD + ui.CYAN) + ui.colorize("  Delete a note", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav:
            return nav

        if choice == "b":
            return NAV_BACK
        elif choice == "a":
            note_text = input(ui.colorize("  New note: ", ui.CYAN)).strip()
            nav = handle_nav(note_text)
            if nav:
                return nav
            if note_text:
                db.add_note_to_task(task_id, note_text)
                print(ui.colorize("  ✓ Note added.", ui.GREEN))
                ui.wait_for_enter()
        elif choice == "d" and notes:
            print(ui.colorize("  Enter the letter of the note to delete (a, b, c...): ", ui.CYAN), end="")
            letter = input().strip().lower()
            nav = handle_nav(letter)
            if nav:
                return nav
            if len(letter) == 1 and letter.isalpha():
                index = ord(letter) - ord('a')
                if 0 <= index < len(notes):
                    confirm = input(ui.colorize(f"  Delete note ({letter})? Type YES to confirm: ", ui.RED)).strip()
                    if confirm == "YES":
                        db.delete_note_from_task(task_id, index)
                        print(ui.colorize("  ✓ Note deleted.", ui.GREEN))
                        ui.wait_for_enter()
                else:
                    print(ui.colorize("  Note not found.", ui.RED))
            else:
                print(ui.colorize("  Invalid input.", ui.RED))


def screen_postpone_task(task_id):
    ui.print_header("Postpone Task")
    task = db.get_task_by_id(task_id)
    ui.print_nav_hint()

    if not task:
        print(ui.colorize("  Task not found.", ui.RED))
        ui.wait_for_enter()
        return NAV_BACK

    print(ui.colorize(f"  Postponing: {task['title']}", ui.WHITE))
    print()
    print(ui.colorize("  When would you like to reschedule this task?", ui.CYAN))
    print()

    options = ["Later today", "Tomorrow", "Another day"]
    choice = ui.pick_from_list("Select:", options, allow_cancel=True)

    nav = handle_nav(choice)
    if nav:
        return nav
    if choice is None:
        return NAV_BACK

    import datetime

    if choice == "Later today":
        new_date = models.today()
        new_time = ui.ask_time("New scheduled time")
        nav = handle_nav(new_time)
        if nav:
            return nav

    elif choice == "Tomorrow":
        new_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        new_time = ui.ask_time("Scheduled time (optional)")
        nav = handle_nav(new_time)
        if nav:
            return nav

    else:
        new_date = ui.ask_date("Enter the new date")
        nav = handle_nav(new_date)
        if nav:
            return nav
        if not new_date:
            print(ui.colorize("  Date is required to postpone.", ui.RED))
            ui.wait_for_enter()
            return NAV_BACK
        new_time = ui.ask_time("Scheduled time (optional)")
        nav = handle_nav(new_time)
        if nav:
            return nav

    db.postpone_task(task_id, new_date, new_time)
    print()
    print(ui.colorize(f"  ✓ Task postponed to {new_date}" + (f" at {new_time}" if new_time else "") + ".", ui.GREEN))
    ui.wait_for_enter()
    return NAV_BACK


def screen_delete_task(task_id):
    ui.print_header("Delete Task")
    task = db.get_task_by_id(task_id)

    if not task:
        print(ui.colorize("  Task not found.", ui.RED))
        ui.wait_for_enter()
        return NAV_BACK

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
        ui.print_nav_hint()

        print(ui.colorize("  a", ui.BOLD + ui.CYAN) + ui.colorize("  Add a goal", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back to main menu", ui.WHITE))
        print()

        if goals:
            print(ui.colorize("  Or type a goal ID to open it.", ui.DIM))
            print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav in (NAV_QUIT, NAV_MAIN, NAV_BACK):
            return nav

        if choice == "b":
            return NAV_BACK
        elif choice == "a":
            result = screen_add_goal()
            if result == NAV_MAIN:
                return NAV_MAIN
        elif choice.isdigit():
            result = screen_goal_detail(int(choice))
            if result == NAV_MAIN:
                return NAV_MAIN


def screen_goal_detail(goal_id):
    while True:
        ui.print_header("Goal Detail")
        goal = db.get_goal_by_id(goal_id)
        ui.print_nav_hint()

        if not goal:
            print(ui.colorize("  Goal not found.", ui.RED))
            ui.wait_for_enter()
            return NAV_BACK

        ui.print_goal_detail(goal)

        print(ui.colorize("  u", ui.BOLD + ui.CYAN) + ui.colorize("  Update this goal", ui.WHITE))
        print(ui.colorize("  d", ui.BOLD + ui.CYAN) + ui.colorize("  Delete this goal", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav:
            return nav

        if choice == "b":
            return NAV_BACK
        elif choice == "u":
            result = screen_update_goal(goal_id)
            if is_nav(result):
                return result
        elif choice == "d":
            result = screen_delete_goal(goal_id)
            if is_nav(result):
                return result
            return NAV_BACK


def screen_add_goal():
    ui.print_header("Add a Goal")
    print(ui.colorize("  Type .quit at any point to cancel.", ui.DIM))
    print()

    title = ui.ask_required("Goal title")
    nav = handle_nav(title)
    if nav:
        return nav

    print()
    category = ui.pick_goal_category(allow_cancel=True)
    nav = handle_nav(category)
    if nav:
        return nav
    category = category or ""

    subcategory = ""
    if category and category in models.GOAL_CATEGORIES:
        print()
        subcategory = ui.pick_goal_subcategory(category, allow_cancel=True) or ""
        nav = handle_nav(subcategory)
        if nav:
            return nav

    print()
    status = ui.pick_goal_status(editing=False, allow_cancel=True) or "Active"
    nav = handle_nav(status)
    if nav:
        return nav

    print()
    target_date = ui.pick_target_date()
    nav = handle_nav(target_date)
    if nav:
        return nav

    print()
    is_routine_input = ui.ask("Is this a routine goal? (y/n)", default="n").lower()
    nav = handle_nav(is_routine_input)
    if nav:
        return nav
    is_routine = is_routine_input == "y"

    routine_time = ""
    if is_routine:
        print()
        routine_time = ui.ask_time("What time do you usually do this?")
        nav = handle_nav(routine_time)
        if nav:
            return nav

    print()
    description = ui.ask("Description (optional)")
    nav = handle_nav(description)
    if nav:
        return nav

    goal, error = models.create_goal(
        title=title,
        status=status,
        description=description,
        category=category,
        subcategory=subcategory,
        target_date=target_date,
        is_routine=is_routine,
        routine_time=routine_time,
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
    ui.print_nav_hint()

    if not goal:
        print(ui.colorize("  Goal not found.", ui.RED))
        ui.wait_for_enter()
        return NAV_BACK

    print(ui.colorize("  Leave a field blank or type . to keep the current value.", ui.DIM))
    print()

    new_title = ui.ask("Title", default=goal["title"])
    nav = handle_nav(new_title)
    if nav:
        return nav
    if not new_title.strip():
        new_title = goal["title"]

    print()
    new_status = ui.pick_goal_status(editing=True, allow_cancel=True) or goal["status"]
    nav = handle_nav(new_status)
    if nav:
        return nav

    print()
    new_category = ui.pick_goal_category(allow_cancel=True) or goal.get("category", "")
    nav = handle_nav(new_category)
    if nav:
        return nav

    new_subcategory = goal.get("subcategory", "")
    if new_category and new_category in models.GOAL_CATEGORIES:
        print()
        new_subcategory = ui.pick_goal_subcategory(new_category, allow_cancel=True) or new_subcategory
        nav = handle_nav(new_subcategory)
        if nav:
            return nav

    print()
    print(ui.colorize("  Update target date?", ui.CYAN))
    update_date = input(ui.colorize("  (y/n): ", ui.CYAN)).strip().lower()
    new_target = goal.get("target_date", "")
    if update_date == "y":
        new_target = ui.pick_target_date()
        nav = handle_nav(new_target)
        if nav:
            return nav

    print()
    new_description = ui.ask("Description", default=goal.get("description", ""))
    nav = handle_nav(new_description)
    if nav:
        return nav

    updated_fields = {
        "title": new_title,
        "status": new_status,
        "category": new_category,
        "subcategory": new_subcategory,
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
        return NAV_BACK

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
        ui.print_nav_hint()

        if entry:
            print(ui.colorize("  Today's entry:", ui.BOLD + ui.WHITE))
            print()
            ui.print_journal_entry(entry, readonly=False)
            print(ui.colorize("  e", ui.BOLD + ui.CYAN) + ui.colorize("  Edit today's entry", ui.WHITE))
        else:
            print(ui.colorize("  No entry for today yet.", ui.DIM))
            print()
            print(ui.colorize("  w", ui.BOLD + ui.CYAN) + ui.colorize("  Write today's entry", ui.WHITE))

        print(ui.colorize("  p", ui.BOLD + ui.CYAN) + ui.colorize("  Past entries", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back to main menu", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav in (NAV_QUIT, NAV_MAIN, NAV_BACK):
            return nav

        if choice == "b":
            return NAV_BACK
        elif choice in ("w", "e"):
            result = screen_write_journal(entry)
            if is_nav(result):
                return result
        elif choice == "p":
            result = screen_past_journal_entries()
            if is_nav(result):
                return result


def screen_write_journal(existing_entry=None):
    ui.print_header("Journal Entry", models.today())

    existing_lines = []
    if existing_entry and existing_entry.get("content"):
        existing_lines = existing_entry["content"].split("\n")

    content = ui.journal_editor(existing_lines)

    if content is None:
        print(ui.colorize("  Entry cancelled.", ui.DIM))
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
    ui.print_nav_hint()

    entries = db.get_all_journal_entries()

    if not entries:
        print(ui.colorize("  No journal entries yet.", ui.DIM))
        ui.wait_for_enter()
        return NAV_BACK

    entries = sorted(entries, key=lambda e: e["date"], reverse=True)

    print(ui.colorize(f"  {'ID':<4} {'Date':<14} {'Mood':<20} Preview", ui.DIM))
    ui.print_divider()

    for entry in entries:
        entry_id = ui.colorize(f"{entry['id']:<4}", ui.DIM)
        date_col = f"{entry['date']:<14}"
        mood_col = f"{ui.colorize_mood(entry.get('mood', ''))}"
        preview  = entry["content"][:40].replace("\n", " ") + ("..." if len(entry["content"]) > 40 else "")
        print(f"  {entry_id} {date_col} {mood_col}  {preview}")

    print()
    print(ui.colorize("  Type an entry ID to read it, or b to go back.", ui.DIM))
    print()

    choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

    nav = handle_nav(choice)
    if nav:
        return nav

    if choice == "b" or not choice:
        return NAV_BACK
    elif choice.isdigit():
        entry = db.get_journal_entry_by_id(int(choice))
        if entry:
            ui.print_header("Journal Entry", entry["date"])
            is_past = entry["date"] != models.today()
            ui.print_journal_entry(entry, readonly=is_past)
            ui.wait_for_enter()
        else:
            print(ui.colorize("  Entry not found.", ui.RED))
            ui.wait_for_enter()

    return NAV_BACK


# ─── ALL TASKS ────────────────────────────────────────────────────────────────

def screen_all_tasks():
    ui.print_header("All Tasks")
    ui.print_nav_hint()

    tasks = db.get_all_tasks()

    if not tasks:
        print(ui.colorize("  No tasks yet.", ui.DIM))
        ui.wait_for_enter()
        return NAV_BACK

    tasks = sorted(tasks, key=lambda t: t["date"], reverse=True)
    ui.print_tasks_table(tasks, title="All Tasks")

    print(ui.colorize("  Type a task ID to open it, or b to go back.", ui.DIM))
    print()

    choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

    nav = handle_nav(choice)
    if nav:
        return nav

    if choice == "b":
        return NAV_BACK
    elif choice.isdigit():
        return screen_task_detail(int(choice))

    return NAV_BACK



def screen_analytics():
    ui.print_header("Analytics")
    ui.print_nav_hint()
    analytics = db.get_analytics()
    ui.print_analytics(analytics)
    ui.wait_for_enter()


def screen_resolve_abandoned():
    # Prompts the user to resolve each abandoned task one by one.
    abandoned = db.get_abandoned_tasks()
    if not abandoned:
        return

    ui.clear_screen()
    print()
    ui.print_banner_with_tagline()
    print()
    print(ui.colorize(f"  ⚠  {len(abandoned)} task(s) need your attention from previous days.", ui.BOLD + ui.RED))
    print(ui.colorize("  Please update each one before continuing.", ui.DIM))
    print()
    ui.print_divider()
    print()

    for task in abandoned:
        print(ui.colorize(f"  Task: ", ui.DIM) + ui.colorize(task["title"], ui.BOLD + ui.WHITE))
        print(ui.colorize(f"  Date: ", ui.DIM) + task["date"])
        print()

        new_status = ui.pick_from_list(
            "What happened with this task?",
            ["Complete", "Incomplete", "Skipped"],
            allow_cancel=False
        )

        updated = {"status": new_status}
        if new_status == "Complete":
            updated["date_completed"] = models.now()
            if task.get("is_routine") and task.get("goal_id"):
                db.update_goal_streak(task["goal_id"])

        db.update_task(task["id"], updated)
        print(ui.colorize(f"  Marked as {new_status}.", ui.GREEN))
        print()

    print(ui.colorize("  All caught up! 🎉", ui.BOLD + ui.GREEN))
    ui.wait_for_enter()


def screen_export():
    while True:
        ui.print_header("Export Data")
        ui.print_nav_hint()

        print(ui.colorize("  Export your data to CSV files openable in Excel or Google Sheets.", ui.DIM))
        print()
        print(ui.colorize("  1", ui.BOLD + ui.CYAN) + ui.colorize("  Export all tasks", ui.WHITE))
        print(ui.colorize("  2", ui.BOLD + ui.CYAN) + ui.colorize("  Export all goals", ui.WHITE))
        print(ui.colorize("  3", ui.BOLD + ui.CYAN) + ui.colorize("  Export everything", ui.WHITE))
        print(ui.colorize("  b", ui.BOLD + ui.CYAN) + ui.colorize("  Back to main menu", ui.WHITE))
        print()

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav in (NAV_QUIT, NAV_MAIN, NAV_BACK):
            return nav

        if choice == "b":
            return NAV_BACK

        elif choice == "1":
            count = db.export_tasks_to_csv()
            if count:
                print(ui.colorize(f"  Exported {count} task(s) to daykeep_tasks.csv", ui.GREEN))
            else:
                print(ui.colorize("  No tasks to export.", ui.DIM))
            ui.wait_for_enter()

        elif choice == "2":
            count = db.export_goals_to_csv()
            if count:
                print(ui.colorize(f"  Exported {count} goal(s) to daykeep_goals.csv", ui.GREEN))
            else:
                print(ui.colorize("  No goals to export.", ui.DIM))
            ui.wait_for_enter()

        elif choice == "3":
            task_count = db.export_tasks_to_csv()
            goal_count = db.export_goals_to_csv()
            if task_count or goal_count:
                print(ui.colorize(f"  Exported {task_count} task(s) to daykeep_tasks.csv", ui.GREEN))
                print(ui.colorize(f"  Exported {goal_count} goal(s) to daykeep_goals.csv", ui.GREEN))
            else:
                print(ui.colorize("  Nothing to export.", ui.DIM))
            ui.wait_for_enter()

# ─── HELP ─────────────────────────────────────────────────────────────────────

def screen_help():
    ui.print_header("Help")
    ui.print_help()
    ui.wait_for_enter()


# ─── FIRST RUN ────────────────────────────────────────────────────────────────

def screen_first_run():
    ui.print_first_run_welcome()
    print(ui.colorize("  Before we begin — what would you like to be called?", ui.WHITE))
    print()

    while True:
        name = input(ui.colorize("  Your name: ", ui.CYAN)).strip()
        if not name:
            print(ui.colorize("  Please enter a name.", ui.RED))
            continue
        break

    profile = models.create_user_profile(name)
    db.save_user(profile)

    print()
    print(ui.colorize(f"  Welcome to DayKeep, {name}! 🎉", ui.BOLD + ui.GREEN))
    print(ui.colorize("  Keep your day. Keep your word.", ui.DIM))
    print()
    ui.wait_for_enter()


# ─── MAIN MENU & ENTRY POINT ──────────────────────────────────────────────────

def show_startup():
    ui.clear_screen()
    db.check_and_flag_stale_tasks()
    generated = db.auto_generate_routine_tasks()
    summary           = db.get_todays_summary()
    upcoming          = db.get_upcoming_tasks(hours=2)
    overdue           = db.get_overdue_tasks()
    goals             = db.get_all_goals()
    endangered_streaks = db.get_goals_with_endangered_streaks()
    user              = db.get_user()
    user_name         = user.get("name", "")
    ui.print_startup_summary(summary, upcoming, overdue, goals, endangered_streaks, user_name, generated)


def show_main_menu():
    user = db.get_user()
    user_name = user.get("name", "")

    while True:
        ui.clear_screen()
        endangered_streaks = db.get_goals_with_endangered_streaks()
        ui.print_main_menu(user_name, endangered_streaks)

        choice = input(ui.colorize("  Choice: ", ui.CYAN)).strip().lower()

        nav = handle_nav(choice)
        if nav == NAV_QUIT:
            ui.clear_screen()
            print(ui.colorize(f"\n  Keep your day. Keep your word.\n", ui.DIM))
            sys.exit(0)

        screens = {
            "1": screen_todays_tasks,
            "2": screen_goals,
            "3": screen_journal,
            "4": screen_all_tasks,
            "5": screen_analytics,
            "6": screen_export,
            "h": screen_help,
        }

        if choice == "q":
            ui.clear_screen()
            print(ui.colorize(f"\n  Keep your day. Keep your word.\n", ui.DIM))
            sys.exit(0)
        elif choice in screens:
            result = screens[choice]()
            # If any screen returns NAV_QUIT, exit
            if result == NAV_QUIT:
                ui.clear_screen()
                print(ui.colorize(f"\n  Keep your day. Keep your word.\n", ui.DIM))
                sys.exit(0)
            # NAV_MAIN and NAV_BACK both just return to the main menu loop


def run():
    # First run — ask for name if no profile exists
    if db.is_first_run():
        screen_first_run()

    show_startup()
    ui.wait_for_enter("  Press Enter to open the menu...")

    # Resolve any abandoned tasks before opening the menu
    screen_resolve_abandoned()

    show_main_menu()


# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run()