"""
Resolution Tracker App
A Streamlit web app for tracking New Year's resolutions with milestone goals and a reward system.
"""

import streamlit as st
import json
import os
from datetime import datetime, date
import uuid

# =============================================================================
# CONFIGURATION
# =============================================================================

# Path to the JSON data file
DATA_FILE = "data/resolutions.json"

# Page configuration
st.set_page_config(
    page_title="Resolution Tracker",
    page_icon="🎯",
    layout="centered"
)

# =============================================================================
# DATA MANAGEMENT FUNCTIONS
# =============================================================================

def load_data():
    """
    Load resolutions from the JSON file.
    Returns an empty list if the file doesn't exist or is empty.
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return data if data else []
        return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_data(resolutions):
    """
    Save resolutions to the JSON file.
    Creates the data directory if it doesn't exist.
    """
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    with open(DATA_FILE, "w") as f:
        json.dump(resolutions, f, indent=2, default=str)


def check_password(password):
    """
    Validate the password against the stored secret.
    Uses Streamlit secrets for secure password storage.
    """
    try:
        # Try to get password from Streamlit secrets (for cloud deployment)
        correct_password = st.secrets["password"]
    except (KeyError, FileNotFoundError):
        # Fallback for local development without secrets file
        correct_password = "Lynda2026"

    return password == correct_password


# =============================================================================
# RESOLUTION OPERATIONS
# =============================================================================

def create_resolution(title, start_date, target_date, reason, importance, milestone_descriptions):
    """
    Create a new resolution with 4 milestones.
    Returns the new resolution dictionary.
    """
    # Create the 4 milestones from descriptions
    milestones = []
    for desc in milestone_descriptions:
        milestones.append({
            "description": desc,
            "completed": False,
            "note": ""
        })

    # Create the resolution
    resolution = {
        "id": str(uuid.uuid4()),  # Unique identifier
        "title": title,
        "start_date": str(start_date),
        "target_date": str(target_date),
        "reason": reason,
        "importance": importance,
        "milestones": milestones,
        "achieved": False
    }

    return resolution


def update_resolution(resolutions, resolution_id, updated_data):
    """
    Update an existing resolution with new data.
    Returns the updated list of resolutions.
    """
    for i, res in enumerate(resolutions):
        if res["id"] == resolution_id:
            # Update fields that were provided
            for key, value in updated_data.items():
                if key != "id":  # Don't allow changing the ID
                    resolutions[i][key] = value
            break
    return resolutions


def delete_resolution(resolutions, resolution_id):
    """
    Delete a resolution from the list.
    Returns the updated list of resolutions.
    """
    return [res for res in resolutions if res["id"] != resolution_id]


def get_resolution_by_id(resolutions, resolution_id):
    """
    Find and return a resolution by its ID.
    Returns None if not found.
    """
    for res in resolutions:
        if res["id"] == resolution_id:
            return res
    return None


# =============================================================================
# MILESTONE OPERATIONS
# =============================================================================

def mark_milestone_complete(resolutions, resolution_id, milestone_index, completed=True):
    """
    Mark a specific milestone as complete or incomplete.
    Also updates the resolution's achieved status if all milestones are complete.
    Returns the updated list of resolutions.
    """
    for res in resolutions:
        if res["id"] == resolution_id:
            res["milestones"][milestone_index]["completed"] = completed
            # Check if all milestones are now complete
            res["achieved"] = check_resolution_achieved(res)
            break
    return resolutions


def add_milestone_note(resolutions, resolution_id, milestone_index, note):
    """
    Add or update a note for a specific milestone.
    Returns the updated list of resolutions.
    """
    for res in resolutions:
        if res["id"] == resolution_id:
            res["milestones"][milestone_index]["note"] = note
            break
    return resolutions


# =============================================================================
# CALCULATION & DISPLAY FUNCTIONS
# =============================================================================

def get_top_resolutions(resolutions, n=3):
    """
    Sort resolutions by importance (descending) and return the top N.
    """
    sorted_resolutions = sorted(resolutions, key=lambda x: x["importance"], reverse=True)
    return sorted_resolutions[:n]


def calculate_total_stars(resolutions):
    """
    Count the total number of completed milestones across all resolutions.
    Each completed milestone = 1 star.
    """
    total = 0
    for res in resolutions:
        for milestone in res["milestones"]:
            if milestone["completed"]:
                total += 1
    return total


def check_resolution_achieved(resolution):
    """
    Check if all 4 milestones are completed.
    Returns True if the resolution is fully achieved.
    """
    return all(m["completed"] for m in resolution["milestones"])


def display_importance_stars(importance):
    """
    Display importance as stars (1-5).
    """
    return "⭐" * importance


def format_date(date_str):
    """
    Format a date string for display.
    """
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d")
        return d.strftime("%B %d, %Y")
    except:
        return str(date_str)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """
    Initialize all session state variables if they don't exist.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if "selected_resolution_id" not in st.session_state:
        st.session_state.selected_resolution_id = None

    if "selected_milestone_index" not in st.session_state:
        st.session_state.selected_milestone_index = None

    if "resolutions" not in st.session_state:
        st.session_state.resolutions = load_data()

    if "show_celebration" not in st.session_state:
        st.session_state.show_celebration = False

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False


def navigate_to(page, resolution_id=None, milestone_index=None):
    """
    Navigate to a different page and optionally set selected items.
    """
    st.session_state.page = page
    if resolution_id is not None:
        st.session_state.selected_resolution_id = resolution_id
    if milestone_index is not None:
        st.session_state.selected_milestone_index = milestone_index
    st.session_state.edit_mode = False


# =============================================================================
# PAGE FUNCTIONS
# =============================================================================

def show_login_page():
    """
    Display the login screen with password input.
    """
    st.title("🎯 Resolution Tracker")
    st.subheader("Welcome! Please log in to continue.")

    # Password input
    password = st.text_input("Password", type="password", key="login_password")

    # Login button
    if st.button("Login", type="primary"):
        if check_password(password):
            st.session_state.authenticated = True
            st.session_state.page = "home"
            st.session_state.resolutions = load_data()
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")


def show_home_page():
    """
    Display the home page with top 3 resolutions and total star count.
    """
    st.title("🎯 Resolution Tracker")

    # Reload data to ensure we have the latest
    st.session_state.resolutions = load_data()
    resolutions = st.session_state.resolutions

    # Display total stars
    total_stars = calculate_total_stars(resolutions)
    st.markdown(f"### ⭐ Total Stars Earned: **{total_stars}**")

    st.divider()

    # Display top 3 resolutions
    st.subheader("🏆 Top Resolutions")

    if not resolutions:
        st.info("No resolutions yet! Click 'All Resolutions' to create your first one.")
    else:
        top_resolutions = get_top_resolutions(resolutions, 3)

        for res in top_resolutions:
            # Count completed milestones for this resolution
            completed_count = sum(1 for m in res["milestones"] if m["completed"])

            # Create a card-like display
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Show achieved badge if all milestones complete
                    achieved_badge = "✅ " if res["achieved"] else ""
                    st.markdown(f"**{achieved_badge}{res['title']}**")
                    st.caption(f"Importance: {display_importance_stars(res['importance'])} | Progress: {completed_count}/4 ⭐")

                with col2:
                    if st.button("View", key=f"view_{res['id']}"):
                        navigate_to("resolution", resolution_id=res["id"])
                        st.rerun()

                st.divider()

    # Navigation button
    if st.button("📋 All Resolutions", type="primary"):
        navigate_to("all")
        st.rerun()


def show_all_resolutions_page():
    """
    Display all resolutions with options to view or create new ones.
    """
    st.title("📋 All Resolutions")

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Home"):
            navigate_to("home")
            st.rerun()
    with col2:
        if st.button("➕ Create New Resolution", type="primary"):
            navigate_to("create")
            st.rerun()

    st.divider()

    # Load and display all resolutions
    resolutions = st.session_state.resolutions

    if not resolutions:
        st.info("No resolutions yet! Click 'Create New Resolution' to get started.")
    else:
        # Sort by importance
        sorted_resolutions = sorted(resolutions, key=lambda x: x["importance"], reverse=True)

        for res in sorted_resolutions:
            completed_count = sum(1 for m in res["milestones"] if m["completed"])

            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    achieved_badge = "✅ " if res["achieved"] else ""
                    st.markdown(f"**{achieved_badge}{res['title']}**")
                    st.caption(f"Importance: {display_importance_stars(res['importance'])} | Progress: {completed_count}/4 ⭐")
                    st.caption(f"Target: {format_date(res['target_date'])}")

                with col2:
                    if st.button("View", key=f"all_view_{res['id']}"):
                        navigate_to("resolution", resolution_id=res["id"])
                        st.rerun()

                st.divider()


