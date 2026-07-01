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

<!-- Fill in during/after implementation (Phases 2-5). -->
- One change I made after AI review: I added the **`ScheduledTask`** class rather than mutating `Task` objects with start/end times. The AI pointed out that storing schedule-specific fields on `Task` would tangle "what the task is" with "when it happened to be placed today," making recurring tasks and re-planning harder. Separating them keeps `Task` reusable across days.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One deliberate tradeoff: **conflict detection only flags *exact* `preferred_time` matches, not overlapping durations.** If a 30-minute walk is set for 08:00 and a 10-minute feeding is set for 08:15, `Scheduler.detect_conflicts` will *not* warn, even though they actually overlap in real time — it only fires when two tasks claim the identical "HH:MM" slot.

This is reasonable for the scenario because most pet owners think in round, distinct time slots ("morning walk at 8, feeding at 8:30"), so exact-match catches the common mistake of double-booking a slot while keeping the logic simple, fast (a single dictionary pass), and easy to explain. A second, related tradeoff is that `build_plan` lays tasks out *sequentially by priority* from the day's start rather than honoring each task's `preferred_time` — it optimizes for "fit the most important tasks into the available budget" over "put each task at its exact wished-for time." Full interval-overlap detection and preferred-time placement would be the natural next iteration if the app needed calendar-grade accuracy.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
