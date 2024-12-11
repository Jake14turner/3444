import streamlit as st
import pandas as pd
import sqlite3
from user import loadGrades
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import saveGradesToDB, loadGradesFromDB
from user import getNextThreeAssignments, parseDueDate, displayNextThreeAssignments, convertToDictionary, displayAssignmentsWithAverage, displayPieChart, displayProgressBar, displayAssignmentsWithAverageNoText, refresh_grades
from navigationUI import showNavigationBar


def overviewPage(information):
    st.title("Class Progress Visualization Page :pie_chart:")

    if information:
        grade_dicts = convertToDictionary(information)

        grouped_assignments = {}
        for assignment in grade_dicts:
            class_name = assignment["class_name"]
            if class_name not in grouped_assignments:
                grouped_assignments[class_name] = []
            grouped_assignments[class_name].append(assignment)

        for course in st.session_state.studentInfo:
            class_title_html = f"""
                <div style="
                    text-align: center;
                    padding: 10px;
                    margin-bottom: 20px;
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                    <h2 style="margin: 0; color: #1e88e5;">{course.name}</h2>
                </div>
            """
            st.markdown(class_title_html, unsafe_allow_html=True)

            course_assignments = grouped_assignments.get(course.name, [])
            average_percentage, total_score, total_possible = displayAssignmentsWithAverageNoText(course_assignments)

            if average_percentage is not None:
                color = (
                    "green" if average_percentage > 90 else
                    "yellow" if average_percentage > 70 else
                    "red"
                )
                styled_avg = f"<span style='color: {color}; font-size: 1.2em;'><b>{average_percentage:.2f}%</b></span>"
                st.markdown(f"### Average Grade: {styled_avg}", unsafe_allow_html=True)
            else:
                st.markdown("### Average Grade: <span style='color: gray;'>No graded assignments</span>", unsafe_allow_html=True)

 
            displayProgressBar(total_score, total_possible)

            col1, col2 = st.columns([2, 2])

            with col1:
                st.markdown("### Assignment Completion Status")
                displayPieChart(course.name, course_assignments)

            with col2:
                with st.expander(f"{course.name} Grades"):
                   displayAssignmentsWithAverage(course_assignments)

                st.markdown("""
                    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
                        <h3 style="margin: 0; color: #333;">Next 3 Assignments</h3>
                        <div style="margin-top: 10px;">
                """, unsafe_allow_html=True)

                upcoming_assignments = getNextThreeAssignments(course)
                displayNextThreeAssignments(upcoming_assignments)

                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)
          
    else:
        st.text("No grade information available.")

if 'isLoggedIn' not in st.session_state:
    st.session_state.isLoggedIn = False

if 'info' not in st.session_state:
    st.session_state.info = []

if 'username' not in st.session_state:
    st.session_state.username = ''


    


if st.session_state.isLoggedIn:
    showNavigationBar()
    if st.button("Refresh Grades"):
        refresh_grades()
    information = loadGradesFromDB(st.session_state.username)
    if information:
        st.text("IT loaded")
    else:
        st.text("IT did not load")
    overviewPage(information)
else:
    st.text("Please log in to view the Class Visualization Page.")

