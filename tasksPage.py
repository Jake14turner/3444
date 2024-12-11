import streamlit as st
import hashlib
import re
from user import sortUserDataIntoList, initializeUserInfoJSON
from datetime import datetime, date, timedelta
from navigationUI import showNavigationBar
import calendar
import streamlit.components.v1 as components
import json


from settings_functions import (
    init_db,
    save_settings,
    load_settings,
    sync_session_state,
    apply_default_session_state,
    filter_tasks_by_day,
    filter_tasks_by_week,
    filter_tasks_by_month,
    filter_tasks_by_custom_date,
    filter_tasks_none,
    practiceView,
    taskView,
    displayAssignments,
    sanitize_key,
    validate_hex_color,
    clean_due_date,
    settings_ui  
)

# Initialize database and session state
init_db()

if 'isLoggedIn' not in st.session_state:
    st.session_state.isLoggedIn = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Load and sync settings
user_email = st.session_state.user_email
settings = load_settings(user_email)
sync_session_state(settings)

# Apply default session state values
apply_default_session_state()

def tasksPageView():
    username = st.session_state.get("username")
    if not username:
        st.error("Please log in to view tasks.")
        return

    tasks, tasksSettings = st.tabs(["Tasks", "Task Settings"])

    with tasks:
        with st.expander("Classes:"):
            selected_classes = practiceView()

        selected_classes = st.session_state.get("selected_classes", [])
        filtered_assignments = []

        if 'show_tasks_by_date' not in st.session_state or st.session_state.show_tasks_by_date not in ["All Assignments", "Day", "Week", "Month", "Custom Date", "No due-date only"]:
            st.session_state.show_tasks_by_date = "All Assignments"  # Default value

        Show_Tasks_By_Date = st.session_state.get("show_tasks_by_date", "All Assignments")
        if Show_Tasks_By_Date == "Day":
            filtered_assignments = filter_tasks_by_day(selected_classes)
        elif Show_Tasks_By_Date == "Week":
            filtered_assignments = filter_tasks_by_week(selected_classes)
        elif Show_Tasks_By_Date == "Month":
            filtered_assignments = filter_tasks_by_month(selected_classes)
        elif Show_Tasks_By_Date == "Custom Date":
            custom_date_value = st.session_state.get("custom_reminder_1_date", date.today())
            if isinstance(custom_date_value, str): 
                try:
                    custom_date_value = date.fromisoformat(custom_date_value.strip())  # Remove extra spaces and parse
                except ValueError:
                    st.error(f"Invalid date format for custom reminder: '{custom_date_value}'. Expected 'YYYY-MM-DD'.")
                    custom_date_value = date.today()  # Fallback to current date if invalid
            filtered_assignments = filter_tasks_by_custom_date(selected_classes, custom_date_value)

        elif Show_Tasks_By_Date == "All Assignments":
            filtered_assignments = filter_tasks_none(selected_classes)
        elif Show_Tasks_By_Date == "No due-date only":
            filtered_assignments = [
            (class_data.name, assignment)
            for class_data in selected_classes
            for assignment in class_data.assignmentList
            if not assignment.dueDate or assignment.dueDate.lower() == "none"
        ]

        st.session_state.filtered_assignments = filtered_assignments

        if filtered_assignments:
            assignments_by_class = {}
            for class_name, assignment in filtered_assignments:
                if class_name not in assignments_by_class:
                    assignments_by_class[class_name] = []
                assignments_by_class[class_name].append(assignment)

            for class_name, assignments in assignments_by_class.items():
                with st.expander(f"{class_name} Assignments:"):
                    for assignment in assignments:
                        st.write(f"**Assignment**: {assignment.name}, **Due Date**: {assignment.dueDate}")
        else:
            st.write("No assignments to show for the selected filter.")

    with tasksSettings:
        Show_Tasks_By_Date = st.radio(
            "Show Tasks by date:",
            ["All Assignments", "Day", "Week", "Month", "Custom Date", "No due-date only"],
            index=["All Assignments", "Day", "Week", "Month", "Custom Date", "No due-date only"].index(st.session_state.show_tasks_by_date),
            key="show_tasks_by_date_radio_unique"
        )
        st.session_state.show_tasks_by_date = Show_Tasks_By_Date

        if Show_Tasks_By_Date == "Custom Date":
            custom_date_value = st.session_state.get("custom_reminder_1_date", date.today())
            if isinstance(custom_date_value, str):
                custom_date_value = date.fromisoformat(custom_date_value)

            custom_date = st.date_input("Select Custom Date", value=custom_date_value)
            st.session_state["custom_reminder_1_date"] = custom_date
            filtered_assignments = filter_tasks_by_custom_date(selected_classes, custom_date)
            #st.write(f"Filtered assignments after custom date filter: {filtered_assignments}")
        elif Show_Tasks_By_Date == "Day":
            filtered_assignments = filter_tasks_by_day(selected_classes)
        elif Show_Tasks_By_Date == "Week":
            filtered_assignments = filter_tasks_by_week(selected_classes)
        elif Show_Tasks_By_Date == "Month":
            filtered_assignments = filter_tasks_by_month(selected_classes)
        elif Show_Tasks_By_Date == "All Assignments":
            filtered_assignments = filter_tasks_none(selected_classes)
        elif Show_Tasks_By_Date == "No due-date only":
            filtered_assignments = [
            (class_data.name, assignment)
            for class_data in selected_classes
            for assignment in class_data.assignmentList
            if not assignment.dueDate or assignment.dueDate.lower() == "none"
        ]

        st.session_state.filtered_assignments = filtered_assignments

        if st.button("Apply Changes", key="save_all_settings_btn"):
            save_settings(**st.session_state)
            st.success("Changes applied successfully!")

    calendar, calendarSettings = st.tabs(["Calendar", "Calendar Settings"])

    with calendarSettings:
        settings_ui()  

    with calendar:
       
        calendar_events = [
            {
                "title": f"{class_name} - {assignment.name}",
                "start": clean_due_date(assignment.dueDate).strftime("%Y-%m-%d") if clean_due_date(assignment.dueDate) else None,
                "description": f"{class_name}: {assignment.name}",
                "extendedProps": {
                    "assignment_name": assignment.name,
                    "class_name": class_name
                }
            }
            for class_name, assignment in filtered_assignments
            if assignment.dueDate
        ]
        calendar_events_json = json.dumps(calendar_events)

        # Dynamically update font size, font color, and font type
        font_size = st.session_state.get("font_size", 12)
        font_color = st.session_state.get("font_color", "#000000")
        font_type = st.session_state.get("font_type", "Roboto")

        calendar_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link href="https://cdn.jsdelivr.net/npm/fullcalendar/main.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/fullcalendar/main.min.js"></script>
            <style>
                .fc-event-title {{
                    max-width: 200px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: normal;
                    word-wrap: break-word;
                    font-size: {font_size}px;
                    color: {"#FFFFFF" if int(font_color.lstrip("#"), 16) < 0x888888 else "#000000"}; /* Adjusts text color for contrast */
                    font-family: {font_type};
                }}
                .fc-event {{
                    background-color: {font_color};  /* Use font color as background */
                    border: none;  /* Removes border for a cleaner look */
                    padding: 5px;
                }}
                .fc-event.fc-h-event {{
                    white-space: normal !important;
                }}
            </style>
        </head>
        <body>
            <div id="calendar"></div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var calendarEl = document.getElementById('calendar');
                    var calendar = new FullCalendar.Calendar(calendarEl, {{
                        initialView: 'dayGridMonth',
                        events: {calendar_events_json},  // Ensure events data is inserted correctly
                        eventClick: function(info) {{
                            var event = info.event;  // Get the clicked event
                            var details = `Class: ${{
                                event.extendedProps.class_name}}\\nAssignment: ${{
                                event.extendedProps.assignment_name}}\\nDue Date: ${{
                                event.start.toLocaleDateString()}}`;
                            alert(details);  // Display event details
                        }},
                        eventRender: function(info) {{
                            info.el.title = info.event.extendedProps.assignment_name;  // Show full assignment name as a tooltip
                        }},
                    }});
                    calendar.render();
                }});
            </script>
        </body>
        </html>
        """

        # Display the calendar
        components.html(calendar_html, height=700, width=700)

if st.session_state.isLoggedIn:
    showNavigationBar()
    tasksPageView()
else:
    st.text("Please log in to view the Tasks page.")



