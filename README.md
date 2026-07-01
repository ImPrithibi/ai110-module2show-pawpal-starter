# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Owner & pet management** — one owner manages multiple pets, each with its own task list (`Owner`, `Pet`).
- **Rich tasks** — every task tracks duration, priority, category, recurrence, an optional preferred time, completion status, and a due date (`Task`).
- **Sorting by time** — tasks display in chronological order; untimed tasks fall to the end (`Scheduler.sort_by_time`).
- **Filtering** — narrow tasks by completion status or by a single pet (`Scheduler.filter_by_status`, `filter_by_pet`).
- **Budget-aware daily plan** — greedily selects the highest-priority tasks that fit the owner's time budget, lays them out from the day's start, and explains its reasoning (`Scheduler.build_plan`, `explain_plan`).
- **Conflict warnings** — flags tasks that claim the same preferred time slot without crashing (`Scheduler.detect_conflicts`).
- **Daily / weekly recurrence** — completing a recurring task auto-creates its next occurrence with the due date advanced via `datetime.timedelta` (`Scheduler.mark_task_complete`, `Task.next_occurrence`).
- **Streamlit UI** — add pets/tasks, see live per-pet task tables and conflict banners, and generate today's plan, all backed by `st.session_state` persistence.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Below is the terminal output from running the CLI demo (`python main.py`), which
exercises sorting, filtering, conflict detection, recurring rollover, and the plan:

```
🕒 Tasks sorted by time:
  • 08:00  Morning walk [high]
  • 08:00  Breakfast [high]
  • 12:00  Litter scoop [medium]
  • 17:00  Play / enrichment [low]

🔎 Only Mochi's tasks:
  • 08:00  Morning walk [high]
  • 08:00  Breakfast [high]

🔎 Incomplete tasks only:
  • 08:00  Morning walk [high]
  • 08:00  Breakfast [high]
  • 17:00  Play / enrichment [low]
  • 12:00  Litter scoop [medium]

⚠️  Conflict check:
   - Time conflict at 08:00: 'Morning walk' and 'Breakfast'

🔁 Recurring task rollover:
   Completed 'Morning walk' (due 2026-06-30).
   Auto-created next 'Morning walk' due 2026-07-01.

🐾 Today's Schedule for Jordan
   (time budget: 90 min, start: 08:00)
------------------------------------------------
  08:00–08:10  Breakfast (10 min) [high]
  08:10–08:20  Litter scoop (10 min) [medium]
  08:20–08:40  Play / enrichment (20 min) [low]
------------------------------------------------
Here is the reasoning behind today's plan:
  - 08:00: Breakfast — high priority; fits with 80 min budget left
  - 08:10: Litter scoop — medium priority; fits with 70 min budget left
  - 08:20: Play / enrichment — low priority; fits with 50 min budget left
Total free time remaining: 50 min.
```

## 🧪 Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`) covers:

- **Task basics** — `mark_complete()` flips completion status; adding a task grows a pet's task list.
- **Owner aggregation** — `all_tasks()` spans multiple pets; adding a task to an unknown pet raises a clear error.
- **Sorting** — `sort_by_time()` returns tasks in chronological order and pushes untimed tasks last.
- **Filtering** — `filter_by_status()` drops completed tasks; `filter_by_pet()` narrows to one pet.
- **Recurrence** — completing a daily task creates a fresh task due the next day; weekly advances 7 days; a one-off task creates nothing.
- **Conflict detection** — duplicate `preferred_time` slots are flagged; distinct times are not.
- **Daily plan / edge cases** — `build_plan()` respects the time budget; an empty task list yields an empty plan instead of an error.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
collected 15 items

tests/test_pawpal.py ...............                                     [100%]

============================== 15 passed in 0.01s ==============================
```

**Confidence level: ⭐⭐⭐⭐☆ (4/5).** All 15 tests pass and cover every core
behavior including edge cases (no tasks, untimed tasks, duplicate slots). One
star is held back because conflict detection only catches exact time-slot
matches (not overlapping durations), and `build_plan` uses sequential rather
than preferred-time placement — see reflection §2b.

## 📐 Smarter Scheduling

The scheduling intelligence lives in the `Scheduler` class in `pawpal_system.py`:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time` orders by `preferred_time` ("HH:MM"), untimed tasks last; `sort_tasks` orders by priority (high→low) then shorter duration first |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Filter by completion status, or narrow to a single pet's tasks; `build_plan` also filters out tasks that don't fit the time budget |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks that claim the same `preferred_time` slot and returns warning strings (never raises) — see reflection §2b for the exact-match tradeoff |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Completing a `daily`/`weekly` task auto-creates the next occurrence with `due_date` advanced via `datetime.timedelta` (`once` tasks return `None`) |

