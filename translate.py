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
from fpdf import FPDF
from utils.functions import (
    get_vector_store,
    get_response_,
)
from io import BytesIO

# Load environment variables
load_dotenv()

client = OpenAI()

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass

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
    translated_text = ""

    if uploaded_file:
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
                translated_text = response

            st.markdown("<style>.typewriter { display: none; }</style>", unsafe_allow_html=True)

    if translated_text:
        pdf = PDF()
        pdf.add_page()
        font_path = os.path.join('assets', 'DejaVuSans.ttf')
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
        pdf.multi_cell(0, 10, translated_text)

        pdf_output = BytesIO()
        pdf.output(pdf_output, dest='F')
        pdf_content = pdf_output.getvalue()

        st.sidebar.download_button(
            label="Download Translated Report",
            data=pdf_content,
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