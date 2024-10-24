import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAI, OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from PyPDF2 import PdfReader
from fpdf import FPDF
from utils.functions import get_vector_store, get_response_
from io import BytesIO

# Load environment variables
load_dotenv()

client = OpenAI()

# Custom FPDF class to support Unicode (UTF-8)
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Translated Medical Report', 0, 1, 'C')

# Function to add copy-paste functionality
copy_js = """
    function copyToClipboard(text) {
        var tempInput = document.createElement("textarea");
        tempInput.style.position = "absolute";
        tempInput.style.left = "-9999px";
        tempInput.value = text;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand("copy");
        document.body.removeChild(tempInput);
        alert("Copied to clipboard!");
    }
"""

def translate():
    if "translate_state" not in st.session_state:
        st.session_state.translate_state = {}
    
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
        translate_button = st.button("Translate The Medical Report")

    if "chat_history1" not in st.session_state:
        st.session_state.chat_history1 = []

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()

    for message in st.session_state.chat_history1:
        if isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="🤖"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human", avatar="👨‍⚕️"):
                st.write(message.content)

    pdf_text = ""
    translated_text = ""  # To store the translation

    if uploaded_file:
        # Show the typewriter loader when translating
        if translate_button:
            st.markdown("""
                <div class="typewriter">
                    <div class="slide"><i></i></div>
                    <div class="paper"></div>
                    <div class="keyboard"></div>
                </div>
            """, unsafe_allow_html=True)

            with st.spinner("Reading PDF..."):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    pdf_text += page.extract_text()

            translation_prompt = "Please translate the attached pdf file comprehensively into medical Arabic in a well-structured format."
            with st.chat_message("AI", avatar="🤖"):
                response = get_response_(translation_prompt + " " + pdf_text)
                st.write(response)
                st.session_state.chat_history1.append(AIMessage(content=response))
                translated_text = response  # Save the translation

            # Hide the typewriter loader after translation
            st.markdown("<style>.typewriter { display: none; }</style>", unsafe_allow_html=True)

    # Always show download button, active if translated text is available
    if translated_text:
        # Create a PDF from the translated text using UTF-8 compatible font
        pdf = PDF()
        pdf.add_page()

        # Add a font that supports Arabic (or non-Latin) characters
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)

        # Use the translated text
        pdf.multi_cell(0, 10, translated_text)

        # Save the PDF to a BytesIO object
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)  # Move to the beginning of the BytesIO object

        # Display the download button in the sidebar
        st.sidebar.download_button(
            label="Download Translated Report",
            data=pdf_output,
            file_name="translated_report.pdf",
            mime="application/pdf"
        )

        # Add copy-paste functionality using JavaScript and Font Awesome icon
        st.markdown(f"""
            <div style="margin-top: 10px;">
                <button onclick="copyToClipboard('{translated_text}')">
                    <i class="fa fa-copy"></i> Copy to Clipboard
                </button>
            </div>
        """, unsafe_allow_html=True)

        # Inject the copy-to-clipboard JavaScript
        st.markdown(f"<script>{copy_js}</script>", unsafe_allow_html=True)

    # Check if the file is uploaded and translation has happened
    elif uploaded_file and not translated_text:
        st.sidebar.button("Download Translated Report")


if __name__ == "__main__":
    translate()

