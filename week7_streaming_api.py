from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

app = FastAPI(title="Streaming AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# streaming LLM - same model but with streaming=True
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    streaming=True    # this enables streaming!
)

chat_sessions = {}

class ChatRequest(BaseModel):
    message:str
    session_id: Optional[str]="default"

# ============================================
# STREAMING ENDPOINT
# ============================================

async def generate_stream(
    message: str,
    session_id: str
)-> AsyncGenerator[str, None]:
    # get or create session
    if session_id not in chat_sessions:
        chat_sessions[session_id]=[]

    history=chat_sessions[session_id]

    messages=[
        SystemMessage(content="You are a helpful AI assistant.")
    ]+history +[
        HumanMessage(content=message)
    ]

    full_response=""

    try:
        # stream the response token by token
        async for chunk in llm.astream(messages):
            if chunk.content:
                full_response +=chunk.content
                # send each chunk as Server-Sent Event
                yield f"data: {json.dumps({'token':chunk.content})}\n\n"
                await asyncio.sleep(0)  # allow other tasks to run

        # save complete response to history
        history.append(HumanMessage(content=message))
        history.append(AIMessage(content=full_response))
        
        # send done signal
        yield f"data: {json.dumps({'done': True, 'full_response':full_response})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

    
@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    return StreamingResponse(
        generate_stream(request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# regular non-streaming endpoint still available
@app.post("/chat")
async def chat(request:ChatRequest):
    if request.session_id not in chat_sessions:
        chat_sessions[request.session_id] = []

    history = chat_sessions[request.session_id]
    messages = [
        SystemMessage(content="You are a helpful AI assistant.")
    ] + history + [
        HumanMessage(content=request.message)
    ]

    response = llm.invoke(messages)
    ai_reply = response.content

    history.append(HumanMessage(content=request.message))
    history.append(AIMessage(content=ai_reply))
    chat_sessions[request.session_id] = history

    return{
        "session_id": request.session_id,
        "ai_response": ai_reply
    }

@app.get("/")
def home():
    return {"message": "Streaming AI API running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "week7_streaming_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )