import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.lib.utils import simpleSplit
from utils.functions import get_vector_store, get_response_

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
    """Creates a PDF using hospital template and adds translated text."""
    try:
        template_path = os.path.join('assets', 'hospital_template.pdf')
        if not os.path.exists(template_path):
            raise FileNotFoundError("Hospital template PDF not found")

        # Create a buffer for the translated text
        text_buffer = BytesIO()
        c = canvas.Canvas(text_buffer, pagesize=A4)
        c.setTitle("Translated Medical Report")
        c.setAuthor("Doctor AI Assistant")

        width, height = A4
        margin = inch
        text_width = width - 2 * margin

        # Process the translated text
        reshaped_text = reshape_arabic_text(clean_text(translated_text))
        lines = simpleSplit(reshaped_text, 'Arial', 12, text_width)

        # Starting position for text
        y = height - 2 * margin  # Adjusted to leave space for header

        c.setFont("Arial", 12)

        # Draw text
        for line in lines:
            if y < 1.8 * margin:  # Adjusted to leave space at bottom
                c.showPage()
                c.setFont("Arial", 12)
                y = height - 2 * margin

            c.drawRightString(width - margin, y, line)
            y -= 14

        c.save()
        text_buffer.seek(0)

        # Create final PDF by merging template and text
        output_buffer = BytesIO()
        
        # Load template PDF
        template_pdf = PdfReader(template_path)
        output_pdf = PdfWriter()

        # Load the PDF with translated text
        text_pdf = PdfReader(text_buffer)

        # Merge template with text for each page
        for i in range(max(len(template_pdf.pages), len(text_pdf.pages))):
            # Get template page (use first page if template has only one page)
            template_page = template_pdf.pages[0 if len(template_pdf.pages) == 1 else i % len(template_pdf.pages)]
            
            # Create a new page with the template
            new_page = PdfWriter().add_blank_page(width=template_page.mediabox.width, 
                                                  height=template_page.mediabox.height)
            
            # Merge the template page
            new_page.merge_page(template_page)

            # If there's a corresponding text page, merge it
            if i < len(text_pdf.pages):
                text_page = text_pdf.pages[i]
                new_page.merge_page(text_page)

            output_pdf.add_page(new_page)

        # Write the final PDF to buffer
        output_buffer = BytesIO()
        output_pdf.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer

    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def translate():
    if "translate_state" not in st.session_state:
        st.session_state.translate_state = {}

    if "chat_history1" not in st.session_state:
        st.session_state.chat_history1 = []

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()

    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = ""

    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""

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
    st.session_state.uploaded_file = uploaded_file

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

            with st.spinner("Please wait, it's translating the text..."):
                reader = PdfReader(uploaded_file)
                st.session_state.pdf_text = ""
                for page in reader.pages:
                    st.session_state.pdf_text += page.extract_text()

                translation_prompt = "Please translate the attached pdf file comprehensively into medical Arabic in a well-structured format."
                response = get_response_(translation_prompt + " " + st.session_state.pdf_text)
                st.session_state.chat_history1.append(AIMessage(content=response))
                st.session_state.translated_text = clean_text(response)

            st.markdown("<style>.typewriter { display: none; }</style>", unsafe_allow_html=True)

    if st.session_state.translated_text:
        styled_text = st.session_state.translated_text.replace('\n', '</p><p>')
        st.components.v1.html(
            f"""
            <div style="direction: rtl; text-align: justify; font-family: Arial, sans-serif; box-sizing: border-box; padding: 20px; border: 1px solid #ccc; border-radius: 5px; background-color: white; max-height: 85vh; overflow-y: auto; width: 100%;">
                <p>{styled_text}</p>
                <button onclick="copyToClipboard()" style="margin-top: 10px; padding: 10px 15px;">Copy Translation 📕</button>
            </div>
            <script>
                function copyToClipboard() {{
                    var copyText = document.createElement('textarea');
                    copyText.value = `{st.session_state.translated_text}`;
                    document.body.appendChild(copyText);
                    copyText.select();
                    document.execCommand("copy");
                    document.body.removeChild(copyText);
                    alert("Copied to clipboard!");
                }}
            </script>
            <style>
                p {{
                    font-size: 18px;
                    line-height: 1.6;
                    margin: 0 0 10px 0;
                }}
                button {{
                    cursor: pointer;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }}
            </style>
            """,
            height=800,
            width=650,
        )

        pdf_buffer = create_pdf(st.session_state.translated_text)
        
        if pdf_buffer:
            st.sidebar.download_button(
                label="Download Translated Report",
                data=pdf_buffer,
                file_name="translated_report.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Unable to generate PDF. Please check if the template exists.")

if __name__ == "__main__":
    translate()