import streamlit as st
from user import register

st.title("Register")

def registerPageView():

    #This is the User components responsibilty: we need to register as a user so 
    register()

    login = st.button("Log in")
    if login:
        st.switch_page("loginPage.py")

registerPageView()

