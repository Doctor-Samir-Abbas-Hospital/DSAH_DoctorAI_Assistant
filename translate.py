import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO
import arabic_reshaper  # To reshape Arabic text
from bidi.algorithm import get_display  # To handle bidirectional text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from utils.functions import (
    get_vector_store,
    get_response_,
)

# Load environment variables
load_dotenv()

# Register Arabic font (Arial)
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
addMapping('Arial', 0, 0, 'Arial')

def reshape_arabic_text(text):
    """Reshapes and applies bidi formatting for Arabic text."""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def create_pdf(translated_text):
    """Creates a well-formatted PDF using ReportLab."""
    
    # Create a PDF canvas
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Set document metadata
    c.setTitle("Translated Medical Report")
    c.setAuthor("Doctor AI Assistant")

    # Set up page sizes and margins
    width, height = A4
    margin = inch
    c.translate(margin, height - margin)

    # Add a title
    c.setFont('Arial', 18)
    title_text = "تقرير طبي شامل"
    bidi_title = reshape_arabic_text(title_text)
    c.drawRightString(width - inch, -inch, bidi_title)

    # Add a horizontal line
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.black)
    c.line(inch, -1.5 * inch, width - inch, -1.5 * inch)

    # Add the body of the report
    c.setFont('Arial', 12)
    bidi_text = reshape_arabic_text(translated_text)
    
    # Draw the report text, starting from the right
    lines = bidi_text.split('\n')
    y = -2 * inch
    for line in lines:
        c.drawRightString(width - inch, y, line)
        y -= 14  # Line spacing

    # Add page number
    c.setFont("Arial", 10)
    c.drawRightString(width - inch, -11 * inch, "Page 1")

    # Finish the PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

def translate():
    # Initialize session state variables
    if "translate_state" not in st.session_state:
        st.session_state.translate_state = {}

    if "chat_history1" not in st.session_state:
        st.session_state.chat_history1 = []  # Initialize chat_history
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()

    # Upload file section in Streamlit
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    with st.sidebar:
        st.title("Doctor AI Assistant")
        st.subheader("Upload a PDF medical report for translation")
        uploaded_file = st.file_uploader("Upload a medical report (PDF)", type=["pdf"])

    # Process uploaded PDF file and translate
    if uploaded_file:
        translate_button = st.button("Translate The Medical Report")
        if translate_button:
            st.markdown("""
                <div class="typewriter">
                    <div class="slide"><i></i></div>
                    <div class="paper"></div>
                    <div class="keyboard"></div>
                </div>
            """, unsafe_allow_html=True)

            with st.spinner("Reading and translating PDF..."):
                # Read the PDF
                reader = PdfReader(uploaded_file)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text()

                # Simulate translation (this would be your translation logic)
                translation_prompt = "Please translate the attached pdf file comprehensively into medical Arabic."
                response = get_response_(translation_prompt + " " + pdf_text)
                translated_text = response

                # Generate PDF
                st.session_state.translated_pdf = create_pdf(translated_text)

                st.success("Translation completed!")

            st.markdown("<style>.typewriter { display: none; }</style>", unsafe_allow_html=True)

    # Display PDF download button after translation
    if "translated_pdf" in st.session_state:
        st.sidebar.download_button(
            label="Download Translated Report",
            data=st.session_state.translated_pdf,
            file_name="translated_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    translate()


