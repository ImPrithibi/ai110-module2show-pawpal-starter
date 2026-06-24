"""PawPal+ logic layer.

Phase 1 skeleton: class names, attributes, and empty method stubs derived
from diagrams/uml.mmd. No scheduling logic yet — that arrives in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Ordering used to rank tasks; higher number = more important.
PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single pet-care task, e.g. a morning walk or a dose of medication."""

    title: str
    duration_minutes: int
    priority: str = "medium"          # "low" | "medium" | "high"
    category: str = "general"         # e.g. "walk", "feeding", "meds", "grooming"
    recurrence: str = "daily"         # e.g. "daily", "weekly", "once"
    preferred_time: str | None = None  # optional "HH:MM" the owner would like

    def priority_rank(self) -> int:
        """Return a sortable integer for this task's priority."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet that belongs to an owner and has its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age_years: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError


class Owner:
    """The pet owner. Holds pets, scheduling constraints, and preferences."""

    def __init__(
        self,
        name: str,
        available_minutes: int = 120,
        preferred_start: str = "08:00",
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferred_start = preferred_start
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        raise NotImplementedError

    def add_task(self, pet_name: str, task: Task) -> None:
        """Add a task to one of this owner's pets, found by name."""
        raise NotImplementedError

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        raise NotImplementedError


@dataclass
class ScheduledTask:
    """A task placed into the day's plan, with a start/end time and a reason."""

    task: Task
    start_time: str   # "HH:MM"
    end_time: str     # "HH:MM"
    reason: str = ""  # why the scheduler placed it here


class Scheduler:
    """Turns a list of tasks into an ordered daily plan within a time budget."""

    def __init__(self, available_minutes: int = 120, day_start: str = "08:00") -> None:
        self.available_minutes = available_minutes
        self.day_start = day_start

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (and tie-breakers like duration)."""
        raise NotImplementedError

    def expand_recurring(self, tasks: list[Task], day: str) -> list[Task]:
        """Expand recurring tasks into the concrete tasks due on `day`."""
        raise NotImplementedError

    def build_plan(self, tasks: list[Task]) -> list[ScheduledTask]:
        """Select and time-order tasks that fit within the time budget."""
        raise NotImplementedError

    def detect_conflicts(self, plan: list[ScheduledTask]) -> list[str]:
        """Return human-readable warnings for overlapping scheduled tasks."""
        raise NotImplementedError

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Produce a readable explanation of why the plan looks the way it does."""
        raise NotImplementedError
