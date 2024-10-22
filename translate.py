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
from fpdf import FPDF  # Ensure you have fpdf installed
from utils.functions import (
    get_vector_store,
    get_response_,
)
from io import BytesIO  # For handling PDF output in memory

# Load environment variables
load_dotenv()

client = OpenAI()

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
        # Create a PDF from the translated text
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
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

    else:
        # If there is no translated text, disable the download button
        st.sidebar.button("Download Translated Report", disabled=True)

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



