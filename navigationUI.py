import streamlit as st
from user import logout
import streamlit.components.v1 as components


def showNavigationBar():

    #CSS for button styling
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #F25F06;
            color: white;
            font-size: 50px ;
            border-radius: 10px;
            border: 2px solid #FF4500; /* Orange Red */
            padding: 10px 20px;
            margin: 10px 0;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #FF4500; /* Orange Red */
            color: white;
        }
        </style>
        """, unsafe_allow_html=True
        )

    col1, col2, col3, col4, col5, col6, col7 = st.columns((0.5, 3, 5, 3, 2, 3, 2))
    with col1:
        st.page_link("homePage.py", label=":orange[$\\large \\sf{Home}$]")
    with col2:
        st.page_link("tasksPage.py", label=":orange[$\\large \\sf{Assignment}$ $\\large \\sf{}$ $\\large \\sf{Manager}$]")
    with col3:
        st.page_link("toDoPage.py", label=":orange[$\\large \\sf{View}$ $\\large \\sf{}$ $\\large \\sf{All}$ $\\large \\sf{}$ $\\large \\sf{Assignments}$]")
    with col4:
        st.page_link("customSchedulePage.py", label=":orange[$\\large \\sf{View}$ $\\large \\sf{}$ $\\large \\sf{Custom}$ $\\large \\sf{}$ $\\large \\sf{Schedule}$]")
    with col5:
        st.page_link("overviewPage.py", label=":orange[$\\large \\sf{Overview}$]") 
    with col6:
        st.page_link("assignmentWorkflowPage.py", label=":orange[$\\large \\sf{Assignment}$ $\\large \\sf{}$ $\\large \\sf{workflow}$]")
    with col7:
        if st.button("Logout"):
            logout()

