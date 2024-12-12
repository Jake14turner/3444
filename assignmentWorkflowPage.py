import sqlite3
import streamlit as st
from navigationUI import showNavigationBar
from database import createSubtaskDB, addSubTaskToDB, getSubTasksFromDB, updateSubTaskstatus, deleteSubtask




createSubtaskDB()

class Assignment:
    def __init__(self, name, dueDate, pointsPossible):
        self.name = name
        self.dueDate = dueDate
        self.pointsPossible = pointsPossible

class Class:
    def __init__(self, name, assignmentList):
        self.name = name
        self.assignmentList = assignmentList


def assignmentWorkflowPage():
  
    st.title(":clipboard: Assignment Breakdown")

    if "studentInfo" not in st.session_state:
        st.session_state.studentInfo = [
            Class("Math", [
                Assignment("Algebra Homework", "2024-12-15", 10),
                Assignment("Geometry Quiz", "2024-12-20", 20)
            ]),
            Class("Science", [
                Assignment("Lab Report", "2024-12-18", 15),
                Assignment("Final Exam", "2024-12-22", 50)
            ])
        ]


    classNamesList = [cls.name for cls in st.session_state.studentInfo]
    individualClass = st.selectbox("Select a Class", classNamesList)

    if individualClass:

        individualClassObjet = next(cls for cls in st.session_state.studentInfo if cls.name == individualClass)
        assignmentList = [assignment.name for assignment in individualClassObjet.assignmentList]
        selectedAssignment = st.selectbox("Select an Assignment", assignmentList)

        if selectedAssignment:
            st.markdown(f"### {selectedAssignment} Subtasks")
            

            individualSubTask = st.text_input("Enter a subtask", key=f"input_{selectedAssignment}")
            if st.button("Add Subtask", key=f"add_{selectedAssignment}") and individualSubTask:
                addSubTaskToDB(selectedAssignment, individualSubTask)

            subtasks = getSubTasksFromDB(selectedAssignment)
            for subtask_id, individualSubTask, completed in subtasks:
                col1, col2 = st.columns((8, 2))
                with col1:
               
                    subtask_text = f"~~{individualSubTask}~~" if completed else individualSubTask
                    st.markdown(subtask_text)
                with col2:
   
                    if st.checkbox("Complete", key=f"{selectedAssignment}_{subtask_id}", value=completed):
                        updateSubTaskstatus(selectedAssignment, individualSubTask, True)
                        deleteSubtask(subtask_id) 

if st.session_state.get('isLoggedIn', False):
    showNavigationBar()
    assignmentWorkflowPage()
else:
    st.text("Please log in to view the Assignment Workflow page.")
    st.switch_page("registerPage.py")

