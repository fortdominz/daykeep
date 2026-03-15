# ui.py — DayKeep
# Everything visual lives here. Colors, tables, menus, prompts.
# Nothing in this file touches data directly — it only displays what it's given.

import os
import datetime
from models import (GOAL_CATEGORY_NAMES, GOAL_CATEGORIES, GOAL_CREATION_STATUSES,
                    GOAL_EDIT_STATUSES, TASK_CATEGORY_NAMES, TASK_CATEGORIES,
                    TASK_EDIT_STATUSES, MOOD_LABELS, SEASONS, NAV_COMMANDS)


# ─── COLORS ───────────────────────────────────────────────────────────────────

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
    return f"{color}{text}{RESET}"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print(colorize("  +================================+", BOLD + CYAN))
    print(colorize("  |         D A Y K E E P          |", BOLD + CYAN))
    print(colorize("  +================================+", BOLD + CYAN))

def print_banner_with_tagline():
    print(colorize("  +================================+", BOLD + CYAN))
    print(colorize("  |         D A Y K E E P          |", BOLD + CYAN))
    print(colorize("  | Keep your day. Keep your word. |", BOLD + CYAN))
    print(colorize("  +================================+", BOLD + CYAN))


def print_divider(char="─", width=60, color=DIM):
    print(colorize(char * width, color))

def print_header(title, subtitle=""):
    clear_screen()
    print()
    print_banner()
    print()
    print(colorize(f"  >> {title.upper()}", BOLD + CYAN))
    if subtitle:
        print(colorize(f"     {subtitle}", DIM))
    print_divider()
    print()

def wait_for_enter(message="  Press Enter to continue..."):
    input(colorize(message, DIM))

def print_nav_hint():
    # Prints a subtle reminder of navigation commands
    print(colorize("  Navigation: .back — previous  ·  .main — main menu  ·  .quit — exit", DIM))
    print()

def ask(question, default=""):
    if default:
        prompt = colorize(f"  {question} ", CYAN) + colorize(f"[{default}]", DIM) + colorize(": ", CYAN)
    else:
        prompt = colorize(f"  {question}: ", CYAN)
    answer = input(prompt).strip()
    # "." means skip — keep the current value
    if answer == ".":
        return default
    return answer if answer else default

def ask_required(question):
    # Keeps asking until the user provides a non-empty answer.
    # Recognizes nav commands and returns them directly so the caller can handle them.
    while True:
        answer = input(colorize(f"  {question}: ", CYAN)).strip()
        if not answer:
            print(colorize("  This field is required.", RED))
            continue
        return answer

def ask_date(question):
    from models import check_date_format
    while True:
        answer = input(colorize(f"  {question} (YYYY-MM-DD or blank): ", CYAN)).strip()
        if not answer:
            return ""
        if answer.lower() in NAV_COMMANDS:
            return answer.lower()
        if check_date_format(answer):
            return answer
        print(colorize("  Invalid date format. Use YYYY-MM-DD (e.g. 2026-04-15).", RED))

def ask_time(question):
    from models import check_time_format
    while True:
        answer = input(colorize(f"  {question} (HH:MM or blank): ", CYAN)).strip()
        if not answer:
            return ""
        if answer.lower() in NAV_COMMANDS:
            return answer.lower()
        if check_time_format(answer):
            return answer
        print(colorize("  Invalid time format. Use HH:MM (e.g. 09:30).", RED))


# ─── PICKERS ──────────────────────────────────────────────────────────────────

def pick_from_list(question, options, allow_cancel=True):
    # Shows a numbered list and returns the chosen option.
    # Returns None on cancel, or a nav command string if one is entered.
    print(colorize(f"  {question}", CYAN))
    print()
    for i, option in enumerate(options, 1):
        print(colorize(f"    {i}.", DIM) + f" {option}")
    if allow_cancel:
        print(colorize("    0.", DIM) + " Cancel / skip  " + colorize("(or type .)", DIM))
    print()

    while True:
        answer = input(colorize("  Choice: ", CYAN)).strip().lower()
        if not answer:
            continue
        if answer in NAV_COMMANDS:
            return answer
        if allow_cancel and answer in ("0", "q", "."):
            return None
        try:
            index = int(answer) - 1
            if 0 <= index < len(options):
                return options[index]
        except ValueError:
            pass
        print(colorize("  Invalid choice. Try again.", RED))

def pick_with_confirmation(question, options, allow_cancel=True):
    # Like pick_from_list but asks the user to confirm their choice.
    # For "Other" — lets the user type their own value.
    while True:
        result = pick_from_list(question, options, allow_cancel)

        if result is None or result in NAV_COMMANDS:
            return result

        if result == "Other":
            while True:
                custom = input(colorize("  Type your own value: ", CYAN)).strip()
                if not custom:
                    print(colorize("  Value cannot be empty.", RED))
                    continue
                confirm = input(colorize(f"  You typed \"{custom}\" — is the spelling correct? (y/n): ", CYAN)).strip().lower()
                if confirm == "y":
                    return custom
                elif confirm == "n":
                    continue
                else:
                    print(colorize("  Please enter y or n.", RED))
        else:
            confirm = input(colorize(f"  You selected \"{result}\" — confirm? (y/n): ", CYAN)).strip().lower()
            if confirm == "y":
                return result
            elif confirm == "n":
                continue
            else:
                print(colorize("  Please enter y or n.", RED))

def pick_goal_status(editing=False, allow_cancel=True):
    statuses = GOAL_EDIT_STATUSES if editing else GOAL_CREATION_STATUSES
    return pick_from_list("Select a status:", statuses, allow_cancel)

def pick_goal_category(allow_cancel=True):
    return pick_with_confirmation("Select a category:", GOAL_CATEGORY_NAMES, allow_cancel)

def pick_goal_subcategory(category, allow_cancel=True):
    subcategories = GOAL_CATEGORIES.get(category, [])
    if not subcategories:
        return ""
    return pick_with_confirmation(f"Select a sub-category for {category}:", subcategories, allow_cancel)

def pick_task_status(editing=False, allow_cancel=True):
    statuses = TASK_EDIT_STATUSES if editing else ["Planned"]
    return pick_from_list("Select a status:", statuses, allow_cancel)

def pick_task_category(allow_cancel=True):
    return pick_with_confirmation("Select a category:", TASK_CATEGORY_NAMES, allow_cancel)

def pick_task_subcategory(category, allow_cancel=True):
    subcategories = TASK_CATEGORIES.get(category, [])
    if not subcategories:
        return ""
    return pick_with_confirmation(f"Select a sub-category for {category}:", subcategories, allow_cancel)

def pick_mood(allow_cancel=True):
    options = [f"{k} — {v}" for k, v in MOOD_LABELS.items()]
    result = pick_from_list("How did today feel?", options, allow_cancel)
    if result is None or result in NAV_COMMANDS:
        return ""
    return result.split(" — ")[0]

def pick_target_date():
    # Smart date picker — seasons, year options, or manual entry.
    # Returns a YYYY-MM-DD string, empty string, or a nav command.
    from models import get_season_target_date, check_date_format
    import datetime

    print(colorize("  How would you like to set the target date?", CYAN))
    print()
    options = ["By season", "By year", "Enter date manually", "No target date"]
    method = pick_from_list("Select an option:", options, allow_cancel=True)

    if method is None or method in NAV_COMMANDS:
        return method or ""

    # ── BY SEASON ──
    if method == "By season":
        current_month = datetime.date.today().month
        current_year = datetime.date.today().year
        season_options = []

        for season in SEASONS:
            year, month = get_season_target_date(season)
            start_month, _ = SEASONS[season]
            if year > current_year or (year == current_year and start_month > current_month):
                label = f"{season} {year}"
            else:
                label = f"Next {season} ({year})"
            season_options.append((label, year, month))

        display_options = [s[0] for s in season_options]
        selection = pick_from_list("Select a season:", display_options, allow_cancel=True)

        if selection is None or selection in NAV_COMMANDS:
            return selection or ""

        for label, year, month in season_options:
            if label == selection:
                return f"{year}-{month:02d}-01"

    # ── BY YEAR ──
    elif method == "By year":
        current_year = datetime.date.today().year
        year_options = ["This year", "Next year", "Future year"]
        year_choice = pick_from_list("Select a year option:", year_options, allow_cancel=True)

        if year_choice is None or year_choice in NAV_COMMANDS:
            return year_choice or ""

        if year_choice == "This year":
            chosen_year = current_year
        elif year_choice == "Next year":
            chosen_year = current_year + 1
        else:
            while True:
                yr = input(colorize("  Enter the year (e.g. 2028): ", CYAN)).strip()
                try:
                    chosen_year = int(yr)
                    if chosen_year >= current_year:
                        break
                    print(colorize("  Year must be current year or later.", RED))
                except ValueError:
                    print(colorize("  Please enter a valid year.", RED))

        # Month picker
        month_options = [
            "01 — January", "02 — February", "03 — March", "04 — April",
            "05 — May", "06 — June", "07 — July", "08 — August",
            "09 — September", "10 — October", "11 — November", "12 — December"
        ]
        month_choice = pick_from_list("Select a month:", month_options, allow_cancel=True)

        if month_choice is None or month_choice in NAV_COMMANDS:
            return month_choice or ""

        chosen_month = month_choice.split(" — ")[0]

        # Optional day
        day_input = input(colorize(f"  Enter a day (1-31) or press Enter to skip: ", CYAN)).strip()
        if day_input and day_input.isdigit():
            chosen_day = day_input.zfill(2)
        else:
            chosen_day = "01"

        return f"{chosen_year}-{chosen_month}-{chosen_day}"

    # ── MANUAL ──
    elif method == "Enter date manually":
        return ask_date("Enter the target date")

    return ""


# ─── STATUS BADGES ────────────────────────────────────────────────────────────

def colorize_task_status(status):
    colors = {
        "Planned":               BLUE,
        "Complete":              GREEN,
        "Incomplete":            RED,
        "Skipped":               YELLOW,
        "Postponed":             PURPLE,
        "Abandoned: needs update": RED,
    }
    color = colors.get(status, WHITE)
    bold = BOLD if status == "Abandoned: needs update" else ""
    return colorize(f"[{status}]", bold + color)

def colorize_goal_status(status):
    colors = {
        "Active":    CYAN,
        "Achieved":  GREEN,
        "Inactive":  YELLOW,
        "Cancelled": RED,
    }
    color = colors.get(status, WHITE)
    return colorize(f"[{status}]", BOLD + color)

def colorize_mood(mood):
    if not mood:
        return colorize("—", DIM)
    colors = {"1": RED, "2": YELLOW, "3": WHITE, "4": CYAN, "5": GREEN}
    label = MOOD_LABELS.get(mood, "")
    color = colors.get(mood, WHITE)
    return colorize(f"{mood}/5 {label}", color)

def colorize_streak(streak):
    if not streak or streak == 0:
        return colorize("No streak", DIM)
    if streak >= 30:
        return colorize(f"🔥 {streak} days", BOLD + GREEN)
    if streak >= 7:
        return colorize(f"⚡ {streak} days", GREEN)
    return colorize(f"{streak} days", CYAN)


# ─── TABLES ───────────────────────────────────────────────────────────────────

def print_tasks_table(tasks, title="Tasks"):
    if not tasks:
        print(colorize("  No tasks found.", DIM))
        return

    print(colorize(f"  {title}", BOLD + WHITE))
    print()
    print(colorize(f"  {'ID':<4} {'Title':<28} {'Date':<12} {'Time':<7} {'Status'}", DIM))
    print_divider()

    for task in tasks:
        task_id   = colorize(f"{task['id']:<4}", DIM)
        title_col = f"{task['title'][:26]:<28}"
        date_col  = colorize(f"{task.get('date', '—'):<12}", DIM)
        time_col  = colorize(f"{task.get('scheduled_time', '—'):<7}", DIM)
        status    = colorize_task_status(task["status"])

        # Highlight Not Updated rows
        if task["status"] == "Abandoned: needs update":
            print(colorize(f"  ⚠ ", BOLD + RED) + f"{task_id} {title_col} {date_col} {time_col} {status}")
        else:
            print(f"  {task_id} {title_col} {date_col} {time_col} {status}")

    print()

def print_goals_table(goals, title="Goals"):
    if not goals:
        print(colorize("  No goals found.", DIM))
        return

    print(colorize(f"  {title}", BOLD + WHITE))
    print()
    print(colorize(f"  {'ID':<4} {'Title':<28} {'Category':<12} {'Streak':<12} {'Status'}", DIM))
    print_divider()

    for goal in goals:
        goal_id   = colorize(f"{goal['id']:<4}", DIM)
        title_col = f"{goal['title'][:26]:<28}"
        cat_col   = colorize(f"{goal.get('category', '—')[:10]:<12}", DIM)
        streak    = colorize_streak(goal.get("streak", 0))
        status    = colorize_goal_status(goal["status"])
        print(f"  {goal_id} {title_col} {cat_col} {streak:<12} {status}")

    print()

def print_journal_entry(entry, readonly=False):
    if not entry:
        print(colorize("  No journal entry found.", DIM))
        return

    print(colorize(f"  Date:    ", DIM) + colorize(entry["date"], BOLD + WHITE))
    print(colorize(f"  Mood:    ", DIM) + colorize_mood(entry.get("mood", "")))
    print(colorize(f"  Created: ", DIM) + colorize(entry.get("date_created", "-"), DIM))

    # Show update history
    history = entry.get("update_history", [])
    if history:
        print(colorize(f"  Updated: ", DIM) + colorize(f"{len(history)} time(s)", DIM))
        for i, timestamp in enumerate(history, 1):
            print(colorize(f"    {i}. {timestamp}", DIM))
    else:
        print(colorize(f"  Updated: ", DIM) + colorize("Never", DIM))

    if readonly:
        print(colorize("  (Read only — past entries cannot be edited)", YELLOW))

    print()
    print_divider()
    print()
    # Print content with line numbers
    lines = entry["content"].split("\n")
    for i, line in enumerate(lines, 1):
        print(f"  {colorize(f'[{i}]', DIM)} {line}")
    print()
    print_divider()


# ─── DETAIL VIEWS ─────────────────────────────────────────────────────────────

def print_task_detail(task, goal_title=""):
    print(colorize("  TASK DETAIL", BOLD + WHITE))
    print_divider()
    print()

    # Notes — show as stacked list
    notes = task.get("notes", [])
    if isinstance(notes, list) and notes:
        notes_display = ""
        for i, note in enumerate(notes):
            letter = chr(ord('a') + i)
            notes_display += f"({letter}) {note['text']}  "
    elif isinstance(notes, str) and notes:
        notes_display = notes
    else:
        notes_display = "—"

    # Postpone history
    postpone_history = task.get("postpone_history", [])
    postpone_display = f"{len(postpone_history)} time(s)" if postpone_history else "Never"

    fields = [
        ("ID",             str(task["id"])),
        ("Title",          task["title"]),
        ("Date",           task["date"]),
        ("Status",         colorize_task_status(task["status"])),
        ("Category",       task.get("category") or "—"),
        ("Sub-category",   task.get("subcategory") or "—"),
        ("Scheduled Time", task.get("scheduled_time") or "—"),
        ("Routine",        "Yes" if task.get("is_routine") else "No"),
        ("Goal",           goal_title or "—"),
        ("Time Spent",     f"{task.get('time_spent')} min" if task.get("time_spent") else "—"),
        ("Postponed",      postpone_display),
        ("Date Completed", task.get("date_completed") or "—"),
        ("Notes",          notes_display),
        ("Created",        task.get("date_created", "—")),
        ("Last Updated",   task.get("last_updated", "—")),
    ]

    for label, value in fields:
        print(f"  {colorize(f'{label}:', DIM):<28} {value}")

    print()

def print_goal_detail(goal):
    print(colorize("  GOAL DETAIL", BOLD + WHITE))
    print_divider()
    print()

    fields = [
        ("ID",           str(goal["id"])),
        ("Title",        goal["title"]),
        ("Status",       colorize_goal_status(goal["status"])),
        ("Category",     goal.get("category") or "-"),
        ("Sub-category", goal.get("subcategory") or "-"),
        ("Target Date",  goal.get("target_date") or "-"),
        ("Routine",      "Yes" if goal.get("is_routine") else "No"),
        ("Routine Time", goal.get("routine_time") or "-"),
        ("Streak",       colorize_streak(goal.get("streak", 0))),
        ("Description",  goal.get("description") or "-"),
        ("Created",      goal.get("date_created", "-")),
        ("Last Updated", goal.get("last_updated", "-")),
    ]

    for label, value in fields:
        print(f"  {colorize(f'{label}:', DIM):<28} {value}")

    print()

def print_notes_list(notes):
    # Prints a task's notes as a numbered list for individual deletion
    if not notes:
        print(colorize("  No notes yet.", DIM))
        return
    print(colorize("  Notes:", BOLD + WHITE))
    print()
    for i, note in enumerate(notes):
        letter = chr(ord('a') + i)
        added = note.get("added", "")
        print(f"  {colorize(f'({letter})', BOLD + CYAN)} {note['text']}")
        if added:
            print(f"       {colorize(f'Added: {added}', DIM)}")
    print()


# ─── JOURNAL EDITOR ───────────────────────────────────────────────────────────

def journal_editor(existing_lines=None):
    # An improved line-by-line journal editor with commands.
    # Returns the final content as a string, or None if cancelled.

    lines = list(existing_lines) if existing_lines else []

    print(colorize("  ─────────────────────────────────────────────", DIM))
    print(colorize("  Write your entry below, one line at a time.", WHITE))
    print()
    print(colorize("  Commands:", BOLD + WHITE))
    print(colorize("    .save          ", CYAN) + "→ save and finish")
    print(colorize("    .undo          ", CYAN) + "→ delete last line")
    print(colorize("    .undo [#]      ", CYAN) + "→ delete a specific line")
    print(colorize("    .edit [#]      ", CYAN) + "→ edit a specific line")
    print(colorize("    .quit          ", CYAN) + "→ cancel (warns if unsaved changes exist)")
    print(colorize("  ─────────────────────────────────────────────", DIM))
    print()

    # Show existing lines if editing
    if lines:
        print(colorize("  Current entry:", DIM))
        for i, line in enumerate(lines, 1):
            print(f"  {colorize(f'[{i}]', DIM)} {line}")
        print()

    while True:
        line_num = len(lines) + 1
        entry = input(f"  {colorize(f'[{line_num}]', DIM)} ").strip()

        # ── .save ──
        if entry.lower() == ".save":
            if not lines:
                print(colorize("  Nothing written yet.", RED))
                continue
            return "\n".join(lines)

        # ── .quit ──
        elif entry.lower() == ".quit":
            # Check if there are unsaved changes compared to the original entry
            current_content = "".join(lines).strip()
            original_content = "".join(existing_lines).strip() if existing_lines else ""
            if current_content != original_content and lines:
                print(colorize("  ⚠  You have unsaved changes.", BOLD + YELLOW))
                print(colorize("  Use .save to save first, or type .quit again to discard.", DIM))
                # Wait for next input — if it's .quit again, exit without saving
                confirm = input(f"  {colorize(f'[{len(lines) + 1}]', DIM)} ").strip()
                if confirm.lower() == ".quit":
                    return None
                elif confirm.lower() == ".save":
                    if not lines:
                        print(colorize("  Nothing written yet.", RED))
                        continue
                    return "".join(lines)
                else:
                    # Treat as a new line and continue
                    if confirm:
                        lines.append(confirm)
            else:
                return None

        # ── .undo ──
        elif entry.lower() == ".undo":
            if not lines:
                print(colorize("  Nothing to undo.", RED))
            else:
                removed = lines.pop()
                print(colorize(f"  → Line {len(lines) + 1} removed: \"{removed}\"", YELLOW))

        # ── .undo [#] ──
        elif entry.lower().startswith(".undo "):
            parts = entry.split()
            if len(parts) == 2 and parts[1].isdigit():
                index = int(parts[1]) - 1
                if 0 <= index < len(lines):
                    removed = lines.pop(index)
                    print(colorize(f"  → Line {index + 1} removed: \"{removed}\"", YELLOW))
                else:
                    print(colorize(f"  → No line {parts[1]} exists.", RED))
            else:
                print(colorize("  Usage: .undo [line number]", RED))

        # ── .edit [#] ──
        elif entry.lower().startswith(".edit "):
            parts = entry.split()
            if len(parts) == 2 and parts[1].isdigit():
                index = int(parts[1]) - 1
                if 0 <= index < len(lines):
                    print(colorize(f"  → Editing line {index + 1}: \"{lines[index]}\"", YELLOW))
                    new_line = input(f"  {colorize(f'[{index + 1}]', CYAN)} ").strip()
                    if new_line:
                        lines[index] = new_line
                        print(colorize(f"  → Line {index + 1} updated.", GREEN))
                    else:
                        print(colorize("  → No change made.", DIM))
                else:
                    print(colorize(f"  → No line {parts[1]} exists.", RED))
            else:
                print(colorize("  Usage: .edit [line number]", RED))

        # ── Regular line ──
        elif entry:
            lines.append(entry)

        # Show current lines after any command
        if lines and entry.startswith("."):
            print()
            for i, line in enumerate(lines, 1):
                print(f"  {colorize(f'[{i}]', DIM)} {line}")
            print()



def print_analytics(data):
    # Displays the full analytics dashboard.
    print(colorize("  ANALYTICS DASHBOARD", BOLD + WHITE))
    print_divider()
    print()

    # Overall completion rate with bar
    rate = data["overall_rate"]
    bar_filled = int(rate / 5)
    bar_empty  = 20 - bar_filled
    bar_color  = GREEN if rate >= 70 else YELLOW if rate >= 40 else RED
    bar = colorize("█" * bar_filled, bar_color) + colorize("░" * bar_empty, DIM)
    print(colorize("  Overall Completion Rate", BOLD + WHITE))
    print(f"  {bar}  {colorize(f'{rate}%', BOLD + bar_color)}")
    print()

    # Task breakdown
    print(colorize("  Task Breakdown", BOLD + WHITE))
    print_divider()
    total = data["total_tasks"]
    rows = [
        ("Complete",              data["completed"],  GREEN),
        ("Incomplete",            data["incomplete"], RED),
        ("Skipped",               data["skipped"],    YELLOW),
        ("Postponed",             data["postponed"],  PURPLE),
        ("Abandoned: needs update", data["abandoned"], RED),
        ("Planned",               data["planned"],    BLUE),
    ]
    for label, count, color in rows:
        bar_len = int((count / total) * 30) if total else 0
        bar = colorize("█" * bar_len, color) + colorize("░" * (30 - bar_len), DIM)
        print(f"  {colorize(f'{label:<26}', DIM)} {bar}  {colorize(str(count), BOLD + color)}")
    print()
    print(colorize(f"  Total tasks logged: ", DIM) + colorize(str(total), BOLD + WHITE))
    print()

    # Goals summary
    print(colorize("  Goals", BOLD + WHITE))
    print_divider()
    print(colorize(f"  Total: ", DIM) + colorize(str(data["total_goals"]), BOLD + WHITE) +
          colorize("   Active: ", DIM) + colorize(str(data["active_goals"]), BOLD + CYAN) +
          colorize("   Achieved: ", DIM) + colorize(str(data["achieved_goals"]), BOLD + GREEN))
    print()

    # Streak leaderboard
    if data["goals_with_streaks"]:
        print(colorize("  Streak Leaderboard", BOLD + WHITE))
        print_divider()
        for i, goal in enumerate(data["goals_with_streaks"][:5], 1):
            streak = goal.get("streak", 0)
            print(f"  {colorize(str(i) + '.', DIM)} {goal['title']:<30} {colorize_streak(streak)}")
        print()

    # Most productive day
    print(colorize("  Most Productive Day", BOLD + WHITE))
    print_divider()
    print(colorize(f"  {data['best_day']}", BOLD + GREEN))
    print()

    # Journal
    print(colorize(f"  Journal entries written: ", DIM) + colorize(str(data["journal_count"]), BOLD + WHITE))
    print()

# ─── STARTUP SUMMARY ──────────────────────────────────────────────────────────

def section_label(label, color=WHITE):
    line = f"  -- {label} " + "-" * max(0, 34 - len(label))
    print(colorize(line, BOLD + color))

def print_startup_summary(summary, upcoming, overdue, goals, endangered_streaks, user_name="", generated=None):
    import datetime
    today_str = datetime.date.today().strftime("%A, %B %d %Y")
    time_str  = datetime.datetime.now().strftime("%I:%M %p")

    print()
    print_banner_with_tagline()
    print()

    # Welcome + date/time
    if user_name:
        print(colorize(f"  Welcome back, {user_name}!", BOLD + WHITE))
    print(colorize(f"  {today_str}", WHITE) + colorize(f"  |  {time_str}", DIM))
    print()
    print_divider()
    print()

    # AUTO-GENERATED
    if generated:
        section_label("AUTO-GENERATED", GREEN)
        for title in generated:
            print(colorize(f"    + {title}", GREEN))
        print()

    # TODAY
    section_label("TODAY", CYAN)
    if summary["total"] == 0:
        print(colorize("    No tasks planned for today.", DIM))
    else:
        print(
            colorize(f"    {summary['planned']} planned", BLUE) + "   " +
            colorize(f"{summary['completed']} complete", GREEN) + "   " +
            colorize(f"{summary['incomplete']} incomplete", RED) + "   " +
            colorize(f"{summary['skipped']} skipped", YELLOW)
        )
        rate = summary["completion_rate"]
        rate_color = GREEN if rate >= 70 else YELLOW if rate >= 40 else RED
        print(colorize(f"    Completion rate: ", DIM) + colorize(f"{rate}%", BOLD + rate_color))
    print()

    # ALERTS
    alerts = []
    if summary.get("not_updated", 0) > 0:
        alerts.append((RED, f"{summary['not_updated']} task(s) need updating from yesterday"))
    for task in overdue:
        alerts.append((RED, f"Overdue: {task['title']} (was {task['scheduled_time']})"))
    if alerts:
        section_label("ALERTS", RED)
        for color, msg in alerts:
            print(colorize(f"    ! {msg}", color))
        print()

    # STREAKS
    if endangered_streaks:
        section_label("STREAKS", YELLOW)
        for goal in endangered_streaks:
            print(colorize(f"    ~ {goal['title']}  -  {goal.get('streak', 0)} day streak at risk", YELLOW))
        print()

    # COMING UP
    if upcoming:
        section_label("COMING UP", CYAN)
        for task, minutes in upcoming:
            print(colorize(f"    > {task['title']} at {task['scheduled_time']}  -  in {minutes} min", CYAN))
        print()

    # GOALS
    active_goals = [g for g in goals if g["status"] == "Active"]
    if active_goals:
        section_label("GOALS", PURPLE)
        print(colorize(f"    {len(active_goals)} active goal(s)", PURPLE))
        for goal in active_goals[:3]:
            streak = goal.get("streak", 0)
            streak_str = colorize(f"  ({streak}d streak)", GREEN) if streak > 0 else ""
            print(colorize(f"    · {goal['title']}", DIM) + streak_str)
        if len(active_goals) > 3:
            print(colorize(f"    · ...and {len(active_goals) - 3} more", DIM))
        print()

    print_divider()


# ─── FIRST RUN ────────────────────────────────────────────────────────────────

def print_first_run_welcome():
    clear_screen()
    print()
    print_banner_with_tagline()
    print()
    print(colorize("  Welcome! Let's get you set up.", BOLD + WHITE))
    print()
    print_divider()
    print()


# ─── MENUS ────────────────────────────────────────────────────────────────────

def print_main_menu(user_name="", endangered_streaks=None):
    if endangered_streaks is None:
        endangered_streaks = []

    print_banner()
    print()

    if user_name:
        print(colorize(f"  Hey {user_name} 👋", WHITE))
        print()

    # Streak warning in main menu
    if endangered_streaks:
        print(colorize(f"  🔥 Streak alert — {len(endangered_streaks)} goal(s) at risk today!", BOLD + YELLOW))
        for goal in endangered_streaks:
            print(colorize(f"     · {goal['title']} — {goal.get('streak', 0)} day streak", YELLOW))
        print()

    options = [
        ("1", "Today's Tasks",  "plan, log, and manage today"),
        ("2", "Goals",          "set and track your goals"),
        ("3", "Journal",        "write and read journal entries"),
        ("4", "All Tasks",      "browse tasks across all dates"),
        ("5", "Analytics",      "completion rates, streaks, and patterns"),
        ("h", "Help",           "how to use DayKeep"),
        ("q", "Quit",           "exit the app"),
    ]
    for key, label, desc in options:
        print(f"  {colorize(key, BOLD + CYAN)}  {colorize(label, WHITE):<22} {colorize(desc, DIM)}")
    print()

def print_help():
    sections = [
        ("TODAY'S TASKS", [
            ("1 → Today",         "View and manage all tasks for today"),
            ("Add task",          "Plan a new task — title, time, category, goal link"),
            ("Mark complete",     "Type the task ID and update its status"),
            ("Overdue alerts",    "Shown on startup for missed scheduled tasks"),
            ("Upcoming",          "Tasks within the next 2 hours shown on startup"),
            ("Notes",             "Notes stack — each note is saved individually"),
            ("Postpone",          "Move a task to a future date — history is saved"),
        ]),
        ("GOALS", [
            ("2 → Goals",         "View all your goals"),
            ("Add goal",          "Set a goal with category, sub-category, and target date"),
            ("Target date",       "Pick by season, by year, or enter manually"),
            ("Streak",            "Routine tasks linked to a goal build a streak"),
            ("Statuses",          "Active, Achieved, Abandoned, Initialized as Cancelled"),
        ]),
        ("JOURNAL", [
            ("3 → Journal",       "Open today's journal or browse past entries"),
            (".save",             "Save and finish your entry"),
            (".undo",             "Delete the last line"),
            (".undo [#]",         "Delete a specific line by number"),
            (".edit [#]",         "Edit a specific line"),
            (".quit",             "Cancel — warns if unsaved changes exist, .quit again to confirm"),
        ]),
        ("NAVIGATION", [
            (".quit",             "Cancel and exit to main menu"),
            (".back",             "Go back to the previous screen"),
            (".main",             "Go directly to the main menu"),
            ("0 or Cancel",       "Cancel a picker selection"),
        ]),
        ("GENERAL", [
            ("h",                 "Open this help screen"),
            ("q",                 "Quit the app"),
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