from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prisma import Prisma
from passlib.hash import bcrypt
from dotenv import load_dotenv
import os
import json
from typing import List, Dict, Any

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

# ✅ Pydantic Models
class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatHistoryRequest(BaseModel):
    user_id: str
    messages: List[Dict[str, Any]]  # JSON format for messages
    summary: str = None  # Optional chat summary

# ✅ Signup API
@app.post("/signup")
async def signup(request: SignupRequest):
    normalized_email = request.email.strip().lower()
    existing_user = await db.user.find_unique(where={"email": normalized_email})
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hash(request.password)
    user = await db.user.create(data={"email": normalized_email, "password": hashed_password})

    return {"message": "Signup successful!", "user_id": user.id}

# ✅ Login API
@app.post("/login")
async def login(request: LoginRequest):
    normalized_email = request.email.strip().lower()
    user = await db.user.find_unique(where={"email": normalized_email})

    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    if not bcrypt.verify(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": user.id}

# ✅ Store Chat History API
@app.post("/store_chat_history")
async def store_chat_history(request: ChatHistoryRequest):
    print(f"📥 Received chat history request: {request}")  # Debugging

    # Step 1: Ensure user exists
    user = await db.user.find_unique(where={"id": request.user_id})
    if not user:
        print("❌ User not found in the database!")  # Debugging
        raise HTTPException(status_code=404, detail="User not found")

    print(f"✅ User found: {user.email}")  # Debugging

    # Step 2: Check if chat history exists
    existing_chat = await db.chathistory.find_first(
        where={"userId": request.user_id},
        order_by={"createdAt": "desc"}  # Corrected order_by
    )

    if existing_chat:
        print("🔄 Updating existing chat history...")  # Debugging
        existing_messages = json.loads(existing_chat.messages)
        updated_messages = existing_messages + request.messages

        await db.chathistory.update(
            where={"id": existing_chat.id},
            data={"messages": json.dumps(updated_messages)}
        )
        return {"message": "Chat history updated successfully"}
    
    else:
        print("🆕 Creating new chat history...")  # Debugging
        await db.chathistory.create(
            data={
                "userId": request.user_id,
                "messages": json.dumps(request.messages),
                "summary": request.summary or ""
            }
        )
        return {"message": "New chat history created"}

# ✅ Retrieve Chat History API
@app.get("/get_chat_history/{user_id}")
async def get_chat_history(user_id: str):
    chat_histories = await db.chathistory.find_many(
        where={"userId": user_id},
        order={"createdAt": "desc"}  # Sort by latest first
    )
    
    if chat_histories:
        return [
            {
                "messages": json.loads(chat.messages),  # Convert JSON string back to Python list
                "summary": chat.summary,
                "createdAt": chat.createdAt
            }
            for chat in chat_histories
        ]
    
    return {"messages": []}  # Return empty list if no chat history exists
