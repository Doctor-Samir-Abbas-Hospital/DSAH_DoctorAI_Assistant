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
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
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

        # Use st.components.v1.html for copy functionality with Font Awesome
        st.components.v1.html(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" integrity="sha384-k6RqeWeci5ZR/Lv4MR0sA0FfDOMTnlA4E6Zr9/6b0GqAdVIl0QvZb0e6a3ANV3L5" crossorigin="anonymous">
            
            <div>
                <i class="fas fa-copy copy-icon" role="button" style="font-size: 22px; cursor: pointer;"></i>
                <span class="toastbox" role="alert"></span>
            </div>

            <div id="translated-text" style="display:none;">
                {translated_text}
            </div>

            <style>
            .toastbox {{
              width: 280px;
              padding: 10px;
              background-color: rgba(0,0,0,.7);
              color: white;
              text-align: center;
              border-radius: 4px;
              position: fixed;
              top: 105%;
              transition: transform .3s linear;
            }}

            .toastbox.toast-tox--active {{
              transform: translateY(-150px); 
            }}
            </style>

            <script>
            var copyToClipboard = (function () {{ 
              var copyIcon = document.querySelector(".copy-icon");
              var toastBox = document.querySelector(".toastbox");
              var translatedText = document.getElementById("translated-text").textContent;

              function isCopying(string) {{ 
                var textarea, result;
                try {{
                  textarea = document.createElement('textarea');
                  textarea.setAttribute('readonly', true);
                  textarea.setAttribute('contenteditable', true);
                  textarea.style.position = 'fixed'; 
                  textarea.value = string;

                  document.body.appendChild(textarea);

                  textarea.select();

                  var range = document.createRange();
                  range.selectNodeContents(textarea);

                  var selectedText = window.getSelection();
                  selectedText.removeAllRanges();
                  selectedText.addRange(range);

                  textarea.setSelectionRange(0, textarea.value.length);
                  result = document.execCommand('copy');
                }} catch (err) {{
                  console.error(err);
                  result = null;
                }} finally {{
                  document.body.removeChild(textarea);
                }}
                if (!result) {{
                  result = prompt("Copy the text", string); 
                  if (!result) {{
                    return false;
                  }}
                }}
                return true;
              }}

              function showToastBox(message) {{
                toastBox.textContent = message;
                setTimeout(function () {{
                  toastBox.classList.add("toast-tox--active");
                }}, 500);
                setTimeout(function () {{
                  toastBox.classList.remove("toast-tox--active");
                }}, 3000);
              }}

              function handleCopyIconClick() {{
                copyIcon.addEventListener("click", function(){{
                  showToastBox(isCopying(translatedText) ? "Text copied successfully" : "Unable to copy");
                }});
              }}

              return {{handleCopyIconClick: handleCopyIconClick}};
            }})();

            copyToClipboard.handleCopyIconClick();
            </script>
        """, height=300)

if __name__ == "__main__":
    translate()
