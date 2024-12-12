import streamlit as st
import streamlit.components.v1 as components
from calenderUI import generateCalanderUI
from navigationUI import showNavigationBar



#this is the UI component's responsibility: we need to check if the token is saved or not. If the bool variable to check is not present create it and set it to false until the token is saved.
if 'token_saved' not in st.session_state:
    st.session_state.token_saved = False

if 'isLoggedIn' not in st.session_state:
    st.session_state.isLoggedIn = False

if 'hasKey' not in st.session_state:
    st.session_state.hasKey = False

if 'data' not in st.session_state: # I Crrine added this line, code was throwing an error without it, feel free to remove
    st.session_state.data = {} 

def homePageView():
    #this is the user component's responsibility: here we need to check if the user has a key registered with us, if not, prompt them to do so.
    username = st.session_state.username

    #connection point between UI and User. We call user function to return a json file for the UI to display
        
    htmlCode = generateCalanderUI(username)
   # calendarHTML = htmlCode

    # Render the calendar
    components.html(
        htmlCode,
        height=840 
    ) 
    
#this is the responisbility of UI component: Check if the user has logged in, if they have then they can access the home page, other wise tell them to go log in.
if st.session_state.isLoggedIn:
    showNavigationBar()
    homePageView()
else:
    st.text("Please log in to view home page.")
    st.switch_page("registerPage.py")
