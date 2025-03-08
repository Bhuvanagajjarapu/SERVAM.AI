import streamlit as st
import requests

# Backend API URL
BACKEND_URL = "http://127.0.0.1:8000"

st.title("Login with OTP")

# Select Login or Signup
auth_option = st.selectbox("Select an option", ["Login", "Signup"])

if auth_option == "Signup":
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")
    if st.button("Signup"):
        response = requests.post(f"{BACKEND_URL}/signup", json={"email": email, "password": password})
        if response.status_code == 200:
            st.success(response.json().get("message"))
        else:
            st.error(response.json().get("detail", "Signup failed"))

if auth_option == "Login":
    email = st.text_input("Enter Email")
    if st.button("Send OTP"):
        response = requests.post(f"{BACKEND_URL}/send-otp", json={"email": email})
        if response.status_code == 200:
            st.success("OTP sent to your email")
        else:
            st.error(response.json().get("detail", "Failed to send OTP"))

    otp = st.text_input("Enter OTP")
    if st.button("Verify OTP"):
        response = requests.post(f"{BACKEND_URL}/verify-otp", json={"email": email, "otp": otp})
        if response.status_code == 200:
            st.success("Login successful! Redirecting...")
            st.switch_page("pages/components.py")  # ✅ Redirect to chatbot page
        else:
            st.error(response.json().get("detail", "Invalid OTP"))
