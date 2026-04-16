from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import json
import os
import datetime

load_dotenv()

# ============================================
# CONFIGURATION
# ============================================
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 3
MODEL = "gpt-3.5-turbo"
HISTORY_FILE = "chatbot_history.json"

# ============================================
# DOCUMENT LOADER
# ============================================
def load_document(file_path):
    print(f"\nLoading: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # detect file type and use correct loader
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Only .pdf and .txt files supported!")
    
    documents = loader.load()
    print(f"Loaded {len(documents)} page(s)")
    return documents

# ============================================
# VECTOR STORE BUILDER
# ============================================
def build_vectorstore(documents, db_name):
    print("Creating embeddings...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    
    embeddings = OpenAIEmbeddings()
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=f"./{db_name}_db"
    )
    print(f"Stored in ChromaDB!")
    return vectorstore

# ============================================
# RAG ENGINE
# ============================================
class PDFChatbot:
    def __init__(self, file_path):
        self.file_path = file_path
        self.chat_history = []
        self.llm = ChatOpenAI(model=MODEL, temperature=0)
        
        # load document name for db
        self.db_name = os.path.basename(file_path).replace(".", "_")
        
        # load and build vectorstore
        documents = load_document(file_path)
        vectorstore = build_vectorstore(documents, self.db_name)
        self.retriever = vectorstore.as_retriever(
            search_kwargs={"k": TOP_K_RESULTS}
        )
        
        # setup prompts
        self.rephrase_prompt = ChatPromptTemplate.from_messages([
            ("system", "Rephrase the follow up question to be standalone. Return only the rephrased question."),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}")
        ])
        
        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant answering 
questions about a document.
Answer using ONLY the context provided.
If answer is not in context say 'This information 
is not in the document.'
Be clear, concise and helpful.

Context:
{context}"""),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}")
        ])
        
        print("\nChatbot ready!")

    def get_standalone_question(self, question):
        if not self.chat_history:
            return question
        chain = self.rephrase_prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "chat_history": self.chat_history,
            "question": question
        })

    def get_context(self, question):
        standalone = self.get_standalone_question(question)
        docs = self.retriever.invoke(standalone)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context, standalone

    def ask(self, question):
        try:
            context, standalone = self.get_context(question)
            chain = self.answer_prompt | self.llm | StrOutputParser()
            answer = chain.invoke({
                "context": context,
                "chat_history": self.chat_history,
                "question": question
            })
            # save to history
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=answer))
            return answer, standalone

        except Exception as e:
            return f"Error: {e}", question

    def save_history(self):
        history = []
        for msg in self.chat_history:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            else:
                history.append({"role": "assistant", "content": msg.content})
        
        session = {
            "file": self.file_path,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": history
        }

        # load existing history if file exists
        try:
            with open(HISTORY_FILE, "r") as f:
                all_history = json.load(f)
        except FileNotFoundError:
            all_history = []

        all_history.append(session)

        with open(HISTORY_FILE, "w") as f:
            json.dump(all_history, f, indent=4)

        print(f"\nChat saved to {HISTORY_FILE}")

    def show_history(self):
        if not self.chat_history:
            print("No history yet!")
            return
        print("\n--- Chat History ---")
        for msg in self.chat_history:
            role = "YOU" if isinstance(msg, HumanMessage) else "AI"
            print(f"\n{role}: {msg.content}")
        print("--- End ---")

# ============================================
# MAIN CHAT INTERFACE
# ============================================
def main():
    print("=" * 50)
    print("   PDF Q&A Chatbot")
    print("=" * 50)

    # ask for file
    file_path = input("\nEnter PDF or TXT filename: ").strip()

    try:
        chatbot = PDFChatbot(file_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print("\nCommands:")
    print("  'history' - show chat history")
    print("  'save'    - save chat to file")
    print("  'quit'    - exit")
    print("=" * 50)

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "quit":
            chatbot.save_history()
            print("Goodbye!")
            break

        elif question.lower() == "history":
            chatbot.show_history()
            continue

        elif question.lower() == "save":
            chatbot.save_history()
            continue

        elif question == "":
            print("Please type something!")
            continue

        else:
            print("\nAI is thinking...")
            answer, standalone = chatbot.ask(question)

            if standalone != question:
                print(f"(Understood as: {standalone})")

            print(f"\nAI: {answer}")
            print(f"\n(Messages in memory: {len(chatbot.chat_history)})")

main()