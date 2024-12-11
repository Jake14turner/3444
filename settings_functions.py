import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import re
import hashlib
from user import sortUserDataIntoList, initializeUserInfoJSON
import calendar
import streamlit.components.v1 as components


def init_db():
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT UNIQUE,
            email_notifications TEXT,
            summary_reminder TEXT,
            show_tasks_by_date TEXT,
            show_no_due_date TEXT,  
            show_completed_tasks BOOLEAN,
            task_priority TEXT,
            task_notifications TEXT,
            task_reminders TEXT,
            custom_reminder_1_date TEXT,
            custom_reminder_2_date TEXT,
            font_color TEXT,
            font_type TEXT,
            font_size REAL
        )
    ''')

    # Dynamically add missing columns
    c.execute('PRAGMA table_info(user_settings)')
    columns = [column[1] for column in c.fetchall()]

    if 'show_no_due_date' not in columns:
        c.execute('ALTER TABLE user_settings ADD COLUMN show_no_due_date TEXT')

    # Ensure valid font_color values
    c.execute('''
        UPDATE user_settings
        SET font_color = '#000000'
        WHERE font_color NOT LIKE '#%' OR LENGTH(font_color) NOT IN (4, 7);
    ''')

    conn.commit()
    conn.close()

def save_settings(**kwargs):
    try:
        # Convert dates to string before saving to DB
        kwargs['custom_reminder_1_date'] = str(kwargs.get('custom_reminder_1_date', date.today()))
        kwargs['custom_reminder_2_date'] = str(kwargs.get('custom_reminder_2_date', date.today() + timedelta(days=1)))

        conn = sqlite3.connect('settings.db')
        c = conn.cursor()

        user_email = kwargs.get("user_email", None)
        c.execute("SELECT id FROM user_settings WHERE user_email = ?", (user_email,))
        existing_record = c.fetchone()

        if existing_record:
            c.execute('''
                UPDATE user_settings SET 
                    email_notifications = :email_notifications,
                    summary_reminder = :summary_reminder,
                    show_tasks_by_date = :show_tasks_by_date,
                    show_no_due_date = :show_no_due_date,
                    show_completed_tasks = :show_completed_tasks,
                    task_priority = :task_priority,
                    task_notifications = :task_notifications,
                    task_reminders = :task_reminders,
                    custom_reminder_1_date = :custom_reminder_1_date,
                    custom_reminder_2_date = :custom_reminder_2_date,
                    font_color = :font_color,
                    font_type = :font_type,
                    font_size = :font_size
                WHERE user_email = :user_email
            ''', kwargs)
        else:
            c.execute('''
                INSERT INTO user_settings (
                    user_email, email_notifications, summary_reminder, show_tasks_by_date, 
                    show_no_due_date, show_completed_tasks, task_priority, task_notifications, task_reminders, 
                    custom_reminder_1_date, custom_reminder_2_date, font_color, font_type, font_size
                ) VALUES (
                    :user_email, :email_notifications, :summary_reminder, :show_tasks_by_date,
                    :show_no_due_date, :show_completed_tasks, :task_priority, :task_notifications, :task_reminders,
                    :custom_reminder_1_date, :custom_reminder_2_date, :font_color, :font_type, :font_size
                )
            ''', kwargs)

        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error saving settings: {e}")
        print(f"Error saving settings: {e}")
        conn.rollback()
        conn.close()



def load_settings(user_email=None):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
        SELECT user_email, email_notifications, summary_reminder, show_tasks_by_date, 
               show_no_due_date, show_completed_tasks, task_priority, task_notifications, task_reminders,
               custom_reminder_1_date, custom_reminder_2_date, font_color, font_type, font_size
        FROM user_settings WHERE user_email = ?
    ''', (user_email,))
    settings = c.fetchone()
    conn.close()

    # Default values if no settings are found
    if not settings:
        return {
            "user_email": user_email,
            "email_notifications": "Off",
            "summary_reminder": "Daily",
            "show_tasks_by_date": "Day",
            "show_no_due_date": False,
            "show_completed_tasks": False,
            "task_priority": "",
            "task_notifications": "Off",
            "task_reminders": "30 Minutes",
            "custom_reminder_1_date": "2024-12-31",
            "custom_reminder_2_date": "2024-12-31",
            "font_color": "#000000",
            "font_type": "Roboto",
            "font_size": 12
        }

    # Return as a dictionary
    keys = [
        "user_email", "email_notifications", "summary_reminder", "show_tasks_by_date", 
        "show_no_due_date", "show_completed_tasks", "task_priority", "task_notifications", 
        "task_reminders", "custom_reminder_1_date", "custom_reminder_2_date", 
        "font_color", "font_type", "font_size"
    ]
    
    # Convert custom reminder dates back to date objects if they exist
    settings_dict = dict(zip(keys, settings))
    settings_dict["custom_reminder_1_date"] = date.fromisoformat(settings_dict["custom_reminder_1_date"])
    settings_dict["custom_reminder_2_date"] = date.fromisoformat(settings_dict["custom_reminder_2_date"])
    
    return settings_dict


def sync_session_state(settings):
    for key, value in settings.items():
        if key not in st.session_state:
            st.session_state[key] = value

        # Validate font_size
        if key == "font_size":
            try:
                st.session_state[key] = int(value)
            except ValueError:
                st.session_state[key] = 12

        # Validate custom reminder dates
        if key.startswith("custom_reminder") and value:
            try:
                
                if isinstance(value, str):
                    st.session_state[key] = date.fromisoformat(value)
                elif isinstance(value, date):
                    st.session_state[key] = value  
                else:
                    # Handle unexpected types
                    st.session_state[key] = date(2024, 12, 31)  
            except ValueError:
                # Handle invalid date format
                st.session_state[key] = date(2024, 12, 31)  
       

def apply_default_session_state():
    default_values = {
        "username": None,
        "email_notifications": "Off",
        "show_tasks_by_date": "Day",
        "show_no_due_date": False,
        "show_completed_tasks": False,
        "task_priority": "",
        "font_color": "#000000",
        "font_type": "Roboto",
        "font_size": 12,
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sanitize_key(name: str, index: int = None, extra: str = "") -> str:
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_'))
    key = sanitized_name
    if index is not None:
        key += f"_{index}"
    if extra:
        key += f"_{extra}"
    return key

def validate_hex_color(color_code):
    if re.match(r'^#[0-9A-Fa-f]{6}$', color_code):
        return color_code
    return "#000000"  # Default to black if the color code is invalid

# Data models
class Class:
    def __init__(self, name, assignmentList):
        self.name = name
        self.assignmentList = assignmentList

class Assignment:
    def __init__(self, name, dueDate):
        self.name = name
        self.dueDate = dueDate

# Utility functions
def taskView(class_name, assignments):
    if assignments:
        with st.expander(f"{class_name} Assignments:"):
            for assignment in assignments:
                st.write(f"**Assignment**: {assignment.name}, **Due Date**: {assignment.dueDate}")
    else:
        st.write("No assignments to show.")
def displayAssignments(username):
    """
    Displays assignments in the Tasks column for selected classes.
    Only the classes that have their checkbox checked will display assignments.
    """
    if not username:
        st.error("Please log in.")
        return []

    studentInfo = st.session_state.studentInfo

    # Loop through all assignments
    for user_class in studentInfo:
        for assignment in user_class.assignmentList:
            # Additional code for display
            taskView(user_class.name, user_class.assignmentList)

def clean_due_date(due_date):
    """Convert due_date string to a datetime.date object."""
    if due_date:
        if 'T' in due_date:
            due_date = due_date.split('T')[0]
        return datetime.strptime(due_date, '%Y-%m-%d').date() 
    return date.today()

    
def filter_tasks_by_day(selected_classes):
    """Filter tasks due today."""
    current_date = datetime.now().date()
    return [
        (class_data.name, assignment)
        for class_data in selected_classes
        for assignment in class_data.assignmentList
        if assignment.dueDate and clean_due_date(assignment.dueDate) == current_date
    ]

def filter_tasks_by_week(selected_classes):
    """Filter tasks due this week."""
    current_date = datetime.now()
    week_start = current_date - timedelta(days=current_date.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    return [
        (class_data.name, assignment)
        for class_data in selected_classes
        for assignment in class_data.assignmentList
        if assignment.dueDate
        and week_start.date() <= clean_due_date(assignment.dueDate) <= week_end.date()
    ]

def filter_tasks_by_month(selected_classes):
    """Filter tasks due this month."""
    current_date = datetime.now()
    first_of_month = current_date.replace(day=1)
    next_month = first_of_month + timedelta(days=31)
    first_of_next_month = next_month.replace(day=1)
    return [
        (class_data.name, assignment)
        for class_data in selected_classes
        for assignment in class_data.assignmentList
        if assignment.dueDate
        and first_of_month.date() <= clean_due_date(assignment.dueDate) < first_of_next_month.date()

    ]

def filter_tasks_by_custom_date(selected_classes, custom_date):
    """Filter tasks due on a custom date."""
    filtered = [
        (class_data.name, assignment)
        for class_data in selected_classes
        for assignment in class_data.assignmentList
        if assignment.dueDate and clean_due_date(assignment.dueDate) == custom_date
    ]
    return filtered


def filter_tasks_none(selected_classes):
    """Return all tasks without filtering."""
    return [
        (class_data.name, assignment)
        for class_data in selected_classes
        for assignment in class_data.assignmentList
    ]

def practiceView():
    """
    Displays checkboxes for classes and ensures that the assignments update correctly
    when the checkbox is checked or unchecked.
    """
    username = st.session_state.get("username", None)
    if not username:
        st.error("Please log in.")
        return []

    # Fetch user data and sort it
    studentInfo = st.session_state.studentInfo
    # Initialize session state for selected classes if not present
    if "selected_classes" not in st.session_state:
        st.session_state.selected_classes = []

    # Temporarily hold selected classes within the same interaction cycle
    updated_selected_classes = []

    # Render checkboxes for each class
    for class_data in studentInfo:
        class_checkbox_key = f"show_{class_data.name}"
        is_checked = st.checkbox(class_data.name, key=class_checkbox_key)

        #
        if is_checked:
            updated_selected_classes.append(class_data)

    # Update session state for selected classes
    st.session_state.selected_classes = updated_selected_classes

    return updated_selected_classes



def settings_ui():
    apply_default_session_state()

    # Include Google Fonts link for Lobster
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Lobster&display=swap" rel="stylesheet">
        """, 
        unsafe_allow_html=True
    )

    with st.form("settings_form"):
        st.subheader("Calendar Settings")
        
        st.session_state["font_color"] = st.color_picker("Font Color", value=st.session_state.get("font_color", "#000000"))
        st.session_state["font_type"] = st.selectbox("Font Type", ["Roboto", "Arial", "Courier New", "Comic Sans MS", "Lobster"], index=0)
        
        # Font Size Slider with explicit update handling
        new_font_size = 12
        if new_font_size != st.session_state["font_size"]:
            st.session_state["font_size"] = 12

        submitted2 = st.form_submit_button("Apply Calendar Changes")
        if submitted2:
            save_settings(**st.session_state)
            st.success("Calendar Updated successfully!")

    # Apply selected font using CSS
    font_type = st.session_state.get("font_type", "Roboto")

    st.markdown(
        f"""
        <style>
            body {{
                font-family: {font_type}, sans-serif;
            }}
        </style>
        """, 
        unsafe_allow_html=True
    )






