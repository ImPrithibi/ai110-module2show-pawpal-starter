# PawPal+ Project Reflection

## 1. System Design

**Three core actions a user should be able to perform:**

1. **Add a pet** — enter a pet's name, species, and basic details so the app knows who it is planning for.
2. **Add a care task to a pet** — record something that needs to happen (e.g. a walk, feeding, or medication) along with how long it takes and how important it is.
3. **Generate today's daily plan** — produce an ordered schedule that fits the owner's available time, and read the explanation of why each task was chosen and placed where it is.

**a. Initial design**

My initial UML has four core classes plus one small helper:

- **Owner** — the top-level entity. Holds the owner's name, scheduling constraints (`available_minutes`, `preferred_start`), and the list of pets. Responsible for managing pets (`add_pet`), routing tasks to the right pet (`add_task`), and gathering every task across all pets (`all_tasks`).
- **Pet** — a `dataclass` holding identity info (name, species, breed, age) and its own list of tasks. Responsible only for owning its tasks (`add_task`); it is mostly a data container.
- **Task** — a `dataclass` representing one unit of care (title, duration, priority, category, recurrence, optional preferred time). Knows how to rank its own priority (`priority_rank`).
- **Scheduler** — the "brains." Given a list of tasks and a time budget, it sorts them (`sort_tasks`), expands recurring tasks for a given day (`expand_recurring`), builds the timed plan (`build_plan`), detects overlap conflicts (`detect_conflicts`), and explains the result (`explain_plan`).
- **ScheduledTask** — a small `dataclass` that wraps a `Task` with a concrete `start_time`, `end_time`, and a `reason`. This keeps the original `Task` immutable-ish and gives the "explain the plan" requirement a clean place to live.

Relationships: an Owner *has many* Pets, a Pet *has many* Tasks, and the Scheduler *reads* Tasks and *produces* ScheduledTasks. I deliberately kept data (Pet/Task) separate from behavior (Owner/Scheduler) so the scheduling logic stays in one place and is easy to test on its own.

**b. Design changes**

Yes, the design evolved during implementation:

- **Added a `ScheduledTask` class** rather than mutating `Task` objects with start/end times. Storing schedule-specific fields on `Task` would tangle "what the task is" with "when it happened to be placed today," making recurring tasks and re-planning harder. Separating them keeps `Task` reusable across days.
- **Added `due_date` and `next_occurrence()` to `Task`** once I reached the recurring-task feature (Phase 4). My initial skeleton only had a `recurrence` string; I discovered I also needed an actual date to advance with `timedelta`, so recurrence became real behavior instead of just a label.
- **Changed `detect_conflicts` to operate on `Task` lists (by `preferred_time`) instead of on the built plan.** My first version checked for overlaps in the generated plan, but since `build_plan` lays tasks out back-to-back, that version could never actually fire. Checking the owner's *intended* times is what surfaces a real double-booking.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three constraints:

1. **Time budget** — the owner's `available_minutes`. `build_plan` never schedules more total task time than the owner actually has.
2. **Priority** — `high` / `medium` / `low`. When everything can't fit, higher-priority tasks are kept and lower-priority ones are dropped.
3. **Preferences** — each task's `preferred_time`, used for chronological display and for detecting double-booked slots.

I decided **time budget matters most**, because the whole point of the app is a *busy* owner who can't do everything — the plan has to be realistic first. **Priority is the tie-breaker** that decides *what* to cut when time runs short. Preferences are treated as softer hints (surfaced as conflict warnings and sort order) rather than hard placement rules, which keeps the plan feasible even when the owner's wished-for times are unrealistic.

**b. Tradeoffs**

One deliberate tradeoff: **conflict detection only flags *exact* `preferred_time` matches, not overlapping durations.** If a 30-minute walk is set for 08:00 and a 10-minute feeding is set for 08:15, `Scheduler.detect_conflicts` will *not* warn, even though they actually overlap in real time — it only fires when two tasks claim the identical "HH:MM" slot.

