import os
import base64
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
import openai
from streamlit_float import *
from templates.watch import clock
import streamlit.components.v1 as components
from streamlit_extras.stylable_container import stylable_container
from utils.functions import (
    speech_to_text,
    get_vector_store,
    get_response,
    text_to_audio,
)



# Initialize OpenAI Client
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

#
# Main app function
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
    user_input = st.chat_input(
        "Type your message here...", key="app_chat_input"
    )  # Unique key

    # JavaScript code for controlling the toggle between mic and send button
    components.html(
        """
        <script>
        const chatInput = document.querySelector('[data-testid="stChatInputTextArea"]');
        const sendButton = document.querySelector('[data-testid="stChatInputSubmitButton"]');
        const micButton = document.createElement('button');
        micButton.classList.add('mic-btn');
        micButton.innerHTML = '<i class="fas fa-microphone"></i>';
        sendButton.parentElement.insertBefore(micButton, sendButton);
        let isRecording = false;
        function toggleButtons() {
            if (chatInput.value.trim().length > 0) {
                micButton.style.display = 'none';
                sendButton.style.display = 'block';
            } else {
                micButton.style.display = 'block';
                sendButton.style.display = 'none';
            }
        }
        chatInput.addEventListener('input', toggleButtons);
        micButton.addEventListener('click', () => {
            if (!isRecording) {
                isRecording = true;
                micButton.innerHTML = '<i class="fas fa-stop"></i>';
                window.parent.postMessage({ type: 'start_recording' }, '*');
            } else {
                isRecording = false;
                micButton.innerHTML = '<i class="fas fa-microphone"></i>';
                window.parent.postMessage({ type: 'stop_recording' }, '*');
            }
        });
        toggleButtons();
        </script>
        """,
        height=0,
    )

    

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

