import streamlit as st
from streamlit_navigation_bar import st_navbar
import app
import translate

# Set page configuration
st.set_page_config(
    page_title="Doctor AI Assistant",
    page_icon="assets/Dsahicon.png",
    initial_sidebar_state="collapsed"
)

# Create the navigation bar with styles
pages = ["AI Doctor Assistant", "Medical Report Translator"]
styles = {
    "nav": {
        "background-color": "rgb(123, 209, 146)",
        "fontsize":"0.5rem",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "rgb(49, 51, 63)",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
        "fontsize":"0.5rem"
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
}

# Pass the list and styles directly
page = st_navbar(pages, styles=styles)

# Conditional rendering based on the selected page
if page == "AI Doctor Assistant":
    app.app()  # Call the app function from app.py
else:
    translate.translate()  # Call the translate function from translate.py


