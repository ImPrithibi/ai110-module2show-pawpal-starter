"""Automated test suite for the PawPal+ logic layer.

Covers the core behaviors: task completion, task ownership, chronological
sorting, filtering, recurring-task rollover, conflict detection, and the
budget-aware daily plan — plus a few edge cases (no times, empty lists).
"""

from datetime import date

from pawpal_system import Owner, Pet, ScheduledTask, Scheduler, Task


# --- Task basics ----------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task's completed flag to True."""
    task = Task("Evening walk", 20, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Breakfast", 10))
    assert len(pet.tasks) == 1


# --- Owner aggregation ----------------------------------------------------

def test_owner_all_tasks_spans_multiple_pets():
    """all_tasks() collects tasks from every pet the owner has."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))
    owner.add_pet(Pet("Biscuit", "cat"))
    owner.add_task("Mochi", Task("Walk", 30))
    owner.add_task("Biscuit", Task("Litter scoop", 10))
    assert len(owner.all_tasks()) == 2


def test_add_task_to_unknown_pet_raises():
    """Adding a task for a nonexistent pet raises a clear error."""
    owner = Owner("Jordan")
    try:
        owner.add_task("Ghost", Task("Walk", 30))
        assert False, "expected ValueError for unknown pet"
    except ValueError:
        pass


# --- Sorting --------------------------------------------------------------

def test_sort_by_time_is_chronological():
    """sort_by_time() returns tasks in ascending preferred_time order."""
    scheduler = Scheduler()
    tasks = [
        Task("Dinner", 10, preferred_time="18:00"),
        Task("Walk", 30, preferred_time="08:00"),
        Task("Lunch", 10, preferred_time="12:00"),
    ]
    ordered = [t.preferred_time for t in scheduler.sort_by_time(tasks)]
    assert ordered == ["08:00", "12:00", "18:00"]


def test_sort_by_time_puts_untimed_tasks_last():
    """Tasks without a preferred_time sort after all timed tasks."""
    scheduler = Scheduler()
    tasks = [
        Task("Anytime play", 15, preferred_time=None),
        Task("Walk", 30, preferred_time="08:00"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert ordered[0].title == "Walk"
    assert ordered[-1].title == "Anytime play"


# --- Filtering ------------------------------------------------------------

def test_filter_by_status_returns_only_incomplete():
    """filter_by_status(completed=False) drops completed tasks."""
    scheduler = Scheduler()
    done = Task("Walk", 30)
    done.mark_complete()
    todo = Task("Feed", 10)
    result = scheduler.filter_by_status([done, todo], completed=False)
    assert result == [todo]


def test_filter_by_pet_returns_only_that_pets_tasks():
    """filter_by_pet() narrows the tasks to a single named pet."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))
    owner.add_pet(Pet("Biscuit", "cat"))
    owner.add_task("Mochi", Task("Walk", 30))
    owner.add_task("Biscuit", Task("Litter scoop", 10))
    scheduler = Scheduler()
    mochi_tasks = scheduler.filter_by_pet(owner, "Mochi")
    assert [t.title for t in mochi_tasks] == ["Walk"]


# --- Recurrence -----------------------------------------------------------

def test_completing_daily_task_creates_next_day_task():
    """Marking a daily task complete creates a fresh task due the following day."""
    scheduler = Scheduler()
    task = Task("Morning walk", 30, recurrence="daily", due_date=date(2026, 1, 1))
    next_task = scheduler.mark_task_complete(task)
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date(2026, 1, 2)


def test_completing_weekly_task_advances_seven_days():
    """A weekly task rolls forward exactly one week."""
    task = Task("Nail trim", 15, recurrence="weekly", due_date=date(2026, 1, 1))
    assert task.next_occurrence().due_date == date(2026, 1, 8)


def test_completing_one_off_task_creates_nothing():
    """A 'once' task has no next occurrence."""
    task = Task("Vet appointment", 60, recurrence="once")
    assert task.next_occurrence() is None


# --- Conflict detection ---------------------------------------------------

def test_detect_conflicts_flags_duplicate_times():
    """Two tasks claiming the same preferred_time produce a warning."""
    scheduler = Scheduler()
    tasks = [
        Task("Walk", 30, preferred_time="08:00"),
        Task("Breakfast", 10, preferred_time="08:00"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_detect_conflicts_none_when_times_differ():
    """Distinct preferred_times produce no warnings."""
    scheduler = Scheduler()
    tasks = [
        Task("Walk", 30, preferred_time="08:00"),
        Task("Dinner", 10, preferred_time="18:00"),
    ]
    assert scheduler.detect_conflicts(tasks) == []


# --- Daily plan (budget) & edge cases ------------------------------------

def test_build_plan_respects_time_budget():
    """Tasks that exceed the time budget are skipped, keeping higher priority first."""
    scheduler = Scheduler(available_minutes=40, day_start="08:00")
    tasks = [
        Task("Long walk", 30, priority="high"),
        Task("Feed", 10, priority="high"),
        Task("Enrichment", 20, priority="low"),  # would push past 40 min
    ]
    plan = scheduler.build_plan(tasks)
    titles = [item.task.title for item in plan]
    assert "Enrichment" not in titles
    assert sum(item.task.duration_minutes for item in plan) <= 40


def test_build_plan_with_no_tasks_is_empty():
    """A pet/owner with no tasks yields an empty plan, not an error."""
    scheduler = Scheduler()
    assert scheduler.build_plan([]) == []
    assert "No tasks" in scheduler.explain_plan([])


# --- Extension: next available slot (Challenge 1) -------------------------

def test_next_available_slot_finds_gap_between_tasks():
    """A gap large enough between two scheduled tasks is returned."""
    scheduler = Scheduler(day_start="08:00")
    plan = [
        ScheduledTask(Task("Walk", 30), "08:00", "08:30"),
        ScheduledTask(Task("Meds", 15), "09:00", "09:15"),
    ]
    assert scheduler.next_available_slot(plan, 20) == "08:30"


def test_next_available_slot_empty_plan_returns_day_start():
    """With nothing scheduled, the first slot is the start of the day."""
    scheduler = Scheduler(day_start="08:00")
    assert scheduler.next_available_slot([], 30) == "08:00"


def test_next_available_slot_returns_none_when_full():
    """When the day has no room for the duration, None is returned."""
    scheduler = Scheduler(day_start="08:00")
    plan = [ScheduledTask(Task("Walk", 60), "08:00", "09:00")]
    assert scheduler.next_available_slot(plan, 30, day_end="09:15") is None
