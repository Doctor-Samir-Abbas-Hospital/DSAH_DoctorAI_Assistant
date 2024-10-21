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
from fpdf import FPDF
import base64
from openai import OpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.functions import (
    get_vector_store,
    get_response_,
)

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
    if "chat_history1" not in st.session_state:
        st.session_state.chat_history1 = [
        
        ]
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()

    for message in st.session_state.chat_history1:
        if isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="🤖"):
                st.write(message.content)
                # Add copy icon
                copy_html = f"""
                <div>
                    <i class="fas fa-copy" onclick="copyToClipboard('{message.content}')" style="cursor: pointer;"></i>
                </div>
                <script>
                    function copyToClipboard(text) {{
                        navigator.clipboard.writeText(text).then(() => {{
                            alert('Copied to clipboard!');
                        }});
                    }}
                </script>
                """
                st.components.v1.html(copy_html)
                # Add download as PDF button
                if st.button("Download as PDF", key=f"download_{message.content}"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.multi_cell(0, 10, message.content)
                    pdf_output = f"{message.content[:50]}.pdf"
                    pdf.output(pdf_output)
                    with open(pdf_output, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{pdf_output}">Download PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human", avatar="👨‍⚕️"):
                st.write(message.content)

    pdf_text = ""
    if uploaded_file:
        with st.spinner("Reading PDF..."):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                pdf_text += page.extract_text()
        
        if st.button("Translate The Medical Report"):
            translation_prompt = "Please translate the attached pdf file comprehensively into medical Arabic in a well-structured format."
            # Append translation to chat history
            response = get_response_(translation_prompt + " " + pdf_text)
            st.session_state.chat_history1.append(AIMessage(content=response))
            with st.chat_message("AI", avatar="🤖"):
                st.write(response)

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
