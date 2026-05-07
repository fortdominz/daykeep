# Project Reflection — DayKeep

**Project type:** Full-stack web app  
**Stack:** FastAPI, React, Vite, Python, JSON file (db.py)  
**Live at:** https://daykeep.dominioneze.dev  
**Repo:** https://github.com/fortdominz/daykeep  
**Deployed:** May 2026  
**Built by:** Dominion Eze

---

## Overview

DayKeep is a personal accountability app that tracks goals, tasks, and journal entries with a real-time dashboard. It started as a Python CLI tool and became a full-stack web app with a FastAPI backend and a React + Vite frontend. The core idea: one place to set goals, schedule tasks, log your day in a journal, and see how consistent you actually are — with streaks, stale-task detection, and mood tracking baked in.

---

## The Journey

### Why it was built

I needed something I'd actually use to stay accountable. Most productivity apps are either too generic or locked behind subscriptions. DayKeep was built to track my specific workflow: daily goals tied to habits, tasks that could be scheduled or postponed, and a journal that captures the day without pressure. The CLI came first because that was fastest to ship. The web version came because I wanted to use it without opening a terminal every time.

### What was built

- **Dashboard** — summary of today's tasks, upcoming tasks (within 2 hours), overdue tasks, endangered streaks, and abandoned task count
- **Goals** — create goals with category, subcategory, target date, status, and optional routine flag + routine time; streak tracking auto-updates when routine tasks are marked complete
- **Tasks** — create/edit/delete tasks with date, category, scheduling, goal linkage, notes stacking, and postpone history (full history stored in `postpone_history`)
- **Journal** — multiple entries per day; today's entries are live-editable; past entries are read-only with a full-screen modal view; mood stored as string "1"–"5" mapped to emoji labels
- **Analytics** — task completion rates, goal progress, mood trend
- **Export** — CSV export for tasks and goals via `/api/export/tasks` and `/api/export/goals`
- **React frontend** — sidebar nav, dark slate + amber design, custom CSS properties (no framework), ErrorBoundary per route, `← Back` button on all non-dashboard pages
- **FastAPI backend** — all CRUD endpoints, CORS configured for `daykeep.dominioneze.dev` and localhost dev ports

### Deployment

- Backend on **Render** (`daykeep` service) — start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Frontend on **Vercel** (`daykeep` project) — build root: `frontend`, env var `VITE_API_URL` = Render backend URL
- Custom domain: `daykeep.dominioneze.dev` — CNAME record in Namecheap pointing to Vercel's domain-specific value from Vercel's Settings → Domains panel

---

## What I Learned About Full-Stack Field Mapping

The biggest technical trap in this project was the mismatch between how the CLI stored data and what the API expected. `models.py` stores journal entries under the key `content`, not `text`. Mood is stored as a string `"1"`–`"5"`, not an integer. I originally wired the FastAPI journal endpoints to call the CLI's model functions directly — those functions enforced strict category lists and field names designed for terminal input, not HTTP JSON bodies. Every journal save returned a 500.

The fix was simple once I understood the problem: stop calling CLI model functions from the API layer. Build the dicts directly in `api.py`, use the exact field names db.py expects, and convert mood to `str()` before storing. After that, the frontend also needed a `getEntryText()` guard function that checks `entry.content || entry.text || entry.entry` to handle entries written under different field names by different versions.

The lesson: when you adapt a CLI to a web backend, the model layer you built for the terminal is not your API layer. They solve different problems.

---

## Architectural Decisions

**Why FastAPI over Flask?**  
FastAPI gives me Pydantic model validation and automatic docs out of the box. For a CRUD app with several request body shapes (GoalCreate, GoalUpdate, TaskCreate, TaskUpdate, etc.), the `BaseModel` approach makes the input contract explicit. Flask would have needed manual validation on every route. FastAPI also runs async natively, which matters later if I add real-time features.

**Why JSON file storage instead of a database?**  
DayKeep is a personal tool with a single user. A SQLite or Postgres setup would add migration complexity for no functional gain at this stage. `db.py` handles all reads and writes, so the storage layer is fully isolated — swapping to MongoDB Atlas later means rewriting only `db.py`, not the API or frontend. That isolation was intentional from the CLI version and it held up.

