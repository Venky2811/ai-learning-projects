from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================
# STEP 1 - LOAD the PDF
# ============================================
print("STEP 1 - Loading PDF resume...")

loader = PyPDFLoader("Venkat_Abhijeet_Chinnari_resume.pdf")
pages = loader.load()

print(f"Loaded {len(pages)} pages")
for i, page in enumerate(pages):
    print(f"Page {i+1}: {len(page.page_content)} characters")

# ============================================
# STEP 2 - SPLIT into chunks
# ============================================
print("\nSTEP 2 - Splitting into chunks...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(pages)
print(f"Split into {len(chunks)} chunks")

# ============================================
# STEP 3 - EMBED and STORE
# ============================================
print("\nSTEP 3 - Creating embeddings and storing...")

embeddings = OpenAIEmbeddings()

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./resume_chroma_db"
)

print(f"Stored {len(chunks)} chunks in ChromaDB!")

# ============================================
# STEP 4 - Create Retriever
# ============================================
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)

# ============================================
# STEP 5 - RAG Chain
# ============================================
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

prompt = ChatPromptTemplate.from_template("""
You are an AI assistant analyzing a resume.
Answer the question using ONLY the context from 
the resume provided below.
If the answer is not in the resume, say 
"This information is not in the resume."

Resume Context:
{context}

Question: {question}

Answer:
""")

def ask_resume(question):
    # retrieve relevant chunks
    relevant_chunks = retriever.invoke(question)
    
    # combine into context
    context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])
    
    # create and run chain
    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "question": question
    })
    
    return response.content

# ============================================
# Chat with your resume!
# ============================================
print("\n--- Chat with Venkat's Resume ---")
print("=" * 50)

questions = [
    "What are the technical skills mentioned?",
    "What projects has the candidate built?",
    "What is the educational background?",
    "What frameworks and technologies are listed?",
    "Is this candidate suitable for an AI Engineer role?"
]

for question in questions:
    print(f"\nQ: {question}")
    answer = ask_resume(question)
    print(f"A: {answer}")