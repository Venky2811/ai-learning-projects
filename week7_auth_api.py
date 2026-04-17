from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

app = FastAPI(
    title="Authenticated AI API",
    description="FastAPI with API Key authentication",
    version="7.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
chat_sessions = {}

# ============================================
# API KEY SETUP
# ============================================

# in production store these in a database!
# for now we use a dictionary
VALID_API_KEYS ={
    "user-venkat-key-123":{
        "name":"Venkat",
        "role":"admin",
        "requests_limit":1000
    },
    "user-demo-key-456":{
        "name":"Demo User",
        "role":"user",
        "requests_limit":100
    }
}

# request counter per key
request_counts={}

# tells FastAPI to look for API key in header called "X-API-Key"
api_key_header = APIKeyHeader(name="X-API-Key",auto_error=False)

# dependency function - runs before every protected route
async def verify_api_key(api_key:str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required! Add X-API-Key header"
        )
    
    # check request limit
    user_info = VALID_API_KEYS[api_key]
    current_count = request_counts.get(api_key,0)

    if current_count >= user_info["requests_limit"]:
        raise HTTPException(
            status_code=429,
            detail=f"Request Limit reached: {user_info['requests_limit']}"
        )
    
    # increment counter
    request_counts[api_key] = current_count + 1

    return user_info

# ============================================
# MODELS
# ============================================
class ChatRequest(BaseModel):
    message:str
    session_id: Optional[str]="default"

# ============================================
# PUBLIC ROUTES - no auth needed
# ============================================

@app.get("/")
def home():
    return{
        "message":"Authenticated AI API",
        "docs": "Add X-API-Key header to use protected endpoints",
        "test_keys":{
            "admin": "user-venkat-key-123",
            "demo": "user-demo-key-456"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# ============================================
# PROTECTED ROUTES - auth required
# ============================================

# Depends(verify_api_key) runs the auth check before this route!
@app.post("/chat")
def chat(
    request:ChatRequest,
    user: dict = Depends(verify_api_key) # auth check here!
):
    try:
        session_id = f"{user['name']}_{request.session_id}"

        if session_id not in chat_sessions:
            chat_sessions[session_id]=[]

        history=chat_sessions[session_id]
        messages=[
            SystemMessage(content=f"You are a helpful AI assistant. You are talking to {user['name']}.")
        ] + [
            HumanMessage(content=request.message)
        ]
    
        response = llm.invoke(input=messages)
        ai_reply=response.content

        history.append(HumanMessage(content=request.message))
        history.append(AIMessage(content=ai_reply))
        chat_sessions[session_id] = history

        return{
                        "user": user["name"],
            "role": user["role"],
            "session_id": session_id,
            "ai_response": ai_reply,
            "requests_used": request_counts.get(
                [k for k, v in VALID_API_KEYS.items() 
                 if v["name"] == user["name"]][0], 0
            )
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/me")
def get_my_info(user: dict=Depends(verify_api_key)):
    return{
        "name": user["name"],
        "role": user["role"],
        "requests_limit": user["requests_limit"]
    }

@app.get("/usage")
def get_usage(user: dict=Depends(verify_api_key)):
    api_key= [k for k, v in VALID_API_KEYS.items() 
               if v["name"] == user["name"]][0]
    used = request_counts.get(api_key, 0)
    return{
        "name": user["name"],
        "requests_used": used,
        "requests_limit": user["requests_limit"],
        "requests_remaining": user["requests_limit"] - used
    }

# ============================================
# GENERATE NEW API KEY
# ============================================
@app.post("/generate-key")
def generate_key(user: dict = Depends(verify_api_key)):
    # only admin can generate new keys
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can generate new keys!"
        )
    
    new_key=f"user-{secrets.token_hex(8)}"
    VALID_API_KEYS[new_key]={
        "name":f"New User {len(VALID_API_KEYS)}",
        "role": "user",
        "requests_limit": 100
    }

    return{
        "message": "New API key generated!",
        "api_key": new_key,
        "note": "Save this key — it won't be shown again!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "week7_auth_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )