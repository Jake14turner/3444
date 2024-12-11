import streamlit as st
import sqlite3 as sqlite3
from user import login
from user import initializeUserInfoJSON
from user import sortUserDataIntoList

st.title("Login")

st.session_state.isLoggedIn = False

def loginPageView():
    #This is the responsiblity of the User component: we need to allow someone to log into an account 
    success = login()
    if success:
        st.session_state.isLoggedIn = True
        username = st.session_state.username
        st.session_state.data = initializeUserInfoJSON(username)
        st.session_state.studentInfo = sortUserDataIntoList(st.session_state.data)
        st.switch_page("homePage.py")
    else:
        st.session_state.isLoggedIn = False

loginPageView()

