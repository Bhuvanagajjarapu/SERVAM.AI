import streamlit as st
import os
from dotenv import load_dotenv
import speech_recognition as sr
import PyPDF2
from groq import Groq
import google.generativeai as genai
from prisma import Client
import json
import asyncio  # ✅ Required for async functions

# ✅ Initialize Prisma Client
db = Client()

# ✅ Load environment variables
load_dotenv()

# ✅ Redirect if user is not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("You must log in to access this page.")
    st.stop()

# ✅ Get logged-in user's email
user_email = st.session_state.get("logged_in_user")

st.title("🤖 AI Chat")
st.write("Come let me share your work💬")

# ✅ Configure APIs
groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not groq_api_key or not google_api_key:
    st.error("Missing API keys! Set them in your environment variables.")
    st.stop()

groq_client = Groq(api_key=groq_api_key)
genai.configure(api_key=google_api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Initialize session state for chat history
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# ✅ Fetch chat history from database asynchronously
async def fetch_chat_history():
    if user_email:
        user = await db.user.find_unique(
            where={"email": user_email},
            include={"chatHistory": True}  # Ensure related chat history is loaded
        )
        if user and user.chatHistory:
            latest_chat = sorted(user.chatHistory, key=lambda x: x.createdAt, reverse=True)[0]
            st.session_state["conversation_history"] = json.loads(latest_chat.messages)

# ✅ Run the async function in Streamlit
if "loaded_chat_history" not in st.session_state:
    asyncio.run(fetch_chat_history())  # Run async database query
    st.session_state["loaded_chat_history"] = True  # Prevent reloading on every rerun

# ✅ Function: Save chat to NeonDB
async def save_chat_to_db():
    if user_email and st.session_state["conversation_history"]:
        user = await db.user.find_unique(where={"email": user_email})
        if user:
            await db.chat_history.create({
                "userId": user.id,
                "messages": json.dumps(st.session_state["conversation_history"]),
                "summary": "",  # Future: Summarize chat
            })

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

    # ✅ Add PDF content if available
    if "pdf_content" in st.session_state and st.session_state["pdf_content"]:
        messages.insert(0, {"role": "system", "content": f"The user has provided a document: {st.session_state['pdf_content']}"})

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

# ✅ Save chat history when user logs out
if st.button("🚪 Logout"):
    asyncio.run(save_chat_to_db())  # Save chat to database
    st.session_state.clear()  # Clear session state
    st.switch_page("app.py")  # ✅ Redirect to login page

# ✅ Detect if user refreshes
if "chat_saved" not in st.session_state:
    st.session_state["chat_saved"] = False

if not st.session_state["chat_saved"]:
    asyncio.run(save_chat_to_db())  # Save chat history before losing session
    st.session_state["chat_saved"] = True  # Prevent multiple saves
