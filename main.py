import streamlit as st
from notifications import run_background_scheduler
from database import create_assignments_table
from user import run_reminder_in_background
from user import initialize_user_assignments

st.set_page_config(layout="wide")

if "isLoggedIn" not in st.session_state:
    st.session_state.isLoggedIn = False
    

if st.session_state.isLoggedIn and st.session_state.username:
    initialize_user_assignments(st.session_state.username)
# Start background reminder system
    run_reminder_in_background()

# Ensure the assignments table exists
create_assignments_table()


if "assignmentsArray" not in st.session_state:
    st.session_state.assignmentsArray = []  # Placeholder for assignments array

if st.session_state.assignmentsArray and st.session_state.username:
    run_background_scheduler(st.session_state.assignmentsArray, st.session_state.username)




registerPage = st.Page("registerPage.py", title="Register", icon=":material/person_add:")
loginPage = st.Page("loginPage.py", title="Login", icon=":material/login:")
homePage = st.Page("homePage.py", title="Home", icon=":material/calendar_today:")
toDoPage = st.Page("toDoPage.py", title="To Do List", icon=":material/note:")
customSchedulePage = st.Page("customSchedulePage.py", title="Custom Schedule", icon=":material/access_time:")
tasksPage = st.Page("tasksPage.py", title="Tasks Page", icon=":material/add_circle:")
logoutPage = st.Page("logoutPage.py", title="Logout Page", icon=":material/logout:")
overviewPage = st.Page("overviewPage.py", title="Over view Page")
assignmentWorkflowPage = st.Page("assignmentWorkflowPage.py", title="Assignment Work Flow Page")

#idkyetPage = st.Page("idkyet.py", title="idk yet", icon=":material/pie_chart:")


pg = st.navigation([registerPage, loginPage, homePage, toDoPage, tasksPage, customSchedulePage, overviewPage, assignmentWorkflowPage, logoutPage], position="hidden")

pg.run()


