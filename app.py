# from dotenv import load_dotenv
# import streamlit as st
# import os
# import time
# import google.generativeai as genai

# # Load environment variables
# load_dotenv()

# # Configure Gemini API
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# # Initialize the model
# model = genai.GenerativeModel("gemini-1.5-pro")

# # Function to get response from Gemini API with conversation history
# def get_gemini_response(question):
#     # Limit to last 10 messages for context (to avoid exceeding token limit)
#     conversation_history = st.session_state["conversation_history"][-10:]

#     # Format conversation history as a single prompt
#     context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
#     # Append the latest user question
#     full_prompt = f"{context}\nUser: {question}\nAssistant:"

#     # Introduce a delay to avoid hitting API limits
#     time.sleep(1)  # Reduce rapid API calls

#     try:
#         response = model.generate_content(full_prompt)
#         assistant_reply = response.text

#         # Store user input and AI response in session history
#         st.session_state["conversation_history"].append({"role": "User", "content": question})
#         st.session_state["conversation_history"].append({"role": "Assistant", "content": assistant_reply})

#         return assistant_reply

#     except Exception as e:
#         return f"⚠️ API Error: {str(e)}"

# # Streamlit UI
# st.set_page_config(page_title="Chat with Gemini", layout="wide")
# st.header("🤖 Gemini LLM - Chat Mode")

# # Initialize session state for conversation history
# if "conversation_history" not in st.session_state:
#     st.session_state["conversation_history"] = []

# # Display chat history
# for message in st.session_state["conversation_history"]:
#     with st.chat_message(message["role"].lower()):  # "user" or "assistant"
#         st.write(message["content"])

# # User input field
# input_text = st.chat_input("Type your message here...")

# if input_text:
#     # Display user message instantly
#     with st.chat_message("user"):
#         st.write(input_text)

#     # Check if response is cached to reduce API calls
#     if input_text in st.session_state:
#         response = st.session_state[input_text]
#     else:
#         response = get_gemini_response(input_text)
#         st.session_state[input_text] = response  # Cache the response

#     # Display AI response
#     with st.chat_message("assistant"):
#         st.write(response)







from dotenv import load_dotenv
import streamlit as st
import os
import speech_recognition as sr
import PyPDF2
from groq import Groq

# Load environment variables
load_dotenv()

# Configure Groq API
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Function to transcribe voice input
def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Speech Recognition service error"

# Function to extract text from uploaded PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# Function to get response from Groq API with conversation history & PDF content
def get_groq_response():
    if not st.session_state["current_input"].strip():
        return "No valid input provided."

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state["conversation_history"]]

    if "pdf_content" in st.session_state and st.session_state["pdf_content"]:
        messages.append({"role": "system", "content": f"Reference Document: {st.session_state['pdf_content']}"})

    messages.append({"role": "user", "content": st.session_state["current_input"]})

    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="Chat with Groq AI", layout="wide")
st.header("🤖 Groq AI Chat - Conversational Memory & PDF Support")

# Inject **CSS to make footer static**
st.markdown("""
    <style>
        /* Fix the footer at bottom */
        .fixed-footer {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: white;
            padding: 10px 20px;
            box-shadow: 0px -2px 10px rgba(0, 0, 0, 0.1);
            z-index: 999;
        }
        /* Align elements in footer */
        .footer-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .chat-input {
            flex-grow: 1;
            margin-right: 20px;
        }
        .icon-buttons {
            display: flex;
            gap: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

# Display chat history
for message in st.session_state["conversation_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ✅ **Fixed Footer Section (Static at Bottom)**
st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([7, 1, 3])

with col1:
    input_text = st.chat_input("Type your message here...")  # Centered

with col2:
    if st.button("🎤", key="mic_button", help="Click to Speak"):
        voice_text = record_and_transcribe()
        if voice_text and voice_text not in ["Could not understand audio", "Speech Recognition service error"]:
            input_text = voice_text  

with col3:
    uploaded_file = st.file_uploader("📂", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        st.session_state["uploaded_file"] = uploaded_file
        st.session_state["pdf_content"] = extract_text_from_pdf(uploaded_file)
        st.success("✅ PDF uploaded successfully!")

st.markdown('</div>', unsafe_allow_html=True)

# Process input
if input_text:
    st.session_state["current_input"] = input_text
    response = get_groq_response()

    st.session_state["conversation_history"].append({"role": "user", "content": input_text})
    with st.chat_message("user"):
        st.write(input_text)

    st.session_state["conversation_history"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
