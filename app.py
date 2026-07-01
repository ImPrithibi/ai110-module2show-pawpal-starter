import os

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant. Add your pets and their tasks, then generate a daily plan.")

# --- Application "memory" -------------------------------------------------
# Streamlit re-runs this script top-to-bottom on every interaction, so we
# stash the Owner instance in st.session_state to keep data across reruns.
# On first load we also restore any owner previously saved to data.json.
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    else:
        st.session_state.owner = Owner(name="Jordan", available_minutes=90, preferred_start="08:00")

owner: Owner = st.session_state.owner

# --- Persistence controls -------------------------------------------------
with st.sidebar:
    st.header("💾 Data")
    st.caption(f"Pets and tasks persist to `{DATA_FILE}` between runs.")
    if st.button("Save to disk"):
        owner.save_to_json(DATA_FILE)
        st.success("Saved.")
    if st.button("Reload from disk"):
        if os.path.exists(DATA_FILE):
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
            st.rerun()
        else:
            st.warning("No saved data yet.")

# --- Owner settings -------------------------------------------------------
st.subheader("Owner & day settings")
with st.form("owner_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Owner name", value=owner.name)
    with col2:
        available = st.number_input(
            "Time budget (min)", min_value=10, max_value=600, value=owner.available_minutes, step=10
        )
    with col3:
        start = st.text_input("Day start (HH:MM)", value=owner.preferred_start)
    if st.form_submit_button("Save settings"):
        owner.name = name
        owner.available_minutes = int(available)
        owner.preferred_start = start
        st.success("Settings saved.")

st.divider()

# --- Add a pet ------------------------------------------------------------
st.subheader("Add a pet")
with st.form("pet_form", clear_on_submit=True):
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with pcol2:
        breed = st.text_input("Breed", value="")
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if owner.find_pet(pet_name):
            st.warning(f"A pet named {pet_name!r} already exists.")
        else:
            owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age_years=int(age)))
            st.success(f"Added {pet_name}.")

# --- Add a task -----------------------------------------------------------
st.subheader("Add a task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("task_form", clear_on_submit=True):
        tcol1, tcol2, tcol3 = st.columns(3)
        with tcol1:
            which_pet = st.selectbox("For pet", [p.name for p in owner.pets])
            title = st.text_input("Task title", value="Morning walk")
        with tcol2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "general"])
        with tcol3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            recurrence = st.selectbox("Recurrence", ["daily", "weekly", "once"])
            preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="08:00")
        if st.form_submit_button("Add task"):
            owner.add_task(
                which_pet,
                Task(
                    title=title,
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category,
                    recurrence=recurrence,
                    preferred_time=preferred_time.strip() or None,
                ),
            )
            st.success(f"Added '{title}' for {which_pet}.")

# --- Current pets & tasks -------------------------------------------------
st.divider()
st.subheader("Your pets")

# One scheduler drives both the live views and the generated plan.
scheduler = Scheduler(available_minutes=owner.available_minutes, day_start=owner.preferred_start)

# Surface time conflicts across ALL tasks up front, so the owner sees them
# before generating a plan.
all_conflicts = scheduler.detect_conflicts(owner.all_tasks())
if all_conflicts:
    for warning in all_conflicts:
        st.warning(f"⚠️ {warning}")

if not owner.pets:
    st.info("No pets yet.")
for pet in owner.pets:
    with st.expander(f"{pet.name} — {pet.species} ({len(pet.tasks)} tasks)", expanded=True):
        if pet.tasks:
            st.table(
                [
                    {
                        "Time": t.preferred_time or "—",
                        "Task": t.title,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                        "Category": t.category,
                        "Recurrence": t.recurrence,
                        "Done": "✓" if t.completed else "",
                    }
                    for t in scheduler.sort_by_time(pet.tasks)  # chronological
                ]
            )
        else:
            st.caption("No tasks yet.")

# --- Generate the schedule ------------------------------------------------
st.divider()
st.subheader("Today's plan")
if st.button("Generate schedule", type="primary"):
    due_today = scheduler.expand_recurring(owner.all_tasks())
    active = scheduler.filter_by_status(due_today, completed=False)  # skip done tasks
    plan = scheduler.build_plan(active)

    if not plan:
        st.warning("No tasks fit the available time budget. Add tasks or increase the budget.")
    else:
        st.success(f"Planned {len(plan)} task(s) within your {owner.available_minutes}-min budget.")
        st.table(
            [
                {
                    "Start": item.start_time,
                    "End": item.end_time,
                    "Task": item.task.title,
                    "Priority": item.task.priority,
                }
                for item in plan
            ]
        )

        conflicts = scheduler.detect_conflicts(active)
        if conflicts:
            for warning in conflicts:
                st.warning(f"⚠️ {warning} — the plan still runs tasks back-to-back; consider adjusting times.")
        else:
            st.success("✅ No scheduling conflicts.")

        with st.expander("Why this plan?", expanded=True):
            st.text(scheduler.explain_plan(plan))