**Why build dict directly in api.py instead of calling CLI model functions?**  
The CLI model functions (in `models.py`) were written for terminal input — they validated against category enums, reformatted strings, and assumed a specific execution flow. Using them in the API layer meant every web request had to satisfy CLI constraints. Bypassing them and building dicts directly in `api.py` keeps the web API clean while leaving the CLI intact. Both layers share `db.py` — that's the only coupling that matters.

**Why `VITE_API_URL` as an env var instead of hardcoding?**  
The Vite proxy handles `/api` → `localhost:8080` in dev. In production, the same `api.js` file needs to point to the Render backend. Using `import.meta.env.VITE_API_URL` means zero code changes between environments — just set the env var in Vercel's dashboard. This is the standard Vite pattern and it worked exactly as expected.

**Why Render for the backend instead of Railway?**  
Consistency. MusicTasteMatch already went to Render. Introducing Railway would mean managing accounts, dashboards, and billing on two platforms for no technical reason. Render handles FastAPI well (just set the start command and port), so it's the standard for all my backends going forward.

---

## AI Collaboration — One Instance Where It Worked Well

The journal UX redesign. The original journal was a single entry per day — open, edit, save, done. I described what I actually wanted: multiple entries per day, today's entries stay editable with inline forms per entry, past entries become read-only cards that open into a full-screen modal. That's a non-trivial state machine — `formMode` switching between null, `'new'`, and a specific entry object, separate rendering logic for today vs. past entries, and a `PastEntryModal` overlay. AI collaboration produced a working `Journal.jsx` with all of that on the first pass. The component structure was clean enough that I could reason about it immediately — I didn't have to untangle anything.

---

## AI Collaboration — One Instance Where It Fell Short

The CNAME setup. I was given `cname.vercel-dns.com` as the CNAME value to enter in Namecheap. That's the generic Vercel DNS value — it doesn't work for custom subdomains tied to a specific project. Namecheap threw "Failed to save record" and I was stuck. The correct value has to come from Vercel's Settings → Domains panel for the specific project. AI gave me a generic answer when the correct answer required navigating to the right UI to get a project-specific value. The lesson: for steps that involve external dashboards generating unique values, AI can't substitute for actually going to the dashboard and reading the value it gives you.

---

## What Surprised Me About Building and Testing This

How many small things broke at the boundary between dev and prod. Locally, the Vite proxy forwarded `/api` cleanly to port 8080, and the app felt seamless. In production, `VITE_API_URL` had to be set or every API call would 404 against the Vercel frontend origin. CORS had to include `https://daykeep.dominioneze.dev` explicitly or every request would be blocked. None of these were hard to fix, but none of them showed up during local dev. The dev-to-prod gap on full-stack apps is always wider than it looks.

The other surprise: PowerShell's execution policy blocked `npm run dev` entirely on the Windows machine. The fix — calling `node node_modules/vite/bin/vite.js` directly — felt like a hack but it's just bypassing the policy restriction. Updated `package.json` scripts to use that pattern so it just works.

---

## Could This System Be Misused? How Would You Prevent It?

Right now, DayKeep has no authentication. Anyone with the Render backend URL can read, write, or delete all goals, tasks, and journal entries. The data includes journal content and mood logs — genuinely personal information.

For a single-user personal tool deployed on a private subdomain, the risk is low in practice. But if I opened this to multiple users or made the backend URL discoverable, the attack surface is wide open.

