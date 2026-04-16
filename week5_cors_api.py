from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(
    title="AI API with CORS",
    description="FastAPI with CORS enabled for React frontend",
    version="4.0.0"
)

# ============================================
# CORS CONFIGURATION
# ============================================
# this is the fix for the Access-Control-Allow-Origin error!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React default port
        "http://localhost:5173",    # Vite React port
        "http://localhost:4200",    # Angular port - your MEAN stack!
    ],
    allow_credentials=True,
    allow_methods=["*"],            # allow GET, POST, PUT, DELETE etc
    allow_headers=["*"],            # allow all headers
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
chat_sessions = {}

# ============================================
# REQUEST MODELS
# ============================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    ai_response: str
    message_count: int

# ============================================
# ROUTES
# ============================================

@app.get("/")
def home():
    return {
        "message": "AI API with CORS is running!",
        "cors_enabled": True,
        "allowed_origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:4200"
        ]
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        session_id = request.session_id

        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        history = chat_sessions[session_id]

        messages = [
            SystemMessage(content="You are a helpful AI assistant.")
        ] + history + [
            HumanMessage(content=request.message)
        ]

        response = llm.invoke(messages)
        ai_reply = response.content

        history.append(HumanMessage(content=request.message))
        history.append(AIMessage(content=ai_reply))
        chat_sessions[session_id] = history

        return ChatResponse(
            session_id=session_id,
            user_message=request.message,
            ai_response=ai_reply,
            message_count=len(history)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
def get_history(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found!")

    history = chat_sessions[session_id]
    formatted = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            formatted.append({"role": "user", "content": msg.content})
        else:
            formatted.append({"role": "assistant", "content": msg.content})

    return {
        "session_id": session_id,
        "message_count": len(history),
        "history": formatted
    }

@app.delete("/history/{session_id}")
def clear_history(session_id: str):
    if session_id in chat_sessions:
        chat_sessions[session_id] = []
        return {"message": f"Session {session_id} cleared!"}
    raise HTTPException(status_code=404, detail="Session not found!")

# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    uvicorn.run(
        "week5_cors_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )