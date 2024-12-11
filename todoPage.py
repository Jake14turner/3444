import streamlit as st
from user import initializeUserInfoJSON, sortUserDataIntoList
from datetime import datetime, timezone, timedelta
import time
import re
from navigationUI import showNavigationBar
if 'isLoggedIn' not in st.session_state:
    st.session_state.isLoggedIn = False

def countdown(name, target_time):
    """Generate countdown text with color gradient based on urgency."""
    now = datetime.now(timezone.utc)
    remaining_time = target_time - now

    if remaining_time.total_seconds() > 0:
        days, remainder = divmod(remaining_time.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Calculate urgency-based color
        total_seconds = timedelta(days=7).total_seconds()  # Assume 30 days max
        urgency_ratio = max(0, min(1, remaining_time.total_seconds() / total_seconds))
        red = int(255 * (1 - urgency_ratio))
        green = int(255 * urgency_ratio)
        color = f"rgb({red},{green},0)"

        return f"<span style='color:{color};'>{int(days)}d {int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s</span>"

def toDoView():

    st.title("To Do List :material/note:")
    username = st.session_state.username

    # Fetch user data
   # data = initializeUserInfoJSON(username)
   # studentInfo = sortUserDataIntoList(data)
    studentInfo = st.session_state.studentInfo

    # Prepare assignments
    assignments_with_due_dates = []
    assignments_without_due_dates = []

    for k in studentInfo:
        for j in k.assignmentList:
            due_date_str = j.dueDate
            if due_date_str:
                try:
                    now = datetime.now(timezone.utc)
                    target_time = datetime.fromisoformat(due_date_str[:-1] + "+00:00")
                    remaining_time = target_time - now

                    if remaining_time.total_seconds() > 0:
                        assignments_with_due_dates.append((k.name, j.name, target_time))
                except ValueError:
                    st.error(f"Invalid date format for assignment '{j.name}'. Please check the due date.")
            else:
                assignments_without_due_dates.append((k.name, j.name))

    # Sort assignments by due date
    assignments_with_due_dates.sort(key=lambda x: x[2])

    # Display assignments with countdowns
    st.write("## Assignments with Due Dates")
    placeholders = []
    for course_name, assignment_name, target_time in assignments_with_due_dates:
        placeholder = st.empty()
        first_hyphen = course_name.find('-')

        if first_hyphen != -1:
            
            # Replace the substring (including the hyphens) with an empty string
            course_name = course_name[:first_hyphen]


        #print("hello")

        placeholders.append((placeholder, course_name, assignment_name, target_time))

    # Display assignments without due dates
    st.write("## Assignments Without Due Dates")
    for course_name, assignment_name in assignments_without_due_dates:
        st.write(f"- **{assignment_name}** (No due date)")

    # Start updating countdowns
    while True:
        for placeholder, course_name, assignment_name, target_time in placeholders:
            countdown_text = countdown(f"{course_name} - {assignment_name}", target_time)
            placeholder.markdown(
                f"**{course_name} - {assignment_name}:** {countdown_text}",
                unsafe_allow_html=True
            )
        time.sleep(1)  # Update every second

if st.session_state.isLoggedIn:
    showNavigationBar()
    toDoView()
else:
    st.text("Please log in to view the To-Do page.")
