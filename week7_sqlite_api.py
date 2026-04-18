from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import sqlite3
import datetime
import os

load_dotenv()

app = FastAPI(
    title="AI API with SQLite",
    description="FastAPI with persistent SQLite storage",
    version="8.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# ============================================
# SQLITE SETUP
# ============================================

DB_FILE = "chatbot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized!")

# initialize database on startup
init_db()

# ============================================
# DATABASE FUNCTIONS
# ============================================

def save_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_history(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    messages = cursor.fetchall()
    conn.close()
    return messages

def delete_history(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT session_id) FROM messages")
    total_sessions = cursor.fetchone()[0]
    conn.close()
    return total_messages, total_sessions

def get_all_sessions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT session_id FROM messages")
    sessions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sessions

# ============================================
# MODELS
# ============================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    user_name: Optional[str] = "User"

# ============================================
# ROUTES
# ============================================

@app.get("/")
def home():
    return {"message": "AI API with SQLite running!"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # load history from SQLite
        history_rows = get_history(request.session_id)

        # convert to LangChain messages
        history = []
        for role, content, _ in history_rows:
            if role == "user":
                history.append(HumanMessage(content=content))
            else:
                history.append(AIMessage(content=content))

        # build messages
        messages = [
            SystemMessage(content=f"You are a helpful AI assistant talking to {request.user_name}.")
        ] + history + [
            HumanMessage(content=request.message)
        ]

        # call OpenAI
        response = llm.invoke(input=messages)
        ai_reply = response.content

        # save both messages to SQLite
        save_message(request.session_id, "user", request.message)
        save_message(request.session_id, "assistant", ai_reply)

        return {
            "session_id": request.session_id,
            "user_message": request.message,
            "ai_response": ai_reply,
            "messages_in_history": len(history_rows) + 2
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
def get_chat_history(session_id: str):
    history = get_history(session_id)

    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No history found for session {session_id}"
        )

    formatted = []
    for role, content, timestamp in history:
        formatted.append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })

    return {
        "session_id": session_id,
        "message_count": len(formatted),
        "messages": formatted
    }

@app.delete("/history/{session_id}")
def clear_chat_history(session_id: str):
    deleted = delete_history(session_id)
    return {
        "message": f"Deleted {deleted} messages",
        "session_id": session_id
    }

@app.get("/sessions")
def get_sessions():
    sessions = get_all_sessions()
    return {
        "sessions": sessions,
        "count": len(sessions)
    }

@app.get("/stats")
def stats():
    total_messages, total_sessions = get_stats()
    return {
        "total_messages": total_messages,
        "total_sessions": total_sessions,
        "database": "SQLite",
        "db_file": DB_FILE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "week7_sqlite_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )