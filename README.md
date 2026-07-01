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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The scheduling intelligence lives in the `Scheduler` class in `pawpal_system.py`:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time` orders by `preferred_time` ("HH:MM"), untimed tasks last; `sort_tasks` orders by priority (high→low) then shorter duration first |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Filter by completion status, or narrow to a single pet's tasks; `build_plan` also filters out tasks that don't fit the time budget |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks that claim the same `preferred_time` slot and returns warning strings (never raises) — see reflection §2b for the exact-match tradeoff |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Completing a `daily`/`weekly` task auto-creates the next occurrence with `due_date` advanced via `datetime.timedelta` (`once` tasks return `None`) |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
