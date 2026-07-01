# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent (Claude Code) to add a third algorithmic capability beyond the core requirements: a "next available slot" finder that, given the current day's plan and a desired task duration, returns the earliest free time the task could start without overlapping already-scheduled tasks.

**What did the agent do?**

- **Files modified:** `pawpal_system.py` (added `Scheduler.next_available_slot()`), `tests/test_pawpal.py` (added 3 tests), `README.md` (documented the feature with CLI examples).
- Implemented an interval-gap scan: it sorts the busy intervals, walks a cursor through the day, and returns the first gap ≥ the requested duration (or `None` if the day is full before `day_end`).
- Wrote tests for three cases — a gap between tasks, an empty plan (returns day start), and a full day (returns `None`) — and ran `python -m pytest` to confirm all 18 tests pass.

**What did you have to verify or fix manually?**

I verified the boundary behavior myself with a quick scratch script before trusting it: I checked that a gap exactly equal to the duration counts as a fit (`>=`, not `>`), and that when a gap is too small the cursor correctly advances past the busy interval instead of getting stuck. I also confirmed the `day_end` cutoff actually returns `None` rather than a time past the end of the day.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
