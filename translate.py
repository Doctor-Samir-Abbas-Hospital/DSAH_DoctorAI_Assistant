import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.vectorstores.qdrant import Qdrant
import qdrant_client
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAI, OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from PyPDF2 import PdfReader
from io import BytesIO
import arabic_reshaper  # To reshape Arabic text
from bidi.algorithm import get_display  # To handle bidirectional text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from utils.functions import (
    get_vector_store,
    get_response_,
)

# Load environment variables
load_dotenv()

# Register Arabic font (Arial)
font_path = os.path.join('assets', 'Arial.ttf')
pdfmetrics.registerFont(TTFont('Arial', font_path))
addMapping('Arial', 0, 0, 'Arial')

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
    text_width = width - 2 * margin
    text_height = height - 2 * margin

    # Prepare text
    reshaped_text = reshape_arabic_text(clean_text(translated_text))
    lines = reshaped_text.split('\n')  # Split by lines to handle text

    y = height - margin  # Start drawing text just below the margin

    # Set up text object
    textobject = c.beginText()
    textobject.setFont("Arial", 12)
    textobject.setTextOrigin(width - margin, y)  # Right-align starting point
    textobject.setWordSpace(-2)  # Adjust word spacing for justification
    
    # Add the title
    c.setFont('Arial', 18)
    title_text = "تقرير طبي شامل"
    bidi_title = reshape_arabic_text(title_text)
    c.drawRightString(width - inch, y - inch, bidi_title)

    # Draw a horizontal line
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.black)
    c.line(margin, y - 1.5 * inch, width - margin, y - 1.5 * inch)
    
    y -= 2 * inch

    # Draw text lines and handle pagination
    for line in lines:
        if y < margin:  # Check if space is available, otherwise start a new page
            c.drawText(textobject)  # Draw the text for the current page
            c.showPage()
            textobject = c.beginText()
            textobject.setFont("Arial", 12)
            textobject.setTextOrigin(width - margin, height - margin)
            y = height - margin

        # Right-align text for RTL Arabic
        textobject.setTextOrigin(width - margin, y)
        textobject.textLine(line)
        y -= 14  # Move down for the next line

    # Finalize the text object and save the PDF
    c.drawText(textobject)
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

    for message in st.session_state.chat_history1:
        if isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="🤖"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human", avatar="👨‍⚕️"):
                st.write(message.content)

    pdf_text = ""
    translated_text = ""

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
            with st.chat_message("AI", avatar="🤖"):
                response = get_response_(translation_prompt + " " + pdf_text)
                st.write(response)
                st.session_state.chat_history1.append(AIMessage(content=response))
                translated_text = response

            st.markdown("<style>.typewriter { display: none; }</style>", unsafe_allow_html=True)

    if translated_text:
        pdf_buffer = create_pdf(translated_text)

        st.sidebar.download_button(
            label="Download Translated Report",
            data=pdf_buffer,
            file_name="translated_report.pdf",
            mime="application/pdf"
        )

        st.markdown("""
            <div style="display: flex; justify-content: flex-end; margin-top: 10px;">
                <i class="fas fa-copy" style="font-size: 24px; cursor: pointer;" onclick="copyToClipboard()"></i>
            </div>
            <script src="https://kit.fontawesome.com/a076d05399.js"></script>
            <script>
                function copyToClipboard() {
                    const el = document.createElement('textarea');
                    el.value = `""" + translated_text.replace('\n', '\\n') + """`;
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert('Text copied to clipboard');
                }
            </script>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    translate()
