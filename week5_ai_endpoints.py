from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import uvicorn
import time

load_dotenv()

app = FastAPI(
    title="AI Powered API",
    description="FastAPI backend with OpenAI integration",
    version="2.0.0"
)

# initialize LLM once at startup - not on every request
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# in memory storage for chat sessions
# in real app this would be a database like MongoDB!
chat_sessions = {}

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================
class ChatRequest(BaseModel):
    message:str
    session_id: Optional[str] = "default"
    system_prompt: Optional[str] = "You are a helpful AI assistant."

class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    ai_response: str
    message_count: int

class ClearRequest(BaseModel):
    session_id: str

# ============================================
# BASIC ROUTES
# ============================================
@app.get("/")
def home():
    return{
        "message": "AI Powered API is running!",
        "endpoints": [
            "POST /chat - chat with AI",
            "GET /history/{session_id} - get chat history",
            "POST /clear - clear chat history",
            "POST /summarize - summarize text",
            "POST /analyze - analyze text"
        ]
    }

# ============================================
# CHAT ENDPOINT WITH MEMORY
# ============================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        session_id = request.session_id

        # create session if doesn't exist
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        # get existing history
        history = chat_sessions[session_id]

        # build messages list
        messages = [
            SystemMessage(content=request.system_prompt)
        ] + history + [
            HumanMessage(content=request.message)
        ]

        # call OpenAI
        response = llm.invoke(messages)
        ai_reply = response.content

        # save to history
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

# ============================================
# GET CHAT HISTORY
# ============================================
@app.get("/history/{session_id}")
def get_history(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found!"
        )
    
    history =chat_sessions[session_id]
    formatted=[]

    for msg in history:
        if isinstance(msg,HumanMessage):
            formatted.append({"role":"user","content":msg.content})
        else:
            formatted.append({"role":"assistant","content":msg.content})

    return {
        "session_id": session_id,
        "message_count": len(history),
        "history": formatted
    }

# ============================================
# CLEAR CHAT HISTORY
# ============================================

@app.post("/clear")
def clear_history(request: ClearRequest):
    if request.session_id in chat_sessions:
        chat_sessions[request.session_id] = []
        return {"message": f"Session {request.session_id} cleared!"}
    raise HTTPException(status_code=404, detail="Session not found!")

# ============================================
# SUMMARIZE ENDPOINT
# ============================================

class SummarizeRequest(BaseModel):
    text:str
    max_words: Optional[int]=100

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    try:
        messages = [
            SystemMessage(content=f"You are a summarization expert. Summarize the given text in maximum {request.max_words} words. Be concise and capture key points."),
            HumanMessage(content=request.text)
        ]
        response  = llm.invoke(messages)
        return {
            "original_length": len(request.text.split()),
            "summary": response.content,
            "summary_length": len(response.content.split())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ANALYZE ENDPOINT
# ============================================
class AnalyzeRequest(BaseModel):
    text: str

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        messages = [
            SystemMessage(content="""Analyze the given text and return:
1. Sentiment (positive/negative/neutral)
2. Main topic in one sentence
3. Key points as a list
4. Suggested action if any
Be concise."""),
            HumanMessage(content=request.text)
        ]
        response = llm.invoke(messages)
        return {
            "text": request.text,
            "analysis": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    uvicorn.run(
        "week5_ai_endpoints:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )