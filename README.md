# 🗓 DayKeep — Daily Accountability Tracker

> *Keep your day. Keep your word.*

A personal Python CLI tool built to solve a real problem — holding yourself accountable to what you plan, tracking whether you followed through, and building streaks around the routines that matter most.

Built from a real experience: arriving at Fisk University as a spring student with no blueprint, no orientation, and quickly getting overwhelmed saying yes to too many things. A planner saved that semester. DayKeep is that planner, built properly.

---

## What It Does

- **Goals** — set goals with categories, sub-categories, target dates, and routine tracking. Goals build streaks when you show up consistently
- **Today's Tasks** — plan your day, log what you did, manage notes, postpone tasks with full history
- **Journal** — write daily entries with a line-by-line editor. Past entries are read-only with full timestamp history
- **Analytics** — completion rates, streak leaderboard, task breakdown, most productive day
- **Auto-generation** — routine tasks linked to goals are created automatically every morning
- **Accountability** — tasks not updated by midnight are flagged as Abandoned and must be resolved before the app opens
- **Export** — export tasks and goals to CSV for Excel or Google Sheets

---

## How to Run

**Requirements:** Python 3.8 or higher. No third-party packages — everything uses Python's built-in standard library.

```bash
# Clone the repo
git clone https://github.com/fortdominz/daykeep.git

# Navigate into the folder
cd daykeep

# Run the app
python main.py
```

The app will ask for your name on first run and create `daykeep.json` automatically.

---

## Navigation

| Command | Action |
|---|---|
| `.quit` | Cancel and exit to main menu |
| `.back` | Go back to previous screen |
| `.main` | Jump directly to main menu |
| `.` | Skip a field during updates |
| `0` or `q` | Cancel a picker selection |

### Journal Editor Commands

| Command | Action |
|---|---|
| `.save` | Save and finish the entry |
| `.undo` | Delete the last line |
| `.undo [#]` | Delete a specific line |
| `.edit [#]` | Edit a specific line |
| `.quit` | Cancel — warns if unsaved changes exist |

---

## Project Structure

```
daykeep/
├── db.py        # All data storage — reads and writes to daykeep.json
├── models.py    # Data models and validation for Goals, Tasks, and Journal Entries
├── ui.py        # Everything visual — colors, tables, menus, prompts, editor
├── main.py      # All screens and app flow — the entry point
└── .gitignore   # Excludes personal data and cache files
```

> `daykeep.json` is excluded via `.gitignore` — it contains your personal data and is created automatically on first run.

---

## Build Roadmap

| Phase | Name | Status |
|---|---|---|
| Phase 1 | Core Data Layer | Complete |
| Phase 2 | CLI Menu and Navigation | Complete |
| Phase 3 | CRUD Deep Dive and Polish | Complete |
| Phase 4 | Planning and Accountability | Complete |
| Phase 5 | Polish and CSV Export | Complete |
| Future | MongoDB Migration | Planned |
| Future | FastAPI Backend | Planned |
| Future | Web Platform | Planned |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| `json` module | Reading and writing data to a local file |
| `os` module | File existence checks, terminal clearing |
| `datetime` module | Date validation, streak logic, overdue detection |
| `csv` module | CSV export for tasks and goals |
| `sys` module | Clean app exit |
| ANSI escape codes | Terminal colors and formatting |
| JSON file | Local data storage — MongoDB planned |

---

## Notes

- Built from scratch as part of a structured personal development roadmap
- Standard library only — no pip installs required
- Data layer is intentionally isolated for clean MongoDB migration later
- Commit history follows the build phases

---

*Built by [@fortdominz](https://github.com/fortdominz)*
