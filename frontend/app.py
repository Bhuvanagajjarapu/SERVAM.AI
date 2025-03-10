import streamlit as st
import requests

# ✅ Backend API URL
BACKEND_URL = "http://127.0.0.1:8000"

# ✅ Page Configuration
st.set_page_config(page_title="WELCOME TO THE AI WORLD", layout="centered")

# ✅ Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ✅ Centered layout with form styling
st.markdown(
    """
    <style>
    .stApp { display: flex; align-items: center; justify-content: center; height: 100vh; }
    .login-container { padding: 2rem; border-radius: 10px; background-color: #f9f9f9; 
                       box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); width: 400px; text-align: center; }
    .stTextInput, .stButton { margin-bottom: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Authentication Card
st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.title("WELCOME TO AI WORLD")

# ✅ Dropdown for selecting Authentication Mode
auth_option = st.selectbox("Select an option", ["Login", "Signup"])

email = st.text_input("Enter Email")
password = st.text_input("Enter Password", type="password")

if auth_option == "Signup":
    if st.button("Signup"):
        normalized_email = email.strip().lower()
        response = requests.post(
            f"{BACKEND_URL}/signup",
            json={"email": normalized_email, "password": password}
        )
        try:
            response_data = response.json()
            if response.status_code == 200:
                st.success(response_data.get("message", "Signup successful"))
            else:
                st.error(response_data.get("detail", "Signup failed"))
        except requests.exceptions.JSONDecodeError:
            st.error("Unexpected response from server. Please try again.")

elif auth_option == "Login":
    if st.button("Login"):
        normalized_email = email.strip().lower()
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": normalized_email, "password": password}
        )
        try:
            response_data = response.json()
            if response.status_code == 200:
                st.session_state.logged_in = True
                st.success("Login successful! Redirecting...")

                # ✅ Redirect to chatbot page after login
                st.switch_page("pages/components.py")

            else:
                st.error(response_data.get("detail", "Invalid credentials"))
        except requests.exceptions.JSONDecodeError:
            st.error("Unexpected response from server. Please try again.")

st.markdown("</div>", unsafe_allow_html=True)
