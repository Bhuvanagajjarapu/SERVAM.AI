import streamlit as st
import os
from dotenv import load_dotenv
import speech_recognition as sr
import PyPDF2
from groq import Groq
import google.generativeai as genai

# ✅ Ensure this is the first Streamlit command
st.set_page_config(page_title="AI Chat (Text & PDF)", layout="wide")

# ✅ Load environment variables
load_dotenv()

# ✅ Redirect if user is not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("You must log in to access this page.")
    st.switch_page("app.py")  # ✅ Redirect to login page

st.title("🤖 AI Chat - Groq & Gemini")
st.write("Welcome to the AI-powered chat for text and PDFs.")

# ✅ Configure APIs
groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not groq_api_key:
    st.error("Missing `GROQ_API_KEY`! Set it in your environment variables.")
    st.stop()
if not google_api_key:
    st.error("Missing `GOOGLE_API_KEY`! Set it in your environment variables.")
    st.stop()

groq_client = Groq(api_key=groq_api_key)
genai.configure(api_key=google_api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Initialize session state variables
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []
if "pdf_content" not in st.session_state:
    st.session_state["pdf_content"] = ""
if "current_input" not in st.session_state:
    st.session_state["current_input"] = ""

# ✅ Function: Transcribe voice input
def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Speech Recognition service error"

# ✅ Function: Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text()).strip()
    return extracted_text or "No extractable text found."

# ✅ Function: Get response from Groq API
def get_groq_response():
    if not st.session_state["current_input"].strip():
        return "No valid input provided."

    messages = st.session_state["conversation_history"][:]
    if st.session_state["pdf_content"]:
        messages.append({"role": "system", "content": f"Reference Document: {st.session_state['pdf_content']}"})

    messages.append({"role": "user", "content": st.session_state["current_input"]})

    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            stream=True
        )

        response_text = ""
        with st.chat_message("assistant"):
            response_area = st.empty()
            for chunk in response:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content
                    response_area.markdown(response_text)

        return response_text
    except Exception as e:
        return f"Error: {str(e)}"

# ✅ UI Section
st.header("💬 AI Chat - Groq for Text & PDF")

# 🔹 Display chat history
for message in st.session_state["conversation_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 🔹 Input & Upload Section
col1, col2, col3 = st.columns([6, 1, 3])

with col1:
    input_text = st.chat_input("Type your message here...")  

with col2:
    if st.button("🎤", key="mic_button", help="Click to Speak"):
        voice_text = record_and_transcribe()
        if voice_text not in ["Could not understand audio", "Speech Recognition service error"]:
            input_text = voice_text  

with col3:
    uploaded_file = st.file_uploader("📂 Upload PDF", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        st.session_state["pdf_content"] = extract_text_from_pdf(uploaded_file)
        st.success("✅ PDF uploaded successfully!")

# 🔹 Process Input
if input_text:
    st.session_state["current_input"] = input_text
    st.session_state["conversation_history"].append({"role": "user", "content": input_text})
    
    with st.chat_message("user"):
        st.write(input_text)
    
    response = get_groq_response()
    st.session_state["conversation_history"].append({"role": "assistant", "content": response})
