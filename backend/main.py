from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prisma import Prisma
from passlib.hash import bcrypt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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
    password: str

# Signup API
@app.post("/signup")
async def signup(request: SignupRequest):
    # Normalize email
    normalized_email = request.email.strip().lower()

    # Check if user already exists
    existing_user = await db.user.find_unique(where={"email": normalized_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash the password
    hashed_password = bcrypt.hash(request.password)

    # Create the user
    await db.user.create(data={"email": normalized_email, "password": hashed_password})
    return {"message": "Signup successful! Please log in."}

# Login API
@app.post("/login")
async def login(request: LoginRequest):
    # Normalize email
    normalized_email = request.email.strip().lower()
    print(f"Normalized email: {normalized_email}")

    # Fetch user from the database
    user = await db.user.find_unique(where={"email": normalized_email})
    print(f"User found: {user}")

    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    # Verify the password
    print(f"Stored hashed password: {user.password}")
    print(f"Provided password: {request.password}")

    if not bcrypt.verify(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": "Login successful"}