def show_individual_resolution_page():
    """
    Display an individual resolution with all its details and milestones.
    """
    resolution_id = st.session_state.selected_resolution_id
    resolutions = st.session_state.resolutions
    resolution = get_resolution_by_id(resolutions, resolution_id)

    if not resolution:
        st.error("Resolution not found!")
        if st.button("🏠 Go Home"):
            navigate_to("home")
            st.rerun()
        return

    # Navigation
    if st.button("🏠 Home"):
        navigate_to("home")
        st.rerun()

    st.divider()

    # Check if in edit mode
    if st.session_state.edit_mode:
        show_edit_resolution_form(resolution)
        return

    # Display resolution details
    achieved_badge = "✅ ACHIEVED! " if resolution["achieved"] else ""
    st.title(f"{achieved_badge}{resolution['title']}")

    # Resolution info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Start Date:** {format_date(resolution['start_date'])}")
        st.markdown(f"**Target Date:** {format_date(resolution['target_date'])}")
    with col2:
        st.markdown(f"**Importance:** {display_importance_stars(resolution['importance'])}")
        completed_count = sum(1 for m in resolution["milestones"] if m["completed"])
        st.markdown(f"**Progress:** {completed_count}/4 ⭐")

    st.markdown(f"**Why this matters:** {resolution['reason']}")

    st.divider()

    # Display milestones
    st.subheader("🎯 Milestones")

    for i, milestone in enumerate(resolution["milestones"]):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                # Show star if completed
                star = "⭐ " if milestone["completed"] else "○ "
                status = "(Completed)" if milestone["completed"] else "(In Progress)"
                st.markdown(f"**{star}Milestone {i + 1}:** {milestone['description']} {status}")
                if milestone["note"]:
                    st.caption(f"Note: {milestone['note']}")

            with col2:
                if st.button("Edit", key=f"milestone_{i}"):
                    navigate_to("milestone", resolution_id=resolution_id, milestone_index=i)
                    st.rerun()

        st.divider()

    # Action buttons
    st.subheader("Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✏️ Edit Resolution"):
            st.session_state.edit_mode = True
            st.rerun()

    with col2:
        if st.button("🗑️ Delete Resolution", type="secondary"):
            st.session_state.confirm_delete = True
            st.rerun()

    # Confirm delete dialog
    if st.session_state.get("confirm_delete", False):
        st.warning("Are you sure you want to delete this resolution?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete", type="primary"):
                st.session_state.resolutions = delete_resolution(resolutions, resolution_id)
                save_data(st.session_state.resolutions)
                st.session_state.confirm_delete = False
                navigate_to("all")
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()


def show_edit_resolution_form(resolution):
    """
    Display the edit form for a resolution.
    """
    st.subheader("✏️ Edit Resolution")

    with st.form("edit_resolution_form"):
        title = st.text_input("Title", value=resolution["title"])

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.strptime(resolution["start_date"], "%Y-%m-%d"))
        with col2:
            target_date = st.date_input("Target Date", value=datetime.strptime(resolution["target_date"], "%Y-%m-%d"))

        reason = st.text_area("Why is this important to you?", value=resolution["reason"])
        importance = st.slider("Importance (1-5)", 1, 5, value=resolution["importance"])

        # Milestone descriptions
        st.markdown("**Milestones:**")
        milestone_descriptions = []
        for i, m in enumerate(resolution["milestones"]):
            desc = st.text_input(f"Milestone {i + 1}", value=m["description"], key=f"edit_m_{i}")
            milestone_descriptions.append(desc)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancelled = st.form_submit_button("Cancel")

        if submitted:
            # Update the resolution
            updated_data = {
                "title": title,
                "start_date": str(start_date),
                "target_date": str(target_date),
                "reason": reason,
                "importance": importance,
            }

            # Update milestone descriptions (preserve completed status and notes)
            for i, desc in enumerate(milestone_descriptions):
                resolution["milestones"][i]["description"] = desc

            updated_data["milestones"] = resolution["milestones"]

            st.session_state.resolutions = update_resolution(
                st.session_state.resolutions,
                resolution["id"],
                updated_data
            )
            save_data(st.session_state.resolutions)
            st.session_state.edit_mode = False
            st.success("Resolution updated!")
            st.rerun()

        if cancelled:
            st.session_state.edit_mode = False
            st.rerun()