## 🚀 Optional Extensions

### Challenge 3 — Priority-based scheduling

`Scheduler.sort_tasks()` sorts by **priority first, then preferred time, then duration**, so within a priority band tasks still fall in chronological order. `build_plan()` uses this ordering to decide which tasks to keep when the time budget is tight.

```
Priority-first, then time:
  [  high] 08:00  Morning walk
  [  high] 12:00  Meds
  [medium] 09:00  Litter scoop
  [   low] 17:00  Evening play
```

### Challenge 1 — "Next available slot" finder

`Scheduler.next_available_slot(plan, duration_minutes, day_end)` scans the gaps between already-scheduled tasks (and the time after the last one) and returns the earliest `HH:MM` where a new task of the given length fits without overlapping — or `None` if the day is too full. This goes beyond back-to-back planning by reasoning about real time intervals.

```
Busy: 08:00–08:30 Walk, 09:00–09:15 Meds
  next slot for a 20-min task -> 08:30   (fits the 08:30–09:00 gap)
  next slot for a 40-min task -> 09:15   (no gap fits; goes after Meds)
```

## 🎬 Demo Walkthrough

### Main UI features

Launch the app with `streamlit run app.py`. The page lets a pet owner:

- **Set owner & day settings** — name, daily time budget (minutes), and preferred start time. Data persists across reruns via `st.session_state`.
- **Add a pet** — name, species, breed, age (duplicate names are rejected).
- **Add a task** — pick the pet, then set title, duration, category, priority, recurrence, and an optional preferred time.
- **See per-pet task tables** — each pet's tasks render in chronological order, with a completion column and a warning banner if any two tasks share the same time slot.
- **Generate today's plan** — a budget-aware, priority-first schedule with start/end times, a conflict check, and an expandable "Why this plan?" explanation.

### Example workflow

1. Set the time budget to `90` min and start time to `08:00`.
2. Add a pet: **Mochi** (dog).
3. Add tasks for Mochi: **Morning walk** (30 min, high, 08:00) and **Breakfast** (10 min, high, 08:00).
4. Notice the ⚠️ conflict banner — both tasks want the 08:00 slot.
5. Add **Play / enrichment** (20 min, low, 17:00) and click **Generate schedule**.
6. Read the ordered plan and the "Why this plan?" reasoning; complete a daily task to roll it over to tomorrow.

### Key Scheduler behaviors shown

- **Sorting** — tasks appear in chronological order (`sort_by_time`).
- **Filtering** — completed tasks are dropped from the plan (`filter_by_status`).
- **Conflict warnings** — duplicate time slots are flagged, not crashed (`detect_conflicts`).
- **Budget planning + explanation** — highest-priority tasks that fit the budget are chosen and explained (`build_plan`, `explain_plan`).
- **Recurrence** — completing a daily/weekly task auto-creates the next occurrence (`mark_task_complete`).

### Sample CLI output (`python main.py`)

```
🕒 Tasks sorted by time:
  • 08:00  Morning walk [high]
  • 08:00  Breakfast [high]
  • 12:00  Litter scoop [medium]
  • 17:00  Play / enrichment [low]

🔎 Only Mochi's tasks:
  • 08:00  Morning walk [high]
  • 08:00  Breakfast [high]

⚠️  Conflict check:
   - Time conflict at 08:00: 'Morning walk' and 'Breakfast'

🔁 Recurring task rollover:
   Completed 'Morning walk' (due 2026-06-30).
   Auto-created next 'Morning walk' due 2026-07-01.

🐾 Today's Schedule for Jordan
   (time budget: 90 min, start: 08:00)
------------------------------------------------
  08:00–08:10  Breakfast (10 min) [high]
  08:10–08:20  Litter scoop (10 min) [medium]
  08:20–08:40  Play / enrichment (20 min) [low]
------------------------------------------------
Here is the reasoning behind today's plan:
  - 08:00: Breakfast — high priority; fits with 80 min budget left
  - 08:10: Litter scoop — medium priority; fits with 70 min budget left
  - 08:20: Play / enrichment — low priority; fits with 50 min budget left
Total free time remaining: 50 min.
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
