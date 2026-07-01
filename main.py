"""CLI demo for PawPal+.

A temporary testing ground that exercises the logic layer end to end:
create an owner with two pets, add several tasks (deliberately out of order,
with a time conflict), then show off sorting, filtering, conflict detection,
recurring tasks, and the generated daily plan.
Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner with two pets and several care tasks (added out of order)."""
    owner = Owner(name="Jordan", available_minutes=90, preferred_start="08:00")

    mochi = Pet(name="Mochi", species="dog", breed="Corgi", age_years=3)
    biscuit = Pet(name="Biscuit", species="cat", breed="Tabby", age_years=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Added intentionally out of chronological order to exercise sort_by_time().
    owner.add_task("Biscuit", Task("Play / enrichment", 20, priority="low",
                                    category="enrichment", preferred_time="17:00"))
    owner.add_task("Mochi", Task("Morning walk", 30, priority="high",
                                 category="walk", preferred_time="08:00"))
    owner.add_task("Biscuit", Task("Litter scoop", 10, priority="medium",
                                   category="grooming", preferred_time="12:00"))
    # Deliberate conflict: also claims the 08:00 slot that the walk uses.
    owner.add_task("Mochi", Task("Breakfast", 10, priority="high",
                                 category="feeding", preferred_time="08:00"))
    return owner


def print_tasks(heading: str, tasks: list[Task]) -> None:
    """Print a labelled list of tasks with their time, priority, and status."""
    print(f"\n{heading}")
    for t in tasks:
        status = "✓" if t.completed else "•"
        when = t.preferred_time or "  —  "
        print(f"  {status} {when}  {t.title} [{t.priority}]")


def main() -> None:
    """Build the demo data and show off each scheduling feature in the terminal."""
    owner = build_demo_owner()
    scheduler = Scheduler(
        available_minutes=owner.available_minutes,
        day_start=owner.preferred_start,
    )
    tasks = owner.all_tasks()

    # --- Sorting (Scheduler.sort_by_time) --------------------------------
    print_tasks("🕒 Tasks sorted by time:", scheduler.sort_by_time(tasks))

    # --- Filtering (Scheduler.filter_by_status / filter_by_pet) ----------
    print_tasks("🔎 Only Mochi's tasks:", scheduler.filter_by_pet(owner, "Mochi"))
    print_tasks("🔎 Incomplete tasks only:", scheduler.filter_by_status(tasks, completed=False))

    # --- Conflict detection (Scheduler.detect_conflicts) -----------------
    print("\n⚠️  Conflict check:")
    conflicts = scheduler.detect_conflicts(tasks)
    if conflicts:
        for warning in conflicts:
            print(f"   - {warning}")
    else:
        print("   No conflicts.")

    # --- Recurring tasks (Scheduler.mark_task_complete) ------------------
    walk = scheduler.filter_by_pet(owner, "Mochi")[0]  # the daily morning walk
    next_walk = scheduler.mark_task_complete(walk)
    print("\n🔁 Recurring task rollover:")
    print(f"   Completed '{walk.title}' (due {walk.due_date}).")
    if next_walk:
        print(f"   Auto-created next '{next_walk.title}' due {next_walk.due_date}.")

    # --- The generated daily plan (Scheduler.build_plan) -----------------
    plan = scheduler.build_plan(scheduler.filter_by_status(tasks, completed=False))
    print(f"\n🐾 Today's Schedule for {owner.name}")
    print(f"   (time budget: {owner.available_minutes} min, start: {owner.preferred_start})")
    print("-" * 48)
    for item in plan:
        print(f"  {item}")
    print("-" * 48)
    print(scheduler.explain_plan(plan))
    print()


if __name__ == "__main__":
    main()
