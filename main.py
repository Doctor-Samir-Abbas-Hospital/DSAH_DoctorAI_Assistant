import streamlit as st
from streamlit_navigation_bar import st_navbar
import app
import translate
# Set page configuration
st.set_page_config(
    page_title="Doctor AI Assistant",
    page_icon="assets/Dsahicon.png",
)

# Create the navigation bar with styles
pages = ["Doctor AI Assistant", "Medical Report Translator"]
styles = {
    "nav": {
        "background-color": "#990033",
        "display":"flex",
        "justify-content": "center",
        "align-items": "center",
        "flex-direction": "row",
        "color": "white",
        "font-size": "0.5rem",
        "transition": "all 0.3s ease-in-out",
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "7px 30px",  # Adjusted padding for both inactive and active
        "font-size": "16px",
        "line-height": "1.5",
        "margin":"5px",
        "font-weight": "600",
        "background": "#990033",  # Matches navbar background
        "border-radius": "10px",
        "box-shadow": "4px 4px 8px 0px rgba(0, 0, 0, 0.15), -2px -1px 10px 0px rgba(255, 255, 255, 0.75), 2px 1px 1px 0px rgba(255, 255, 255, 0.25), -2px -2px 2px 0px rgba(0, 0, 0, 0.1) inset, 2px 2px 5px 0px rgba(255, 255, 255, 0.5) inset;",  # Outward shadow for 3D effect
        "transition": "0.3s linear",
    },
    "active": {
        "color": "black",  # Black text color
        "font-weight": "bold",
        "padding": "7px 30px",  # Same padding as inactive
        "background": "white",  # White background for active button
        "border": "2px solid rgba(255, 255, 255, 0.5)",  # Border to outline the button
        "box-shadow": "2px 2px 10px 0px rgba(0, 0, 0, 0.15) inset, -2px -2px 10px 5px rgba(255, 255, 255, 0.5) inset, -2px -2px 2px 0px rgba(0, 0, 0, 0.15), 2px 2px 10px 0px rgba(255, 255, 255, 0.5);",  # Inward shadow for pressed effect
        "border-radius": "10px",
        "transition": "0.3s linear",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.1)",  # Subtle hover effect
        "box-shadow": "4px 4px 8px 0px rgba(0, 0, 0, 0.15), -2px -1px 10px 0px rgba(255, 255, 255, 0.75), 2px 1px 1px 0px rgba(255, 255, 255, 0.25), -2px -2px 2px 0px rgba(0, 0, 0, 0.1) inset, 2px 2px 5px 0px rgba(255, 255, 255, 0.5) inset;",  # Retain 3D effect on hover
    },
}
# Pass the list and styles directly
page = st_navbar(pages, styles=styles)

# Conditional rendering based on the selected page
if page == "Doctor AI Assistant":
    app.app()  # Call the app function from app.py
elif page=="Medical Report Translator":
    translate.translate()  # Call Call the translate function from translate.py # Call the translate function from translate.py
   