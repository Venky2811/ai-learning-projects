from openai import OpenAI
from dotenv import load_dotenv
import os

# load your API key from .env file
load_dotenv()

# create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# your first real AI call!
response = client.chat.completions.create(
    model="gpt-3.5-turbo", # using 3.5 - cheaper, saves your credits
    messages=[
        {"role":"system", "content":"You are a helpful AI tutor teaching Python and AI to a student."},
        {"role":"user","content":"What is LangChain in one sentence?"}
    ]  
)

# extract the AI's reply
ai_reply = response.choices[0].message.content
print(f"AI says: {ai_reply}")

# print token usage - so you know how much you spent
print(f"\n Token used: {response.usage.total_tokens}")
print(f"Model used: {response.model}")