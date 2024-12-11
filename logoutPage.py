import streamlit as st
import time


col1, col2, col3 = st.columns(3)
with col1:
    st.write(' ')

with col2:
    st.info("Logged out successfully!")

with col3:
    st.write(' ')
    time.sleep(0.5)
    st.switch_page("registerPage.py")
