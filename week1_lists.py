# creating a list - same as array in javascript
skills = ["JavaScript", "Python", "AI", "MERN"]

# printing the whole list
print(skills)

# accessing by index - starts at 0 just like javascript
print(skills[0]) #Javascript
print(skills[1]) #Python
print(skills[-1]) #last item - AI trick python has!

# adding an item to the end
skills.append("Langchain")
print(skills)

# length of list - like .length in javascript
print(len(skills))

# checking if something is in the list
print("Python" in skills) #True
print("React" in skills) #False

# looping through a list
for skill in skills:
    print(f"I know {skill}")

# list of dictionaries - you will use this ALL the time in AI
# this is exactly how chat history looks in LangChain

messages = [
    {"role":"user","content":"what is AI?"},
    {"role":"assistant","content":"AI is artificial intelligence"},
    {"role":"user","content":"give me an example"}
]

# accessing inside a list of dictionaries
print(messages[0])  # whole first message
print(messages[0]["role"]) # user
print(messages[0]["content"]) # what is AI?

# looping through chat history
for message in messages:
    print(f"{message['role']} said:{message['content']}")