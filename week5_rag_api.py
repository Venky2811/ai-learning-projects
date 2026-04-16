from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import uvicorn
import os
import shutil

load_dotenv()

app = FastAPI(
    title="RAG API",
    description="Document Q&A API powered by RAG",
    version="3.0.0"
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
embeddings = OpenAIEmbeddings()

# store loaded documents and chat sessions
loaded_documents = {}
chat_sessions = {}

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================
# REQUEST MODELS
# ============================================
class QuestionRequest(BaseModel):
    document_id: str
    question: str
    session_id: Optional[str] = "default"

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int
    message: str

# ============================================
# HELPER - Build RAG for a document
# ============================================
def build_rag(file_path: str, document_id: str):
    # load document
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    
    documents = loader.load()
    
    #split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)

    # embed and store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=f"./chroma_{document_id}"
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever, len(chunks)

# ============================================
# UPLOAD DOCUMENT ENDPOINT
# ============================================

@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        # check file type
        if not file.filename.endswith((".pdf", ".txt")):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files supported!"
            )

        # save uploaded file
        file_path = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # create document id from filename
        document_id = file.filename.replace(".", "_").replace(" ", "_")

        # build RAG pipeline
        retriever, chunk_count = build_rag(file_path, document_id)

        # store retriever
        loaded_documents[document_id] = retriever

        return DocumentResponse(
            document_id=document_id,
            filename=file.filename,
            chunks=chunk_count,
            message=f"Document loaded successfully with {chunk_count} chunks!"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# LIST DOCUMENTS
# ============================================

@app.get("/documents")
def list_documents():
    return {
        "loaded_documents": list(loaded_documents.keys()),
        "count": len(loaded_documents)
    }

# ============================================
# ASK QUESTION ENDPOINT
# ============================================

@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        # check document exists
        if request.document_id not in loaded_documents:
            raise HTTPException(
                status_code=404,
                detail=f"Document {request.document_id} not found! Upload it first."
            )

        retriever = loaded_documents[request.document_id]

        # get or create session
        session_key = f"{request.document_id}_{request.session_id}"
        if session_key not in chat_sessions:
            chat_sessions[session_key] = []

        history = chat_sessions[session_key]

        # rephrase question if history exists
        if history:
            rephrase_prompt = ChatPromptTemplate.from_messages([
                ("system", "Rephrase the follow up question to be standalone. Return only the rephrased question."),
                MessagesPlaceholder("chat_history"),
                ("human", "{question}")
            ])
            rephrase_chain = rephrase_prompt | llm | StrOutputParser()
            standalone = rephrase_chain.invoke({
                "chat_history": history,
                "question": request.question
            })
        else:
            standalone = request.question

        # retrieve relevant chunks
        docs = retriever.invoke(standalone)
        context = "\n\n".join([doc.page_content for doc in docs])

        # generate answer
        answer_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant answering 
questions about a document.
Answer using ONLY the context provided.
If answer not in context say 'This information is not in the document.'

Context:
{context}"""),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}")
        ])

        chain = answer_prompt | llm | StrOutputParser()
        answer = chain.invoke({
            "context": context,
            "chat_history": history,
            "question": request.question
        })

        # save to history
        history.append(HumanMessage(content=request.question))
        history.append(AIMessage(content=answer))
        chat_sessions[session_key] = history

        return {
            "document_id": request.document_id,
            "session_id": request.session_id,
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
# GET CHAT HISTORY
# ============================================

@app.get("/history/{document_id}/{session_id}")
def get_history(document_id: str, session_id: str):
    session_key = f"{document_id}_{session_id}"
    if session_key not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found!")

    history = chat_sessions[session_key]
    formatted = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            formatted.append({"role": "user", "content": msg.content})
        else:
            formatted.append({"role": "assistant", "content": msg.content})

    return {
        "document_id": document_id,
        "session_id": session_id,
        "history": formatted
    }

# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    uvicorn.run(
        "week5_rag_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    