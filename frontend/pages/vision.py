import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# ✅ Ensure this is the first Streamlit command
st.set_page_config(page_title="AI Chat (Image)", layout="wide")

# ✅ Load environment variables
load_dotenv()

# ✅ Redirect if user is not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("You must log in to access this page.")
    st.switch_page("app.py")  # ✅ Redirect to login page

st.title("AI-Powered Image==>Text")

# ✅ Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Missing API Key! Please set `GOOGLE_API_KEY` in your environment variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_response(input_text, image=None):
    
    contents = [input_text.strip() or "Describe the image."]
    if image:
        contents.append(image)

    try:
        # 🔹 Streaming response
        response = model.generate_content(contents, stream=True)
        full_response = ""
        for chunk in response:
            if chunk.text:
                full_response += chunk.text + " "
                yield chunk.text  # Streaming output
        yield full_response.strip()  # Final output
    except Exception as e:
        yield f"Error generating response: {e}"

# 🔹 Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 🔹 7:3 Layout for Text Input & Image Upload
# st.header("Gemini LLM - Vision Chat")
col1, col2 = st.columns([6, 4])  # 🔹 70% text input, 30% image upload

with col1:
    input_text = st.text_area("Enter your question:", height=70)  # 🔹 Large text input box

with col2:
    upload_file = st.file_uploader("Upload an image (optional)...", type=["jpeg", "png", "jpg"])
    image = None

    if upload_file:
        image = Image.open(upload_file)
        st.session_state["uploaded_image"] = image  # Store image in session state
        st.success("✅ Image uploaded successfully!")

if st.button("Generate Response"):
    if input_text.strip() or "uploaded_image" in st.session_state:
        # Get streamed response
        response_generator = get_gemini_response(input_text, st.session_state.get("uploaded_image"))
        
        # Store question in history
        st.session_state["chat_history"].append({"user": input_text, "ai": ""})

        # 🔹 Display AI's response in streaming mode
        st.subheader("AI Response:")
        response_placeholder = st.empty()  # Placeholder for live streaming response

        full_response = ""
        for chunk in response_generator:
            full_response += chunk
            response_placeholder.write(full_response)  # Update live response
        
        # Store final AI response in history
        st.session_state["chat_history"][-1]["ai"] = full_response
    else:
        st.warning("Please enter a question or upload an image before submitting.")
