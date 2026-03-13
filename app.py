import streamlit as st

from pawpal_system import Pet, Owner, PetCareTask, Scheduler

from datetime import date as Date



st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """

At minimum, your system should:

[MermaidChart: 3c5df3d2-97cb-455e-8e47-a43e262279b1]
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()


st.subheader("Quick Demo Inputs (UI only)")

owner_name = st.text_input("Owner name", placeholder="Enter your name")
time_available = st.number_input("Time available (minutes)", min_value=1, max_value=1440, placeholder="e.g. 180")

if st.button("Add New Owner"):
    if owner_name.strip():
        st.session_state.owner = Owner(owner_name.strip())
    else:
        st.warning("Please enter a name first.")

if "owner" in st.session_state:
    st.success(f"Owner: {st.session_state.owner.get_name()}")



pet_name = st.text_input("Pet name", placeholder="Enter your pet's name")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "pets" not in st.session_state:
    st.session_state.pets = []

if st.button("Add New Pet"):
    if pet_name.strip() and "owner" in st.session_state:
        st.session_state.pets.append(Pet(pet_name.strip(), species))
    else:
        st.warning("Please enter a name first.")

for p in st.session_state.pets:
    st.success(f"Pet: {p.get_name()} ({p.get_type()})")



st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pet_options = [p.get_name() for p in st.session_state.pets]
    selected_pet_name = st.selectbox("Pet", pet_options if pet_options else ["—"])
with col2:
    task_title = st.text_input("Task title", placeholder="e.g. Feed Buddy")
with col3:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, placeholder="e.g. 15")
with col4:
    priority = st.selectbox("Priority", ["low", "medium", "high"], placeholder="Select priority")
with col5:
    task_date = st.date_input("Date", value=Date.today())

if st.button("Add task"):
    selected_pet = next((p for p in st.session_state.pets if p.get_name() == selected_pet_name), None)
    if selected_pet:
        task = PetCareTask(task_title, int(duration), priority, selected_pet, date=task_date)
        st.session_state.tasks.append(task)
    else:
        st.warning("Please add a pet before creating tasks.")


if st.session_state.tasks:
    st.write("Current tasks:")
    task_rows = [
        {
            "Date": task.date.strftime("%Y-%m-%d"),
            "Pet": task.pet.get_name(),
            "Description": task.description,
            "Duration": task.get_duration_display(),
            "Priority": task.priority,
            "Status": task.status,
        }
        for task in st.session_state.tasks
    ]
    st.table(task_rows)

else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

sort_by = st.selectbox("Sort tasks by", ["priority", "duration_asc", "duration_desc"])

if st.button("Generate schedule"):
    if "owner" not in st.session_state or not st.session_state.tasks:
        st.warning("Please add an owner and at least one task first.")
    else:
        time_available = st.session_state.get("time_available", time_available)
        scheduler = Scheduler(st.session_state.owner, time_available)

        for task in st.session_state.tasks:
            scheduler.add_task(task)

        plan = scheduler.generate_plan(sort_by=sort_by)

        total_task_time = sum(task.duration for task in plan)

        format_minutes = lambda m: f"{m} min" if m < 60 else f"{m//60} hr {m%60} min" if m % 60 else f"{m//60} hr"
        


        st.info(f"Schedule for {st.session_state.owner.get_name()} — {scheduler.get_time_available_display()} available — Task Estimate Time: {format_minutes(total_task_time)}")
        plan_rows = [
            {
                "Pet": task.pet.get_name(),
                "Description": task.description,
                "Duration": task.get_duration_display(),
                "Priority": task.priority,
            }
            for task in plan
        ]
        st.table(plan_rows)

        excluded = [t for t in st.session_state.tasks if t not in plan]
        if excluded:
            st.warning(
                f"{len(excluded)} task(s) were excluded because they couldn't fit within "
                f"the available time ({scheduler.get_time_available_display()}):"
            )
            excluded_rows = [
                {
                    "Pet": t.pet.get_name(),
                    "Description": t.description,
                    "Duration": t.get_duration_display(),
                    "Priority": t.priority,
                }
                for t in excluded
            ]
            st.table(excluded_rows)
