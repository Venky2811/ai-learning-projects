from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================
# PART 1 - Basic LangChain Chat Model
# ============================================

# create the chat model - same as OpenAI client but through LangChain
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7    # controls creativity: 0=focused, 1=creative
)

print("=" * 50)
print("PART 1 - Basic LangChain Call:")
print("=" * 50)

# using LangChain message objects instead of raw dictionaries
messages=[
    SystemMessage(content="You are a helpful AI tutor for Python and AI."),
    HumanMessage(content="What is LangChain in one sentence?")
]

response = llm.invoke(messages)
print(f"AI: {response.content}")
print(f"Type: {type(response)}")

# ============================================
# PART 2 - Conversation with Message History
# ============================================

print("\n" + "=" * 50)
print("PART 2 - Multi turn Conversation:")
print("=" * 50)

# building conversation history manually with LangChain messages
conversation = [
    SystemMessage(content="You are a concise AI tutor. Keep answers to 2 sentences max.")
]

# turn 1
conversation.append(HumanMessage(content="What is RAG?"))
response1 = llm.invoke(conversation)
conversation.append(AIMessage(content=response1.content))
print(f"Human: What is RAG?")
print(f"AI: {response1.content}")

# turn 2 - AI remembers context from turn 1
conversation.append(HumanMessage(content="What are its main components?"))
response2=llm.invoke(conversation)
conversation.append(AIMessage(content=response2.content))
print(f"\nHuman: What are its main components?")
print(f"AI: {response2.content}")

# turn 3
conversation.append(HumanMessage(content="Give me a real world use case"))
response3 = llm.invoke(conversation)
print(f"\nHuman: Give me a real world use case")
print(f"AI: {response3.content}")

# ============================================
# PART 3 - Prompt Templates
# ============================================

print("\n" + "=" * 50)
print("PART 3 - Prompt Templates:")
print("=" * 50)

# creating a reusable prompt template with variables
# {topic} and {level} are placeholders filled in later
template = ChatPromptTemplate.from_messages([
    ("system", "You are an AI tutor. Explain concepts clearly and concisely."),
    ("human", "Explain {topic} for a {level} level student in 2 sentences.")
])

# using the template with different values
prompt1 = template.invoke({"topic": "neural networks", "level": "beginner"})
response = llm.invoke(prompt1)
print(f"Beginner explanation of neural networks:")
print(f"AI: {response.content}")

prompt2 = template.invoke({"topic": "neural networks", "level": "advanced"})
response = llm.invoke(prompt2)
print(f"\nAdvanced explanation of neural networks:")
print(f"AI: {response.content}")

# ============================================
# PART 4 - Simple Chain
# ============================================

print("\n" + "=" * 50)
print("PART 4 - LangChain Chain (LCEL):")
print("=" * 50)

# chain = prompt template + llm connected together with | pipe operator
# this is called LCEL - LangChain Expression Language
chain = template | llm

# now just invoke the chain directly - no need to call template and llm separately
result = chain.invoke({"topic": "vector databases", "level": "beginner"})
print(f"Chain result: {result.content}")

# reuse same chain with different input
result2 = chain.invoke({"topic": "AI agents", "level": "intermediate"})
print(f"\nChain result 2: {result2.content}")
