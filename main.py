import streamlit as st
from streamlit_navigation_bar import st_navbar
import app
import translate

# Set page configuration here
st.set_page_config(page_title="Doctor AI Assistant", page_icon="assets/Dsahicon.png")


# Create the navigation bar
page = st_navbar(["AI Doctor Assistant", "Medical Report Translator"])

# Conditional rendering based on the selected page
if page == "AI Doctor Assistant":
    app.app()  # Call the app function from app.py
else:
    translate.translate()  # Call the translate function from translate.py


