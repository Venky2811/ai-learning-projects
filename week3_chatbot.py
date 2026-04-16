from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# file to save chat history
History_File= "week3_chat_history.json"

# load existing chat history from file if it exists
def load_history():
    try:
        with open(History_File,"r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [] # return empty list if no history yet

# save chat history to file
def save_history(history):
    with open(History_File,"w") as f:
        json.dump(history, f, indent=4)

# send message to AI with full history
def chat(user_input, history):
    # add user message to history
    history.append({"role":"user","content":user_input})

    # send full history to OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are a helpful AI tutor teaching Python and AI concepts. Keep answers concise and clear."}
        ] + history  # system message + full conversation history
    )

    # get AI reply
    ai_reply = response.choices[0].message.content

    # add AI reply to history
    history.append({"role":"assistant","content":ai_reply})

    # save updated history to file
    save_history(history)

    return ai_reply,history

# display full chat history
def show_history(history):
    if not history:
        print("No Chat history yet!")
        return
    print("\n--- Chat History ---")
    for message in history:
        role = message["role"].upper()
        content = message["content"]
        print(f"\n{role}:\n{content}")
    print("\n--- End History---")

# main chat loop
def main():
    print("AI Tutor Chatbot - type 'quit' to exit, 'history' to see chat")
    print("=" * 50)

    # load existing history
    history=load_history()

    if history:
        print(f"Welcome back! Loaded {len(history)} previous messages.")
    else:
        print("Starting fresh conversation!")

    while True:
        # get user input
        user_input = input("\nYou: ").strip()

        # check for commands
        if user_input.lower() == 'quit':
            print("Goodbye! Chat saved.")
            break

        if user_input.lower() == "history":
            show_history(history)
            continue

        if user_input == "":
            print("Please type something!")
            continue

        # get AI response
        try:
            print("\nAI is thinking ...")
            reply, history = chat(user_input, history)
            print(f"\nAI: {reply}")
            print(f"\n(Tokens in history: {len(str(history))} chars)")

        except Exception as e:
            print(f"Error: {e}")

# run the chatbot
main()
