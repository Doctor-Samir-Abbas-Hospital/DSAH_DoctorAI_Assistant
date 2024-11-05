import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI, OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from PyPDF2 import PdfReader
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import simpleSplit
from utils.functions import (
    get_vector_store,
    get_response_,
)

# Load environment variables
load_dotenv()

# Register Arabic font (Arial)
font_path = os.path.join('assets', 'Arial.ttf')
pdfmetrics.registerFont(TTFont('Arial', font_path))

def reshape_arabic_text(text):
    """Reshapes and applies bidi formatting for Arabic text."""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def clean_text(text):
    """Removes unwanted characters and cleans the text."""
    return text.replace('*', '').replace('#', '')

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
    text_width = width - 2 * margin  # Calculate usable text width

    # Prepare text
    reshaped_text = reshape_arabic_text(clean_text(translated_text))
    lines = simpleSplit(reshaped_text, 'Arial', 12, text_width)

    y = height - margin  # Start drawing text just below the margin

    # Set font size
    c.setFont("Arial", 12)

    # Right-align text for RTL Arabic
    for line in lines:
        if y < margin:  # If not enough space, move to the next page
            c.showPage()
            c.setFont("Arial", 12)
            y = height - margin

        c.drawRightString(width - margin, y, line)
        y -= 14  # Move down for the next line

    # Finalize the PDF
    c.save()

    buffer.seek(0)
    return buffer

def translate():
    # Initialize session state variables
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""

    if "chat_history1" not in st.session_state:
        st.session_state.chat_history1 = []  # Initialize chat_history
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    with st.sidebar:
        title = "Doctor AI Assistant"
        name = "Medical Diagnosis and More..."
        profession = "Doctor Samir Abbas Hospital"
        imgUrl = "https://media3.giphy.com/media/6P47BlxlgrJxQ9GR58/giphy.gif"
        
        st.markdown(
            f"""
                <img class="profileImage" src="{imgUrl}" alt="Your Photo">
                <div class="textContainer">
                    <div class="title"><p>{title}</p></div>
                    <p>{name}</p>
                    <p>{profession}</p>
                    <p>Powered by DSAH Information Technology</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        
        uploaded_file = st.file_uploader("Upload a medical report (PDF)", type=["pdf"])

        # Show the translate button only if a file is uploaded
        if uploaded_file:
            translate_button = st.button("Translate The Medical Report")

    pdf_text = ""

    if uploaded_file and translate_button:
        st.markdown("""
            <div class="typewriter">
                <div class="slide"><i></i></div>
                <div class="paper"></div>
                <div class="keyboard"></div>
            </div>
        """, unsafe_allow_html=True)

        # Add spinner below the typewriter
        with st.spinner("Please wait, it's translating the text..."):
            with st.spinner("Reading PDF..."):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    pdf_text += page.extract_text()

            translation_prompt = "Please translate the attached pdf file comprehensively into medical Arabic in a well-structured format."
            response = get_response_(translation_prompt + " " + pdf_text)
            st.session_state.chat_history1.append(AIMessage(content=response))
            st.session_state.translated_text = clean_text(response)

            st.markdown("<style>.typewriter { display: none; }</style>", unsafe_allow_html=True)

    if st.session_state.translated_text:
        # Use Streamlit's text_area for editing
        edited_text = st.text_area(
            "Edit Translated Text",
            value=st.session_state.translated_text,
            height=600,
            key="textarea"
        )

        # Update session state with edited text
        st.session_state.translated_text = edited_text

        # Add FontAwesome icons and JavaScript for copy functionality
        st.components.v1.html(
            """
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <script>
                function copyToClipboard() {
                    var copyText = document.getElementsByName('textarea')[0];
                    copyText.select();
                    document.execCommand('copy');
                    alert('Copied to clipboard!');
                }
            </script>
            <style>
                .icon-button {
                    cursor: pointer;
                    font-size: 1.5em;
                    color: #4CAF50;
                    margin-top: 10px;
                }
                textarea {
                    direction: rtl;
                    text-align: right;
                }
            </style>
            <div class="icon-button" onclick="copyToClipboard()">
                <i class="fas fa-copy"></i> Copy
            </div>
            """,
            height=60,
        )

        # Create a PDF with the edited text
        pdf_buffer = create_pdf(edited_text)

        st.sidebar.download_button(
            label="Download Translated Report",
            data=pdf_buffer,
            file_name="translated_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    translate()