from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================
# STEP 1 - LOAD the document
# ============================================
print(" Step 1 - Loading document...")

loader = TextLoader("ai_knowledge.txt")
documents = loader.load()

print(f"Loaded {len(documents)} document")
print(f"Total characters: {len(documents[0].page_content)}")

# ============================================
# STEP 2 - SPLIT into chunks
# ============================================
print("\nSTEP 2 - Splitting into chunks...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,     # each chunk max 200 characters
    chunk_overlap=50    # 50 characters overlap between chunks
)

chunks = splitter.split_documents(documents)

print(f"Split into {len(chunks)} chunks")
print(f"\nFirst chunk preview:")
print(chunks[0].page_content)
print(f"\nSecond chunk preview:")
print(chunks[1].page_content)

# ============================================
# STEP 3 - EMBED and STORE in ChromaDB
# ============================================
print("\nSTEP 3 - Creating embeddings and storing in ChromaDB...")

# OpenAI embeddings - converts text to vectors
embeddings = OpenAIEmbeddings()

# create ChromaDB vector store from chunks
# this automatically embeds all chunks and stores them
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"   # saves to local folder
)

print("\nStep 4 - Testing retrieval...")

# create retriever from vectorstore
retriever = vectorstore.as_retriever(
    search_kwargs={"k":2}  # return top 2 most relevant chunks
)

# test retrieval with a question
test_query = "What is RAG and how does it work?"
relevant_chunks = retriever.invoke(test_query)

print(f"Query: {test_query}")
print(f"Found {len(relevant_chunks)} relevant chunks:")
for i, chunk in enumerate(relevant_chunks):
    print(f"\nChunk {i+1}:")
    print(chunk.page_content)

# ============================================
# STEP 5 - GENERATE answer using LLM
# ============================================
print("\nSTEP 5 - Generating answer with LLM...")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# prompt template that includes retrieved context
prompt = ChatPromptTemplate.from_template("""
You are a helpful AI tutor. Answer the question using 
ONLY the context provided below. If the answer is not 
in the context, say "I don't have that information."

Context:
{context}

Question: {question}

Answer:
""")

def ask_rag(question):
    # retrieve relevant chunks
    chunks = retriever.invoke(question)

    # combine chunks into one context string
    context = "\n\n".join([chunk.page_content for chunk in chunks])

    # create prompt with context and question
    chain = prompt | llm

    # get answer
    response = chain.invoke({
        "context": context,
        "question": question
    })

    return response.content

# test with different questions
questions = [
    "What is RAG?",
    "What is LangChain used for?",
    "What are AI agents?",
    "What is the capital of France?"  # not in document - should say no info
]

print("\n--- RAG Question Answering ---")
for question in questions:
    print(f"\nQ: {question}")
    answer = ask_rag(question)
    print(f"A: {answer}")