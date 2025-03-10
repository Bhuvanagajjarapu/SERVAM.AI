import streamlit as st
import requests

# Backend API URL
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Chat Login", layout="wide")

st.title("Login")

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Select Login or Signup
auth_option = st.selectbox("Select an option", ["Login", "Signup"])

if auth_option == "Signup":
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")
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

if auth_option == "Login":
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")
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

                # ✅ Directly switch to the chatbot page
                st.switch_page("pages/components.py")

            else:
                st.error(response_data.get("detail", "Invalid credentials"))
        except requests.exceptions.JSONDecodeError:
            st.error("Unexpected response from server. Please try again.")
