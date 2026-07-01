"""CLI demo for PawPal+.

A temporary testing ground that exercises the logic layer end to end:
create an owner with two pets, add several tasks, then print today's plan.
Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner with two pets and a handful of care tasks."""
    owner = Owner(name="Jordan", available_minutes=90, preferred_start="08:00")

    mochi = Pet(name="Mochi", species="dog", breed="Corgi", age_years=3)
    biscuit = Pet(name="Biscuit", species="cat", breed="Tabby", age_years=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    owner.add_task("Mochi", Task("Morning walk", 30, priority="high", category="walk"))
    owner.add_task("Mochi", Task("Breakfast", 10, priority="high", category="feeding"))
    owner.add_task("Biscuit", Task("Litter scoop", 10, priority="medium", category="grooming"))
    owner.add_task("Biscuit", Task("Play / enrichment", 20, priority="low", category="enrichment"))
    return owner


def main() -> None:
    """Build the demo data and print today's schedule to the terminal."""
    owner = build_demo_owner()
    scheduler = Scheduler(
        available_minutes=owner.available_minutes,
        day_start=owner.preferred_start,
    )

    due_today = scheduler.expand_recurring(owner.all_tasks())
    plan = scheduler.build_plan(due_today)

    print(f"\n🐾 Today's Schedule for {owner.name}")
    print(f"   (time budget: {owner.available_minutes} min, start: {owner.preferred_start})")
    print("-" * 48)
    for item in plan:
        print(f"  {item}")
    print("-" * 48)

    conflicts = scheduler.detect_conflicts(plan)
    if conflicts:
        print("⚠️  Conflicts:")
        for warning in conflicts:
            print(f"   - {warning}")
    else:
        print("✅ No scheduling conflicts.")

    print()
    print(scheduler.explain_plan(plan))
    print()


if __name__ == "__main__":
    main()