To harden it for real use: add JWT-based auth to FastAPI (FastAPI's `HTTPBearer` dependency is the right entry point), gate every endpoint behind a token check, and store the token in `localStorage` on the frontend (with a proper login flow). Rate limiting on the journal and task creation endpoints would also prevent abuse. The export endpoints especially need auth — they dump all data to CSV with a single GET request.

---

## What Would I Do Differently If I Rebuilt This From Scratch?

- Start with a real database (SQLite at minimum) instead of a JSON file — auto-incrementing IDs and atomic writes matter more than I initially thought
- Separate the CLI and web backend from day one — don't share `models.py` between terminal UX code and API validation
- Add auth before the first deploy, not as a future concern
- Use React Query or SWR for data fetching instead of raw `fetch` — the loading/error/refetch cycle gets repetitive fast
- Design the mood field as an integer in the database from the start — coercing between string and int at the boundary is a small but persistent annoyance

---

## What's the One Thing This Project Taught Me That a Tutorial Never Would?

Adapting a CLI to a web backend is not just "add a framework on top." The CLI was designed for interactive flow — the user types, the program asks questions, validates, and responds. That flow is encoded in the functions and the data shapes. When you move to HTTP, the client sends a complete JSON body and expects a complete JSON response. The validation rules that made sense for terminal prompts (strict category lists, required fields enforced mid-conversation) become obstacles in an API. I had to decide where each layer's responsibility actually ended, and that decision had real downstream consequences — it's why `api.py` builds dicts directly instead of delegating to `models.py`. No tutorial teaches you that. You learn it by running into 500 errors from your own code.

---

## As a System Architect

- **Data flow:** React frontend → `api.js` fetch calls → FastAPI routes → `db.py` read/write → `daykeep.json` — clean layering, each layer owns one thing
- **Deployment pipeline:** Push to GitHub → Render auto-deploys backend (connected to repo) → Vercel auto-deploys frontend → both live at custom subdomain within minutes
- **Layer boundaries:** `db.py` owns all file I/O and query logic. `api.py` owns HTTP contracts, validation, and response shaping. `models.py` owns CLI-specific logic only — it's not imported by `api.py` for anything data-critical. Frontend owns all rendering, state, and user interaction.
- **Highest-impact decision:** Using `db.py` as the single data access layer. If I'd let `api.py` read/write the JSON file directly, swapping to a real database later would require touching every route. Because all persistence goes through `db.py`, the migration scope is one file.

## As an AI Engineer

- **No AI in DayKeep** — intentionally. Every feature is deterministic: streak logic is date arithmetic, stale task detection is timestamp comparison, analytics are aggregations. These are rule-based by design — predictable, auditable, and fast with zero API cost.
- **Where AI was used:** AI collaboration was used in the development process (writing components, debugging), not in the product itself. That distinction matters — the product's behavior is fully deterministic.
- **What this means for reliability:** DayKeep will behave identically on day 1 and day 1000. No model drift, no prompt sensitivity, no quota concerns. For a personal accountability tool, that's the right call.
- **If AI were added:** The one natural fit would be a weekly reflection prompt — "based on your task completion and mood this week, here's a pattern." That would be a single Gemini call on a summarized weekly snapshot, not live inference on every action.

---

## Wins

- Shipped a real full-stack app from scratch — FastAPI backend, React frontend, custom domain, live in production
- Designed and implemented a 4-screen app (Dashboard, Goals, Tasks, Journal) with consistent dark slate + amber design and no CSS framework
- Journal redesign — multiple entries per day, today editable, past read-only with full-screen modal — solid UX delivered without overengineering
- ErrorBoundary pattern: route-level crash isolation means one broken component doesn't kill the whole app
- Got the dev-to-prod environment config right: Vite proxy in dev, `VITE_API_URL` in production — zero code changes between environments
- Locked in hosting standard: Vercel (frontend) + Render (backend) for all future projects

## Hiccups

- **Port 8001 WinError 10013**: Port was reserved on the Windows machine — switched to 8080, updated Vite proxy and CORS config
- **PowerShell execution policy blocked npm**: `npm run dev` failed silently — fixed by calling `node node_modules/vite/bin/vite.js` directly in package.json scripts
- **Journal 500 error**: `api.py` was trying to call CLI model functions that enforced strict category lists — fixed by building dicts directly in `api.py` with the correct field names (`content` not `text`, mood as string)
- **Journal blank page + nav crash**: Missing error boundary — added `ErrorBoundary` class component wrapping each route in `App.jsx`
- **Wrong CNAME value**: Gave generic `cname.vercel-dns.com` instead of the project-specific value from Vercel's Settings → Domains — fixed by going to the dashboard and reading the actual value
- **Sidebar showed "daykeep.app"**: Changed to "DayKeep" — user doesn't own that domain
