from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import uvicorn
import os
import shutil

load_dotenv()
app = FastAPI(
    title="Full AI API",
    description="Complete AI API with Chat, RAG and Analysis",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.7)
embeddings=OpenAIEmbeddings()
chat_sessions={}
loaded_documents={}
UPLOAD_DIR="./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================
# MODELS
# ============================================

class ChatRequest(BaseModel):
    message:str
    session_id: Optional[str]="default"
    system_prompt:Optional[str]="You are a helpful AI assistant."

class QuestionRequest(BaseModel):
    document_id:str
    question:str
    session_id:Optional[str]="default"

class AnalyzeRequest(BaseModel):
    text:str

class SummarizeRequest(BaseModel):
    text:str
    max_words:Optional[int]=100

# ============================================
# ROUTES
# ============================================

@app.get("/")
def home():
    return{
        "message":"Full AI API is running!",
        "version":"5.0.0",
        "endpoints":{
            "chat": "POST /chat",
            "upload": "POST /upload",
            "ask": "POST /ask",
            "summarize": "POST /summarize",
            "analyze": "POST /analyze",
            "history": "GET /history/{session_id}",
            "documents": "GET /documents"
        }   
    }

@app.get("/health")
def health():
    return{
        "status":"healthy",
        "chat_sessions":len(chat_sessions),
        "loaded_documents":len(loaded_documents)
    }


# ============================================
# CHAT WITH MEMORY
# ============================================

@app.post("/chat")
def chat(request:ChatRequest):
    try:
        if request.session_id not in chat_sessions:
            chat_sessions[request.session_id] = []
        
        history = chat_sessions[request.session_id]
        messages=[
            SystemMessage(content=request.system_prompt)
        ] + history + [
            HumanMessage(content=request.message)
        ]

        response = llm.invoke(messages)
        ai_reply=response.content

        history.append(HumanMessage(content=request.message))
        history.append(AIMessage(content=ai_reply))
        chat_sessions[request.session_id] = history

        return{
            "session_id":request.session_id,
            "user_message":request.message,
            "ai_response":ai_reply,
            "message_count":len(history)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ============================================
# DOCUMENT UPLOAD + RAG
# ============================================

@app.post("/upload")
async def upload(file: UploadFile=File(...)):
    try:
        if not file.filename.endswith((".pdf",".txt")):
            raise HTTPException(status_code=400, detail="Only PDF and TXT supported!")
        
        file_path=f"{UPLOAD_DIR}/{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        document_id=file.filename.replace(".", "_").replace(" ", "_")

        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)

        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )    
        chunks = splitter.split_documents(documents)

        vectorstore= Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=f"/.chroma_{document_id}"
        )
        loaded_documents[document_id] = vectorstore.as_retriever(
            search_kwags={"k": 3}
        )

        return{
            "document_id":document_id,
            "filename":file.filename,
            "chunks":len(chunks),
            "message":"Document ready for questions!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@app.get("/documents")
def documents():
    return{
        "documents": list(loaded_documents.keys()),
        "count": len(loaded_documents)
    }

@app.post("/ask")
def ask(request:QuestionRequest):
    try:
        if request.document_id not in loaded_documents:
            raise HTTPException(
                status_code=404,
                detail="Document not found! Upload it first."
            )
        
        retriever = loaded_documents[request.document_id]
        session_key = f"{request.document_id}_{request.session_id}"

        if session_key not in chat_sessions:
            chat_sessions[session_key] = []

        history = chat_sessions[session_key]

        if history:
            rephrase_prompt = ChatPromptTemplate.from_messages([
                ("system", "Rephrase the follow up question to be standalone. Return only the rephrased question."),
                MessagesPlaceholder("chat_history"),
                ("human", "{question}")
            ])
            standalone = (rephrase_prompt | llm | StrOutputParser()).invoke({
                "chat_history":history,
                "question":request.question
            })
        else:
            standalone= request.question

        docs = retriever.invoke(standalone)
        context = "\n\n".join([doc.page_content for doc in docs])

        answer_prompt = ChatPromptTemplate.from_messages([
            ("system","""Answer using ONLY the context below.
             If not in context say 'This information is not in the document.'
             Context: {context}"""),
             MessagesPlaceholder("chat_history"),
             ("human","{question}")
        ])

        answer = (answer_prompt | llm | StrOutputParser()).invoke({
            "context":context,
            "chat_history":history,
            "question":request.question
        })

        history.append(HumanMessage(content=request.question))
        history.append(AIMessage(content=answer))
        chat_sessions[session_key]=history

        return{
            "document_id": request.document_id,
            "question": request.question,
            "answer": answer,
            "sources": [doc.page_content[:100] + "..." for doc in docs],
            "message_count": len(history)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ============================================
# SUMMARIZE + ANALYZE
# ============================================

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    try:
        response = llm.invoke([
            SystemMessage(content=f"Summarize in max {request.max_words} words."),
            HumanMessage(content=request.text)
        ])
        return {
            "summary": response.content,
            "original_words": len(request.text.split()),
            "summary_words": len(response.content.split())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        response = llm.invoke([
            SystemMessage(content="Analyze sentiment, main topic, key points and suggested action."),
            HumanMessage(content=request.text)
        ])
        return{
            "text": request.text,
            "analysis": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
# ============================================
# HISTORY
# ============================================

@app.get("/history/{session_id}")
def history(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found!")
    
    formatted = []
    for msg in chat_sessions[session_id]:
        role="user"if isinstance(msg, HumanMessage) else "assistant"
        formatted.append({"role":role, "content":msg.content})

    return{
        "session_id": session_id,
        "messages": formatted,
        "count": len(formatted)
    }

@app.delete("/history/{session_id}")
def clear(session_id: str):
    if session_id in chat_sessions:
        chat_sessions[session_id]=[]
        return {"message":f"Session {session_id} cleared!"}
    raise HTTPException(status_code=404, detail="Session Not Found!")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    uvicorn.run(
        "week5_final_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

