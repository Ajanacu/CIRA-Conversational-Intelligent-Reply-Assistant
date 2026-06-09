"""
WhatsApp Reply Assistant - FastAPI Backend
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json
import re
import hashlib
import jwt
import datetime
from database import db
from analyzer import WhatsAppAnalyzer
from reply_generator import ReplyGenerator

app = FastAPI(title="WhatsApp Reply Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()

# ── Auth helpers ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Pydantic models ───────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str

class LoginRequest(BaseModel):
    username: str
    password: str

class GenerateReplyRequest(BaseModel):
    incoming_message: str
    sender_name: Optional[str] = None
    context: Optional[str] = None
    relationship: Optional[str] = "friend"
    tone: Optional[str] = "casual"

class AnalyzeChatRequest(BaseModel):
    pass

# ── Auth routes ───────────────────────────────────────────────────────────────

@app.post("/auth/register")
def register(req: RegisterRequest):
    existing = db.get_user(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    db.create_user(req.username, hash_password(req.password), req.display_name)
    token = create_token(req.username)
    return {"token": token, "username": req.username, "display_name": req.display_name}

@app.post("/auth/login")
def login(req: LoginRequest):
    user = db.get_user(req.username)
    if not user or user["password"] != hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(req.username)
    return {"token": token, "username": req.username, "display_name": user["display_name"]}

# ── Chat upload & analysis ────────────────────────────────────────────────────

@app.post("/chat/upload")
async def upload_chat(
    file: UploadFile = File(...),
    username: str = Depends(verify_token)
):
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except Exception:
        text = content.decode("latin-1")

    analyzer = WhatsAppAnalyzer(text, username)
    parsed = analyzer.parse_messages()

    db.save_chat_messages(username, parsed)
    db.mark_analysis_dirty(username)

    return {"message": f"Uploaded {len(parsed)} messages successfully", "count": len(parsed)}

@app.post("/chat/analyze")
async def analyze_chat(req: AnalyzeChatRequest, username: str = Depends(verify_token)):
    # Return cached analysis if clean
    cached = db.get_analysis(username)
    if cached:
        return cached

    messages = db.get_chat_messages(username)
    if not messages:
        raise HTTPException(status_code=404, detail="No chat data found. Upload a chat first.")

    chat_text = "\n".join([f"{m['sender']}: {m['message']}" for m in messages])
    analyzer = WhatsAppAnalyzer(chat_text, username)
    analyzer.messages = messages

    # Compute stats locally (no API needed)
    stats = analyzer.compute_statistics()

    # AI pattern analysis (uses API) — uses hardcoded key, called once and cached
    generator = ReplyGenerator(ANTHROPIC_API_KEY)
    pattern = generator.analyze_user_pattern(username, messages)
    mood_summary = generator.analyze_mood_summary(messages)

    result = {**stats, "user_pattern": pattern, "mood_summary": mood_summary}
    db.save_analysis(username, result)

    return result

@app.get("/chat/analysis")
def get_analysis(username: str = Depends(verify_token)):
    cached = db.get_analysis(username)
    if not cached:
        raise HTTPException(status_code=404, detail="No analysis found. Run analyze first.")
    return cached

@app.get("/chat/status")
def chat_status(username: str = Depends(verify_token)):
    """Returns upload/analysis status for the current user."""
    messages = db.get_chat_messages(username)
    analysis = db.get_analysis(username)
    return {
        "has_messages": len(messages) > 0,
        "message_count": len(messages),
        "has_analysis": analysis is not None,
    }

# ── Reply generation ──────────────────────────────────────────────────────────

@app.post("/reply/generate")
async def generate_reply(req: GenerateReplyRequest, username: str = Depends(verify_token)):
    messages = db.get_chat_messages(username)
    pattern = db.get_user_pattern(username)
    analysis = db.get_analysis(username)

    # Find similar past messages for context
    similar = []
    if messages:
        incoming_lower = req.incoming_message.lower()
        for m in messages:
            if m.get("sender") != username and m.get("message"):
                msg_lower = m["message"].lower()
                words_incoming = set(incoming_lower.split())
                words_msg = set(msg_lower.split())
                overlap = len(words_incoming & words_msg)
                if overlap >= 2:
                    similar.append(m)
        similar = similar[-5:]  # last 5 similar

    generator = ReplyGenerator(ANTHROPIC_API_KEY)
    replies = generator.generate_replies(
        incoming_message=req.incoming_message,
        user_pattern=pattern or {},
        similar_messages=similar,
        sender_name=req.sender_name,
        context=req.context,
        relationship=req.relationship or "friend",
        tone=req.tone or "casual",
        all_messages=messages[-50:] if messages else []
    )

    # Save to history
    db.save_reply_history(username, req.incoming_message, replies)

    return {"replies": replies, "similar_found": len(similar) > 0}

@app.get("/reply/history")
def get_reply_history(username: str = Depends(verify_token)):
    history = db.get_reply_history(username)
    return {"history": history}

@app.get("/chat/contacts")
def get_contacts(username: str = Depends(verify_token)):
    messages = db.get_chat_messages(username)
    if not messages:
        return {"contacts": []}
    senders = list(set(m["sender"] for m in messages if m.get("sender")))
    return {"contacts": senders}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