This is reasonable for the scenario because most pet owners think in round, distinct time slots ("morning walk at 8, feeding at 8:30"), so exact-match catches the common mistake of double-booking a slot while keeping the logic simple, fast (a single dictionary pass), and easy to explain. A second, related tradeoff is that `build_plan` lays tasks out *sequentially by priority* from the day's start rather than honoring each task's `preferred_time` — it optimizes for "fit the most important tasks into the available budget" over "put each task at its exact wished-for time." Full interval-overlap detection and preferred-time placement would be the natural next iteration if the app needed calendar-grade accuracy.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI as a pair-programmer across the whole workflow: brainstorming the UML in Phase 1, scaffolding the class skeletons, fleshing out the `Scheduler` algorithms, drafting the pytest suite, and writing documentation. The most helpful prompts were **specific and grounded in my own files** — e.g. "based on my skeleton, how should the Scheduler get all tasks from the Owner's pets?" and "what edge cases matter for a pet scheduler with sorting and recurring tasks?" Open-ended prompts produced generic code; prompts that referenced my actual class names and constraints produced code that dropped straight into the project.

**b. Judgment and verification**

I did not accept the AI's first conflict-detection approach as-is. It initially checked for overlaps in the *generated plan*, but I realized that because `build_plan` places tasks back-to-back, that check could never actually trigger a warning. I rejected it and re-scoped conflict detection to compare the owner's *intended* `preferred_time` values instead.

I verified AI output three ways: (1) running `main.py` after every change to eyeball the CLI output, (2) running `python -m pytest` so the 15 tests caught regressions, and (3) reading the code myself rather than trusting it — which is exactly how I caught the dead conflict-detection logic.

---

## 4. Testing and Verification

**a. What you tested**

The 15-test suite in `tests/test_pawpal.py` covers: task completion (`mark_complete`), task ownership (adding to a pet, aggregating across pets, rejecting unknown pets), chronological sorting (including untimed-tasks-last), filtering by status and by pet, recurring rollover (daily → +1 day, weekly → +7 days, one-off → nothing), duplicate-time conflict detection (and the no-false-positive case), and budget-aware planning plus the empty-list edge case.

These mattered because they are exactly the behaviors a user *relies on*: if sorting, budgeting, or recurrence silently broke, the daily plan would be wrong in ways that are hard to notice by eye. Testing them locks in the core promises of the app.

**b. Confidence**

Fairly confident — **4/5**. Every core behavior has at least one test and they all pass, including edge cases like empty task lists and untimed tasks. If I had more time I'd test: tasks whose duration exactly equals the remaining budget (boundary condition), invalid time strings like `"25:99"`, very large task lists for performance, and interval *overlap* conflicts (not just exact-slot matches, which is my known tradeoff in §2b).

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the **clean separation between data (`Pet`/`Task`) and behavior (`Owner`/`Scheduler`)**. Because all the logic lived in one place, the CLI-first workflow paid off: I could verify everything through `main.py` and pytest before ever touching the UI, and wiring `app.py` to the backend in Phase 3 was almost trivial since the methods already did the work.

**b. What you would improve**

I'd make `build_plan` actually honor `preferred_time` (placing tasks at their wished-for slots and detecting *real* overlaps) instead of laying them out sequentially. I'd also add input validation for time strings and edit/delete controls in the UI, and probably persist data to a JSON file so pets and tasks survive between runs.

**c. Key takeaway**

The biggest lesson was about **being the architect, not just the typist**. AI could generate plausible code instantly, but it happily wrote a conflict-detection method that could never fire. My job was to hold the mental model of how the pieces fit, catch that kind of subtle dead logic, and decide what "correct" meant — the AI accelerated the work, but the judgment about design and correctness had to stay with me.

---

## 6. AI Strategy (Phase 6)

- **Most effective AI features:** agent/multi-file editing was the biggest win — it could add a method to `Task`, update `Scheduler`, and adjust `main.py` in one coherent change. Grounded chat (attaching my actual files and asking targeted questions) and test generation were close behind.
- **A suggestion I modified:** the first `detect_conflicts` checked the built plan for overlaps; since `build_plan` schedules tasks back-to-back, it could never warn. I re-scoped it to compare tasks' `preferred_time` values so it catches genuine double-bookings.
- **Separate chat sessions per phase:** keeping design, algorithms, and testing in separate contexts stopped earlier scaffolding from muddying later prompts. A focused "testing only" session, for example, produced a much sharper edge-case list than one giant thread would have.
- **What I learned as lead architect:** powerful AI shifts the bottleneck from *writing* code to *judging* it. The most valuable things I did were setting the design boundaries (data vs. behavior), defining what to verify, and reviewing output critically — the AI was fastest when I gave it a clear structure to fill in, and riskiest when I let it decide the structure.
