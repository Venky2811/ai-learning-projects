# basic function - def instead of function keyword in javascript
def greet():
    print("Hello from a function!")

# calling the function
greet()

# function with parameters
def greet_user(name):
    print(f"Hello {name}, welcome to AI Learning!")

greet_user("Venkat")
greet_user("everyone")

# function with return value
def add_numbers(a,b):
    result=a+b
    return result
total=add_numbers(10,20)
print(f"Total:{total}")

# function with default parameter value
def greet_with_course(name,course="Gen AI"):
    print(f"Hello {name}, you are learning {course}")

greet_with_course("Venkat")     # uses default
greet_with_course("Venkat","langchain") # overrides default

# function returning a dictionary
def create_message(role,content):
    message={
        "role":role,
        "content":content
    }
    return message

msg= create_message("user","what is Langchain?")
print(msg)
print(msg["content"])

# real AI use case - this is how you'll structure your AI code
def ask_ai(question):
    # in week 3 this will actually call the OpenAI API
    # for now we simulate a response
    prompt=f"User asked: {question}"
    response=f"This is a simulated answer to:{question}"
    return response
answer =ask_ai("What is RAG?")
print(f"\nAI Response: {answer}")

# combining everything - function with list and loop
def display_chat(messages):
    print("\n-- Chat History ---")
    for message in messages:
        role=message["role"].upper()
        content=message["content"]
        print(f"{role}:{content}")

chat=[
    create_message("user","what is AI?"),
    create_message("assistant","AI is Artificial Intelligence"),
    create_message("user","cool, tell me more!")
]

display_chat(chat)