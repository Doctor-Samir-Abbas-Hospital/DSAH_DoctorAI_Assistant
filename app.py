import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
import openai
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
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
            """
            <head>
              <link rel="preconnect" href="https://fonts.googleapis.com">
              <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
              <link href="https://fonts.googleapis.com/css2?family=Bungee+Spice&display=swap" rel="stylesheet">
          <style>
                 html {
                        overflow-x: hidden;
                    }

                    body {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        font-family: "Bungee Spice", sans-serif;
                        overflow-x: hidden;
                        min-height: 480px;
                    }

                    .container {
                        position: relative;
                        min-height: 250px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }

                    .bubble-wrap {
                        width: 200px;
                        height: 200px;
                        border-radius: 50%;
                        position: relative;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        overflow: hidden;
                        background: #e0e5ec;
                        box-shadow: 3px 3px 8px #ffffff, -3px -3px 8px #babecc;
                    }

                    .bubbles-bg {
                        position: relative;
                        height: 100%;
                        display: flex;
                        gap: 22px;
                        justify-content: center;
                        width: 100%;
                    }

                    .bubbles-bg span {
                        display: inline-block;
                        position: relative;
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        animation: animate 5s linear infinite;
                        animation-duration: calc(150s / var(--i));
                    }

                    @keyframes animate {
                        0% {
                            transform: translateY(350px) scale(0);
                            background-color: #df6208;
                            box-shadow: 0px 0px 4px 4px #e67d31, 0 0 30px #e67d31, 0 0 70px #e67d31;
                        }
                        50% {
                            background: #d3df08;
                            box-shadow: 0px 0px 4px 4px #e4ec53, 0 0 30px #e4ec53, 0 0 70px #e4ec53;
                        }
                        70% {
                            background: #df0808;
                            box-shadow: 0px 0px 4px 4px #ec4242, 0 0 30px #ec4242, 0 0 70px #ec4242;
                        }
                        100% {
                            transform: translateY(-10px) scale(1);
                            background-color: #df6208;
                            box-shadow: 0px 0px 4px 4px #e67d31, 0 0 30px #e67d31, 0 0 70px #e67d31;
                        }
                    }

                    .clock {
                        width: 250px;
                        height: 250px;
                        border-radius: 50%;
                        position: relative;
                        box-shadow: inset 3px 3px 8px #ffffff, inset -3px -3px 8px #babecc;
                        background: #e0e5ec;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin-bottom: 110px;
                    }

                    .clock::before {
                        content: "";
                        width: 10px;
                        height: 10px;
                        border-radius: 50%;
                        border: 2px solid #e0e5ec;
                        background-color: #2f362f;
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        z-index: 1;
                    }

                    .inner-circle {
                        width: 150px;
                        height: 280px;
                        border-radius: 50%;
                        position: absolute;
                        display: flex;
                        justify-content: center;
                        align-items: start;
                    }

                    .inner-circle-2 {
                        width: 150px;
                        height: 250px;
                    }

                    .inner-circle-3 {
                        width: 100px;
                        height: 200px;
                    }

                    .border-circle {
                        border-radius: 50%;
                        position: absolute;
                        background: transparent;
                        border: 2px solid rgba(223, 98, 8, 0.2);
                        left: 50%;
                        top: 50%;
                        width: 180px;
                        height: 180px;
                        transform: translate(-50%, -50%);
                    }

                    .border-circle:nth-child(2) {
                        width: 130px;
                        height: 130px;
                    }

                    .border-circle:nth-child(3) {
                        width: 80px;
                        height: 80px;
                    }

                    .inner-circle div {
                        position: relative;
                        height: 50%;
                        width: 7px;
                        z-index: 1;
                        border-radius: 5px;
                        display: inline-block;
                        transform-origin: bottom;
                        transform: scale(0.5);
                        z-index: 0;
                        background: rgb(223, 98, 8);
                        background: linear-gradient(
                            180deg,
                            rgba(223, 98, 8, 0.9108018207282913) 50%,
                            rgba(255, 0, 0, 0.9304096638655462) 100%
                        );
                    }

                    .inner-circle-2 div {
                        width: 4px;
                    }

                    .inner-circle-3 div {
                        width: 3px;
                    }

                    span {
                        position: absolute;
                        text-align: center;
                        transform: rotate(calc(var(--i) * 29.7deg));
                        inset: 25px;
                    }

                    span b {
                        font-size: 18px;
                        position: absolute;
                        text-align: center;
                        transform: rotateZ(calc(var(--i) * -30deg));
                        display: inline-block;
                        opacity: 0.9;
                    }

                    /* digital clock */
                    .digital-time-wrap {
                        width: 4px;
                        height: 80%;
                        background-color: #ffffff;
                        position: absolute;
                        left: 48.5%;
                        top: 50%;
                        transform: translate(-50%, -50%);
                        z-index: -1;
                        animation-name: rotate;
                        animation-duration: 2s;
                        animation-iteration-count: infinite;
                        transform-origin: 50% 0%;
                        animation-timing-function: linear;
                    }

                    @keyframes rotate {
                        0% {
                            transform: rotate(-6deg);
                            animation-timing-function: ease-in;
                        }
                        25% {
                            transform: rotate(0deg);
                            animation-timing-function: ease-out;
                        }
                        50% {
                            transform: rotate(6deg);
                            animation-timing-function: ease-in;
                        }
                        75% {
                            transform: rotate(0deg);
                            animation-timing-function: ease-out;
                        }
                        100% {
                            transform: rotate(-6deg);
                        }
                    }

                    #digital-time {
                        width: fit-content;
                        display: flex;
                        padding: 10px;
                        border: 2px solid #ffffff;
                        border-radius: 20px;
                        background: #ffffff;
                        position: absolute;
                        left: 50%;
                        transform: translateX(-50%);
                        bottom: 0;
                    }

                    #digital-time div {
                        font-size: 16px;
                        width: 50px;
                        text-align: center;
                        position: relative;
                    }

                    #digital-time div:nth-child(1)::after,
                    #digital-time div:nth-child(2)::after {
                        content: ":";
                        position: absolute;
                        right: -4px;
                        opacity: 0.7;
                    }

                    #digital-time div:nth-child(4) {
                        font-size: 18px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                </style>
            </head>
            <body>
              <div class="container">
                <div class="clock">
                  <div class="bubble-wrap">
                    <div class="bubbles-bg">
                      <span style="--i:15;"></span>
                      <span style="--i:12;"></span>
                      <span style="--i:18;"></span>
                      <span style="--i:22;"></span>
                      <span style="--i:20;"></span>
                      <span style="--i:23;"></span>
                      <span style="--i:13;"></span>
                      <span style="--i:18;"></span>
                      <span style="--i:28;"></span>
                      <span style="--i:24;"></span>
                      <span style="--i:15;"></span>
                      <span style="--i:21;"></span>
                    </div>
                  </div>
                  <div class="border-circle"></div>
                  <div class="border-circle"></div>
                  <div class="border-circle"></div>

                  <div class="inner-circle inner-circle-1" id="sec">
                    <div></div>
                  </div>
                  <div class="inner-circle inner-circle-2" id="min">
                    <div></div>
                  </div>
                  <div class="inner-circle inner-circle-3" id="hrs">
                    <div></div>
                  </div>

                  <span style="--i:1;"><b>1</b></span>
                  <span style="--i:2;"><b>2</b></span>
                  <span style="--i:3;"><b>3</b></span>
                  <span style="--i:4;"><b>4</b></span>
                  <span style="--i:5;"><b>5</b></span>
                  <span style="--i:6;"><b>6</b></span>
                  <span style="--i:7;"><b>7</b></span>
                  <span style="--i:8;"><b>8</b></span>
                  <span style="--i:9;"><b>9</b></span>
                  <span style="--i:10;"><b>10</b></span>
                  <span style="--i:11;"><b>11</b></span>
                  <span style="--i:12;"><b>12</b></span>

                  <div class="digital-time-wrap">
                    <div id="digital-time">
                      <div id="hours">00</div>
                      <div id="minuts">00</div>
                      <div id="seconds">00</div>
                      <div id="ampm">PM</div>
                    </div>
                  </div>
                </div>
              </div>
              <script>
                let hrs = document.querySelector("#hrs");
                let sec = document.querySelector("#sec");
                let min = document.querySelector("#min");

                setInterval(() => {
                  let day = new Date();
                  let hh = day.getHours() * 30;
                  let mm = day.getMinutes() * 6;
                  let ss = day.getSeconds() * 6;

                  hrs.style.transform = `rotateZ(${hh + mm / 12}deg)`;
                  min.style.transform = `rotateZ(${mm}deg)`;
                  sec.style.transform = `rotateZ(${ss}deg)`;
                });

                function updateClock() {
                  const now = new Date();

                  const hours = now.getHours();
                  const minutes = now.getMinutes();
                  const seconds = now.getSeconds();
                  const ampm = hours >= 12 ? "PM" : "AM";

                  document.getElementById("hours").textContent = formatTime(hours % 12 || 12);
                  document.getElementById("minuts").textContent = formatTime(minutes);
                  document.getElementById("seconds").textContent = formatTime(seconds);
                  document.getElementById("ampm").textContent = ampm;
                }

                function formatTime(time) {
                  return time < 10 ? "0" + time : time;
                }

                setInterval(updateClock, 1000);
                updateClock();
              </script>
            </body>
            """,
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
    # Create a chat input field
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