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
pages = ["AI Doctor Assistant", "Medical Report Translator"]
styles = {
    "nav": {
        "background-color": "#990033",
        "justify-content": "center",
        "align-items": "center",
        "flex-direction": "row",
        "color": "white",
        "fontsize": "0.5rem",
        "gap": "0.5rem",
        "transition": "all 0.3s ease-in-out",
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px 40px",  # Adjusted padding for button-like appearance
        "font-size": "16px",
        "line-height": "1.5",
        "font-weight": "600",
        "border": "2px solid",
        "border-image": "linear-gradient(to right, rgb(182, 244, 146), rgb(73, 187, 216)) 1",
        "background": "rgba(153, 0, 51, 0.95)",  # Match navbar background with slight transparency
        "backdrop-filter": "blur(7px)",
        "position": "relative",
        
    },
    "active": {
        "background": "rgba(255, 255, 255, 0.5)",
        "backdrop-filter": "blur(10px)",
        "color": "black",
        "font-weight": "bold",
        "padding": "14px",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.3)",  # Hover effect
        "transform": "scale(1.5)",  # Scaling effect on hover
        "transition": "all 200ms ease-out",
    },
}



# Pass the list and styles directly
page = st_navbar(pages, styles=styles)

# Conditional rendering based on the selected page
if page == "AI Doctor Assistant":
    app.app()  # Call the app function from app.py
else:
    translate.translate()  # Call Call the translate function from translate.py # Call the translate function from translate.py