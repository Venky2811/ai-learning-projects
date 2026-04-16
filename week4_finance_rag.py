from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

# ============================================
# STEP 1 - Load and prepare document
# ============================================
print("Loading finance knowledge...")

loader = TextLoader("finance_knowledge.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = splitter.split_documents(documents)
print(f"Split into {len(chunks)} chunks")

embeddings = OpenAIEmbeddings()

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./finance_chroma_db"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print("Finance knowledge loaded and ready!")

# ============================================
# STEP 2 - Setup LLM
# ============================================
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# ============================================
# STEP 3 - Create RAG prompt
# ============================================
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a knowledgeable finance tutor explaining
concepts about Venture Capital, Hedge Funds, Private Equity
and Investment Banking.
Answer using ONLY the context provided below.
If not in context say 'I dont have that information.'
Be clear and concise.

Context:
{context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}")
])

# ============================================
# STEP 4 - Helper functions
# ============================================

def get_context(question, chat_history):
    # if there is chat history rephrase the question
    if chat_history:
        rephrase_prompt = ChatPromptTemplate.from_messages([
            ("system", "Rephrase the follow up question to be standalone based on chat history. Return only the rephrased question."),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}")
        ])
        rephrase_chain = rephrase_prompt | llm | StrOutputParser()
        standalone_question = rephrase_chain.invoke({
            "chat_history": chat_history,
            "question": question
        })
        print(f"\n(Rephrased to: {standalone_question})")
    else:
        standalone_question = question

    # retrieve relevant chunks
    docs = retriever.invoke(standalone_question)
    return "\n\n".join([doc.page_content for doc in docs])

def ask_finance(question, chat_history):
    # get relevant context
    context = get_context(question, chat_history)

    # generate answer
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "context": context,
        "chat_history": chat_history,
        "question": question
    })
    return answer

# ============================================
# STEP 5 - Conversational Chat
# ============================================

def chat_with_finance():
    print("\n--- Finance & Investing Chat ---")
    print("Ask me anything about VC, PE, Hedge Funds or IB!")
    print("Type 'quit' to exit")
    print("=" * 50)

    chat_history = []

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "quit":
            print("Goodbye!")
            break

        if question == "":
            print("Please type something!")
            continue

        try:
            answer = ask_finance(question, chat_history)
            print(f"\nAI: {answer}")

            # add to history
            chat_history.append(HumanMessage(content=question))
            chat_history.append(AIMessage(content=answer))

            print(f"\n(Messages in memory: {len(chat_history)})")

        except Exception as e:
            print(f"Error: {e}")

chat_with_finance()