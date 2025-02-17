from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Fix API key retrieval
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use the latest supported model
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_response(input_text, image):
    contents = []
    
    if input_text.strip():  
        contents.append(input_text)
    else:
        contents.append("Describe the image.")  

    if image is not None:  
        contents.append(image)

    response = model.generate_content(contents)
    return response.text

st.set_page_config(page_title="With the vision")
st.header("Gemini LLM By Bhuvana of vision")

input_text = st.text_input("Input: ", key="input")
upload_file = st.file_uploader("Choose a file...", type=["jpeg", "png", "jpg"])
image = None

if upload_file is not None:
    image = Image.open(upload_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

submit = st.button("Tell me about the image")

if submit:
    if image is not None:  # Ensure an image is uploaded before calling API
        response = get_gemini_response(input_text, image)
        st.subheader("The response is:")
        st.write(response)
    else:
        st.warning("Please upload an image before submitting.")
