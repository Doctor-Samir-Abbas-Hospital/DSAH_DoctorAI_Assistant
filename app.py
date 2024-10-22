import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
import openai
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from templates.watch import clock
from streamlit_extras.stylable_container import stylable_container
from utils.functions import (
    get_vector_store,
    get_context_retriever_chain,
    get_conversational_rag_chain,
    get_response,
    text_to_audio,
    autoplay_audio,
    speech_to_text,
)

# load the variables
load_dotenv()
client = openai

# app layout
def app():
    # Read CSS file
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        title = "Doctor AI Assistant "
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
        
        # Embed the clock here
        st.components.v1.html(
            clock,
            height=400,
            width=300,
        )

    # Float feature initialization
    float_init()

    # Create footer container for the microphone
    footer_container = stylable_container(
        key="Mic_container",
        css_styles=[
            """
            position: absolute;
            bottom: 10px;
            right: 25px;
            background-color: #007bff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: inline-block;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            """
        ],
    )
    user_query = None
    user_input = st.chat_input("Type your message here...", key="app_chat_input")  # Unique key
    with footer_container:
        transcript = None
        audio_bytes = audio_recorder(text=None, icon_size="15X", key="recorder")
        if audio_bytes:
            # Write the audio bytes to a file
            with st.spinner("Transcribing..."):
                webm_file_path = "temp_audio.mp3"
                with open(webm_file_path, "wb") as f:
                    f.write(audio_bytes)
                transcript = speech_to_text(webm_file_path)
                os.remove(webm_file_path)
                user_query = transcript

    if user_input is not None and user_input != "":
        user_query = user_input
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(
                content=" Hello ! I'm  Doctor AI Assistant at Doctor Samir Abbas Hospital , How can I assist you today with your medical inquiries? 🥰"
            )
        ]
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="🤖"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human", avatar="👩‍⚕️"):
                st.write(message.content)

    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("Human", avatar="👩‍⚕️"):
            st.markdown(user_query)
        with st.chat_message("AI", avatar="🤖"):
            response = st.write_stream(get_response(user_query))
            response_audio_file = "audio_response.mp3"
            text_to_audio(client, response, response_audio_file)
            st.audio(response_audio_file)
            st.session_state.chat_history.append(AIMessage(content=response))

    footer_container.float(
        "bottom: 1.5rem; height:30px; width:30px; display:inline-block; align-items:center;justify-content:center; overflow:hidden visible;align-self:self-end;flex-direction: row-reverse;"
    )


if __name__ == "__main__":
    app()