import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.vectorstores.qdrant import Qdrant
import qdrant_client
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from PyPDF2 import PdfReader
import base64
from openai import OpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from fpdf import FPDF
from io import BytesIO
from utils.functions import (
    get_vector_store,
    get_response_,
)

# Load environment variables
load_dotenv()

client = OpenAI()

def create_pdf(content):
    pdf_buffer = BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, content)

    pdf.output(pdf_buffer, 'F')
    pdf_buffer.seek(0)
    return pdf_buffer

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
    if uploaded_file:
        with st.spinner("Reading PDF..."):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                pdf_text += page.extract_text() or ""

        if st.button("Translate The Medical Report"):
            translation_prompt = "Please translate the attached pdf file comprehensively into medical Arabic in a well-structured format."
            with st.chat_message("AI", avatar="🤖"):
                response = get_response_(translation_prompt + " " + pdf_text)
                st.write(response)
                st.session_state.chat_history1.append(AIMessage(content=response))

                # Debug: Check if response is not empty
                if response:
                    st.session_state.last_translation = response  # Store the translation for PDF download

                    # Create a PDF for download
                    pdf_buffer = create_pdf(response)
                    b64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="translation.pdf">Click here to download the translation</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error("Translation failed. Please try again.")

    user_query = st.chat_input("Type your message here...", key="translate_chat_input")
    if user_query and user_query.strip():
        st.session_state.chat_history1.append(HumanMessage(content=user_query))

        with st.chat_message("Human", avatar="👨‍⚕️"):
            st.markdown(user_query)

        with st.chat_message("AI", avatar="🤖"):
            response = get_response_(user_query)
            st.write(response)
            st.session_state.chat_history1.append(AIMessage(content=response))

if __name__ == "__main__":
    translate()

