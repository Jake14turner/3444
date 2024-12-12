import streamlit as st
import sqlite3
import json
from database import checkForAndInitializeAssignmentTimeEstimates, save_time_estimates_to_db, retrieve_time_estimates_from_db, checkForAndInitializeDaysAvailableToWork, saveDaysAvailableToDB, retrieveDaysAvailableFromDB
from schedules import filterAssignments, generate_weeks_schedule, Assignment
from navigationUI import showNavigationBar


if 'isLoggedIn' not in st.session_state:
    st.session_state.isLoggedIn = False

if 'counter' not in st.session_state:
    st.session_state.counter = 0

if 'info' not in st.session_state:
    st.session_state.info = []

if 'username' not in st.session_state:
    st.session_state.username = ''

if st.session_state.username != '':
    if st.session_state.counter == 0:
        username = st.session_state.username
        data = st.session_state.data
        filteredList = filterAssignments(st.session_state.studentInfo)
        st.session_state.info = filteredList
        st.session_state.counter = st.session_state.counter + 1

def toggle_assignment_time():
    st.session_state.configureAssignmentTimes = not st.session_state.configureAssignmentTimes




if "show_dropdown" not in st.session_state:
    st.session_state.show_dropdown = False

if "show_dropdown2" not in st.session_state:
    st.session_state.show_dropdown2 = False

# Function to toggle the visibility
def toggle_dropdown():
    st.session_state.show_dropdown = not st.session_state.show_dropdown

def toggle_dropdown2():
    st.session_state.show_dropdown2 = not st.session_state.show_dropdown2


def customSchedulePage():

    st.title("Custom Schedule Page :material/access_time:")

    st.markdown("To use this tool, firstly click on \"edit assignment time estimates\", fill in how long each assignemnt will take you, and then click on \"edit available days\" then put in what days you are available and for how many hours, then click generate schedule!")

    username = st.session_state.username


    if st.button("Edit assignment time estimates"):
        toggle_dropdown()

    if st.session_state.show_dropdown:
        with st.form("time_estimation_form"):
        

        

            time_estimates = {}

            for class_info in st.session_state.info:
                with st.expander(f"{class_info.name}"):
                    for assignment in class_info.assignmentList:
                        label = f"{assignment.name}"
                        key = f"{class_info.name}_{assignment.name}_time_estimate"

                        
                        if key not in st.session_state:
                            st.session_state[key] = 0.0

                        time_estimate = st.number_input(
                            label=label,
                            min_value=0.0,
                            step=0.5,
                            key=key
                        )

                        time_estimates[key] = st.session_state[key]
            submitted1 = st.form_submit_button("Submit Estimates")

            if submitted1:
                #save to the db
                save_time_estimates_to_db(username, time_estimates)
                st.session_state.configureAssignmentTimes = False


    if st.button("Edit available Days"):
        toggle_dropdown2()

    if st.session_state.show_dropdown2:
            with st.form("days_available_form"):
                st.write("Select the number of hours you can work each day:")

            
                monday_hours = st.number_input("Monday", min_value=0, max_value=24, step=1)
                tuesday_hours = st.number_input("Tuesday", min_value=0, max_value=24, step=1)
                wednesday_hours = st.number_input("Wednesday", min_value=0, max_value=24, step=1)
                thursday_hours = st.number_input("Thursday", min_value=0, max_value=24, step=1)
                friday_hours = st.number_input("Friday", min_value=0, max_value=24, step=1)
                saturday_hours = st.number_input("Saturday", min_value=0, max_value=24, step=1)
                sunday_hours = st.number_input("Sunday", min_value=0, max_value=24, step=1)

                
                submitted2 = st.form_submit_button("Submit")


                if submitted2:
                    
                    daysAvailable = [monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours, saturday_hours, sunday_hours]
                    saveDaysAvailableToDB(username, daysAvailable)
                    st.session_state.configure_days_available = False



    if st.button("Generate Schedule"):
                
        weeks = generate_weeks_schedule(username)

        st.success("Schedule Generated!")
        for week in weeks:
            with st.expander(f"Week {week.week_number} Schedule"):
                week_schedule = week.display()
                for day_index, tasks in week_schedule.items():
                    day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_index]
                    st.write(f"**{day_name}:**")
                    for task in tasks:
                        st.write(f"- {task['name']}: {task['time']} hours")









if st.session_state.isLoggedIn:
    showNavigationBar()
    customSchedulePage()
else:
    st.text("Please log in to view the scheduler page.")
    st.switch_page("registerPage.py")

