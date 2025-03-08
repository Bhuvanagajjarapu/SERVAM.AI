import smtplib
import random
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prisma import Prisma
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.hash import bcrypt
from backend.auth import store_otp, verify_stored_otp

# Load environment variables
load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

app = FastAPI()
db = Prisma()

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# Pydantic Models
class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str

class OTPRequest(BaseModel):
    email: str
    otp: str

# Function to send OTP via Email
def send_email_otp(email: str, otp: str):
    subject = "Your OTP Code"
    message = MIMEMultipart()
    message["From"] = SMTP_EMAIL
    message["To"] = email
    message["Subject"] = subject
    body = f"Your OTP code is: {otp}. It is valid for 5 minutes."
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print("❌ Email sending failed:", e)
        return False

# ✅ Signup API
@app.post("/signup")
async def signup(request: SignupRequest):
    existing_user = await db.user.find_unique(where={"email": request.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hash(request.password)
    await db.user.create(data={"email": request.email.lower(), "password": hashed_password})
    return {"message": "Signup successful! Please log in."}

# ✅ Send OTP for Login
@app.post("/send-otp")
async def send_otp(request: LoginRequest):
    user = await db.user.find_unique(where={"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=400, detail="Email not registered")

    otp = str(random.randint(100000, 999999))

    # Store OTP in the database
    await store_otp(request.email, otp)

    if send_email_otp(request.email, otp):
        return {"message": "OTP sent to email"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

# ✅ Verify OTP
@app.post("/verify-otp")
async def verify_otp(request: OTPRequest):
    is_valid, message = await verify_stored_otp(request.email, request.otp)

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message, "email": request.email.lower()}