def show_individual_milestone_page():
    """
    Display an individual milestone with checkbox and note field.
    """
    resolution_id = st.session_state.selected_resolution_id
    milestone_index = st.session_state.selected_milestone_index
    resolutions = st.session_state.resolutions
    resolution = get_resolution_by_id(resolutions, resolution_id)

    if not resolution or milestone_index is None:
        st.error("Milestone not found!")
        if st.button("🏠 Go Home"):
            navigate_to("home")
            st.rerun()
        return

    milestone = resolution["milestones"][milestone_index]

    # Back button
    if st.button("⬅️ Back to Resolution"):
        navigate_to("resolution", resolution_id=resolution_id)
        st.rerun()

    st.divider()

    st.title(f"Milestone {milestone_index + 1}")
    st.markdown(f"**{milestone['description']}**")

    # Show celebration if milestone was already complete when page loaded
    if milestone["completed"] and not st.session_state.get("celebration_shown", False):
        st.balloons()
        st.success("🎉 Amazing! You've already completed this milestone! ⭐")
        st.session_state.celebration_shown = True

    st.divider()

    # Completion checkbox
    was_completed = milestone["completed"]
    completed = st.checkbox(
        "Mark as completed",
        value=milestone["completed"],
        key="milestone_completed"
    )

    # Note field
    note = st.text_area(
        "Add a note (optional)",
        value=milestone["note"],
        placeholder="Write any thoughts, reflections, or details about this milestone...",
        key="milestone_note"
    )

    # Save button
    if st.button("💾 Save", type="primary"):
        # Check if milestone was just completed
        just_completed = completed and not was_completed

        # Update milestone
        st.session_state.resolutions = mark_milestone_complete(
            st.session_state.resolutions,
            resolution_id,
            milestone_index,
            completed
        )
        st.session_state.resolutions = add_milestone_note(
            st.session_state.resolutions,
            resolution_id,
            milestone_index,
            note
        )
        save_data(st.session_state.resolutions)

        # Show celebration if just completed
        if just_completed:
            st.balloons()
            st.success("🎉 Congratulations! You've completed this milestone! Keep up the great work! ⭐")

            # Check if all milestones are now complete
            updated_resolution = get_resolution_by_id(st.session_state.resolutions, resolution_id)
            if updated_resolution["achieved"]:
                st.success("🏆 AMAZING! You've achieved your entire resolution! All 4 milestones complete! 🎊")
        else:
            st.success("Milestone saved!")

        # Reset celebration flag for next visit
        st.session_state.celebration_shown = False

        # Navigate back after a moment
        navigate_to("resolution", resolution_id=resolution_id)
        st.rerun()


def show_create_resolution_page():
    """
    Display the form to create a new resolution.
    """
    st.title("➕ Create New Resolution")

    # Back button
    if st.button("⬅️ Back to All Resolutions"):
        navigate_to("all")
        st.rerun()

    st.divider()

    with st.form("create_resolution_form"):
        # Basic info
        title = st.text_input("Resolution Title", placeholder="e.g., Learn a new language")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today())
        with col2:
            target_date = st.date_input("Target Date")

        reason = st.text_area(
            "Why is this important to you?",
            placeholder="Describe your motivation for this resolution..."
        )

        importance = st.slider("Importance (1-5)", 1, 5, value=3)

        # Milestone descriptions
        st.markdown("### 🎯 Define Your 4 Milestones")
        st.caption("Break your resolution into 4 achievable milestones")

        m1 = st.text_input("Milestone 1", placeholder="First step towards your goal")
        m2 = st.text_input("Milestone 2", placeholder="Building momentum")
        m3 = st.text_input("Milestone 3", placeholder="Getting closer")
        m4 = st.text_input("Milestone 4", placeholder="Final milestone to achieve your resolution")

        submitted = st.form_submit_button("💾 Create Resolution", type="primary")

        if submitted:
            # Validate inputs
            if not title:
                st.error("Please enter a title for your resolution.")
            elif not all([m1, m2, m3, m4]):
                st.error("Please fill in all 4 milestones.")
            else:
                # Create the resolution
                new_resolution = create_resolution(
                    title=title,
                    start_date=start_date,
                    target_date=target_date,
                    reason=reason,
                    importance=importance,
                    milestone_descriptions=[m1, m2, m3, m4]
                )

                # Add to list and save
                st.session_state.resolutions.append(new_resolution)
                save_data(st.session_state.resolutions)

                st.success("Resolution created successfully! 🎉")
                navigate_to("all")
                st.rerun()


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """
    Main function that controls the app flow.
    """
    # Initialize session state
    init_session_state()

    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return

    # Route to the appropriate page
    page = st.session_state.page

    if page == "login":
        show_login_page()
    elif page == "home":
        show_home_page()
    elif page == "all":
        show_all_resolutions_page()
    elif page == "resolution":
        show_individual_resolution_page()
    elif page == "milestone":
        show_individual_milestone_page()
    elif page == "create":
        show_create_resolution_page()
    else:
        # Default to home
        show_home_page()


# Run the app
if __name__ == "__main__":
    main()
