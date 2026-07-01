"""PawPal+ logic layer.

Core implementation of the four main classes (Owner, Pet, Task, Scheduler)
plus a small ScheduledTask result type. This is the CLI-first "brain" of the
app; the Streamlit UI in app.py connects to it later.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

# How far ahead each recurrence rule schedules the next occurrence.
RECURRENCE_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

# Ordering used to rank tasks; higher number = more important.
PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3}


def _to_minutes(hhmm: str) -> int:
    """Convert a 'HH:MM' string into minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(total_minutes: int) -> str:
    """Convert minutes since midnight back into a 'HH:MM' string."""
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


@dataclass
class Task:
    """A single pet-care activity (e.g. a walk, feeding, or medication)."""

    title: str
    duration_minutes: int
    priority: str = "medium"           # "low" | "medium" | "high"
    category: str = "general"          # e.g. "walk", "feeding", "meds"
    recurrence: str = "daily"          # e.g. "daily", "weekly", "once"
    preferred_time: str | None = None  # optional "HH:MM" the owner would like
    completed: bool = False            # completion status
    due_date: date = field(default_factory=date.today)  # the day this task is due

    def priority_rank(self) -> int:
        """Return a sortable integer for this task's priority (high = 3)."""
        return PRIORITY_ORDER.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh (uncompleted) copy due on the next date, or None if one-off."""
        delta = RECURRENCE_DELTAS.get(self.recurrence)
        if delta is None:  # "once" or unknown recurrence: nothing to reschedule
            return None
        return replace(self, completed=False, due_date=self.due_date + delta)


@dataclass
class Pet:
    """A pet that belongs to an owner and owns its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age_years: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)


class Owner:
    """The pet owner; holds pets, scheduling constraints, and preferences."""

    def __init__(
        self,
        name: str,
        available_minutes: int = 120,
        preferred_start: str = "08:00",
    ) -> None:
        """Create an owner with a daily time budget and preferred start time."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferred_start = preferred_start
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def find_pet(self, pet_name: str) -> Pet | None:
        """Return the pet with the given name, or None if not found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def add_task(self, pet_name: str, task: Task) -> None:
        """Add a task to one of this owner's pets, found by name."""
        pet = self.find_pet(pet_name)
        if pet is None:
            raise ValueError(f"No pet named {pet_name!r} for owner {self.name!r}.")
        pet.add_task(task)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


@dataclass
class ScheduledTask:
    """A task placed into the day's plan, with a start/end time and a reason."""

    task: Task
    start_time: str    # "HH:MM"
    end_time: str      # "HH:MM"
    reason: str = ""   # why the scheduler placed it here

    def __str__(self) -> str:
        """Render one plan line, e.g. '08:00–08:30  Morning walk (30 min) [high]'."""
        return (
            f"{self.start_time}–{self.end_time}  "
            f"{self.task.title} ({self.task.duration_minutes} min) "
            f"[{self.task.priority}]"
        )


class Scheduler:
    """Turns a list of tasks into an ordered daily plan within a time budget."""

    def __init__(self, available_minutes: int = 120, day_start: str = "08:00") -> None:
        """Create a scheduler with a total time budget and a day start time."""
        self.available_minutes = available_minutes
        self.day_start = day_start

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then by preferred time, then duration."""
        return sorted(
            tasks,
            key=lambda t: (
                -t.priority_rank(),
                _to_minutes(t.preferred_time) if t.preferred_time else 24 * 60,
                t.duration_minutes,
            ),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Order tasks chronologically by preferred_time; untimed tasks go last."""
        return sorted(
            tasks,
            key=lambda t: _to_minutes(t.preferred_time) if t.preferred_time else 24 * 60,
        )

    def filter_by_status(self, tasks: list[Task], completed: bool = False) -> list[Task]:
        """Return only the tasks whose completed flag matches `completed`."""
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, owner: Owner, pet_name: str) -> list[Task]:
        """Return the tasks belonging to a single pet (empty if the pet is unknown)."""
        pet = owner.find_pet(pet_name)
        return list(pet.tasks) if pet else []

    def expand_recurring(self, tasks: list[Task], day: str = "today") -> list[Task]:
        """Return the tasks that are due on `day` (daily tasks always apply)."""
        return [t for t in tasks if t.recurrence in ("daily", "once")]

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task done and return its auto-generated next occurrence (None if one-off)."""
        task.mark_complete()
        return task.next_occurrence()

    def build_plan(self, tasks: list[Task]) -> list[ScheduledTask]:
        """Greedily select the highest-priority tasks that fit the budget, time-ordered."""
        plan: list[ScheduledTask] = []
        cursor = _to_minutes(self.day_start)
        used = 0
        for task in self.sort_tasks(tasks):
            if task.completed:
                continue  # already done today
            if used + task.duration_minutes > self.available_minutes:
                continue  # skip tasks that don't fit the remaining budget
            start = cursor
            end = cursor + task.duration_minutes
            remaining = self.available_minutes - used - task.duration_minutes
            reason = (
                f"{task.priority} priority; fits with {remaining} min budget left"
            )
            plan.append(ScheduledTask(task, _to_hhmm(start), _to_hhmm(end), reason))
            cursor = end
            used += task.duration_minutes
        return plan

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Warn when two tasks want the same preferred_time slot (exact match)."""
        warnings: list[str] = []
        seen: dict[str, str] = {}  # preferred_time -> first task title claiming it
        for task in tasks:
            if not task.preferred_time:
                continue  # untimed tasks can't conflict
            if task.preferred_time in seen:
                warnings.append(
                    f"Time conflict at {task.preferred_time}: "
                    f"'{seen[task.preferred_time]}' and '{task.title}'"
                )
            else:
                seen[task.preferred_time] = task.title
        return warnings

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Produce a readable explanation of why the plan looks the way it does."""
        if not plan:
            return "No tasks fit the available time budget."
        lines = ["Here is the reasoning behind today's plan:"]
        for item in plan:
            lines.append(
                f"  - {item.start_time}: {item.task.title} — {item.reason}"
            )
        skipped = self.available_minutes - sum(
            s.task.duration_minutes for s in plan
        )
        lines.append(f"Total free time remaining: {skipped} min.")
        return "\n".join(lines)
