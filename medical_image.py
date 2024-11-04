import os
import streamlit as st
import requests
from PIL import Image
import io

# Set up the Gork API endpoint and key
GORK_API_URL = "https://api.x.ai/v1/analyze"
XAI_API_KEY = os.getenv("XAI_API_KEY")

def analyze_image(image_data, prompt):
    headers = {
        'Authorization': f'Bearer {XAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    files = {
        'image': image_data
    }
    data = {
        'prompt': prompt
    }
    response = requests.post(GORK_API_URL, headers=headers, files=files, data=data)
    return response.json()

def main():
    st.title("Medical Image Analysis Bot")

    uploaded_image = st.file_uploader("Upload a medical image", type=['jpg', 'jpeg', 'png'])
    prompt = st.text_input("Enter your prompt")

    if uploaded_image and prompt:
        image = Image.open(uploaded_image)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Convert the image to bytes
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()

        if st.button("Analyze"):
            with st.spinner("Analyzing..."):
                analysis_result = analyze_image(image_bytes, prompt)
                st.write("Analysis Result:")
                st.json(analysis_result)

if __name__ == "__main__":
    main()