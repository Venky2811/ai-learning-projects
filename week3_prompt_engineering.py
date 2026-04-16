from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_with_persona(system_prompt, user_question):
    response = client.chat.completions.create(
        model= "gpt-3.5-turbo",
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_question}
        ]
    )
    return response.choices[0].message.content

# same question, 4 different personas - watch how answer changes!
question = "What is machine learning?"

# persona 1 - simple tutor
print("=" * 50)
print("PERSONA 1 - Simple Tutor:")
print("=" * 50)
simple_prompt = """You are a friendly tutor explaining 
concepts to a complete beginner. Use simple words, 
avoid jargon, and use a real life analogy."""
print(ask_with_persona(simple_prompt, question))

# persona 2 - technical expert
print("\n" + "=" * 50)
print("PERSONA 2 - Technical Expert:")
print("=" * 50)
technical_prompt = """You are a senior ML engineer with 
10 years experience. Give a technical and precise answer 
with proper terminology."""
print(ask_with_persona(technical_prompt, question))

# persona 3 - format control
print("\n" + "=" * 50)
print("PERSONA 3 - Structured Format:")
print("=" * 50)
format_prompt = """You are an AI tutor. Always structure 
your answer in exactly this format:
DEFINITION: (one sentence)
HOW IT WORKS: (two sentences)
REAL WORLD EXAMPLE: (one sentence)
"""
print(ask_with_persona(format_prompt, question))

# persona 4 - constrained bot
print("\n" + "=" * 50)
print("PERSONA 4 - Constrained Bot:")
print("=" * 50)
constrained_prompt = """You are an AI assistant that only 
answers questions about Python programming. If asked about 
anything else, politely say you can only help with Python."""
print(ask_with_persona(constrained_prompt, question))

# test the constraint - ask something off topic
print("\n" + "=" * 50)
print("TESTING CONSTRAINT - Off topic question:")
print("=" * 50)
print(ask_with_persona(constrained_prompt, "What is the best cricket team?"))
