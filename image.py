import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.vectorstores.qdrant import Qdrant
import qdrant_client
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
import tiktoken
import base64
from templates.prompt import engineeredprompt
from openai import OpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from PIL import Image
import io

# Load environment variables
load_dotenv()
collection_name = os.getenv("QDRANT_COLLECTION_NAME")

# Initialize OpenAI Client
client = OpenAI()

# Vector store setup
def get_vector_store():
    client = qdrant_client.QdrantClient(
        url=os.getenv("QDRANT_HOST"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    embeddings = OpenAIEmbeddings()
    vector_store = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings,
    )
    return vector_store

vector_store = get_vector_store()

# Context retriever chain setup
def get_context_retriever_chain(vector_store=vector_store):
    llm = ChatOpenAI()
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation",
            ),
        ]
    )
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    return retriever_chain

# Conversational RAG chain setup
def get_conversational_rag_chain(retriever_chain):
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                engineeredprompt
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

# Response generator
def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    response_stream = conversation_rag_chain.stream(
        {"chat_history": st.session_state.chat_history, "input": user_input}
    )
    for chunk in response_stream:
        content = chunk.get("answer", "")
        yield content

# Text-to-audio conversion
def text_to_audio(client, text, audio_path):
    response = client.audio.speech.create(model="tts-1", voice="fable", input=text)
    response.stream_to_file(audio_path)

# Audio autoplay
def autoplay_audio(audio_file):
    with open(audio_file, "rb") as audio_file:
        audio_bytes = audio_file.read()
    base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

# Image analysis with GPT-4V(ision)
def analyze_image(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    response = client.image.create(
        file=img_byte_arr,
        model="gpt-4-vision",
        prompt="Analyze this medical image."
    )
    return response['data']

# Main app function
def image():
    # App layout and initialization
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Sidebar content
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

    # Chat initialization
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello! Doctor Assistant AI chatbot at your service for medical inquiries. How can I help? 🥰")
        ]
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()

    # Display chat history
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="🤖"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human", avatar="👨‍⚕️"):
                st.write(message.content)

    # User input handling
    user_query = st.chat_input("Type your message here...")

    # Image upload feature
    uploaded_file = st.sidebar.file_uploader("Upload a medical image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Analyze the image and display the results
        analysis_result = analyze_image(image)
        st.session_state.chat_history.append(AIMessage(content=analysis_result))
        
        with st.chat_message("AI", avatar="🤖"):
            st.write(analysis_result)

    # Text query handling
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("Human", avatar="👨‍⚕️"):
            st.markdown(user_query)
        
        with st.chat_message("AI", avatar="🤖"):
            response = st.write_stream(get_response(user_query))
            response_audio_file = "audio_response.mp3"
            text_to_audio(client, response, response_audio_file)
            autoplay_audio(response_audio_file)
            st.session_state.chat_history.append(AIMessage(content=response))

# Run the app
if __name__ == "__main__":
    image()

