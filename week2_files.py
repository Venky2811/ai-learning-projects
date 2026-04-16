# ============================================
# PART 1 - txt files
# ============================================

# writing to a txt file - creates file if it doesnt exist
with open("notes.txt", "w") as file:
    file.write("This is my first AI Note\n")
    file.write("I am learning Python for AI\n")

print("notes.text created successfully!!")

# reading a txt file
with open("notes.txt","r") as file:
    content=file.read()
    print("\n--- File Contents ---")
    print(content)

# reading line by line
with open("notes.txt","r") as file:
    print("---Line By Line---")
    for line in file:
        print(line.strip())     # strip() removes extra spaces and newlines

# appending to a file - adds without deleting existing content
with open("notes.txt","a") as file:
    file.write("RAG stands for Retrieval Augmented Generation\n")
    file.write("Agents can use tools to complete tasks\n")

print("\nLines added to notes.txt!")


# read again to see updated content
with open("notes.txt","r") as file:
    print("\n-- Updated File--")
    print(file.read())

# ============================================
# PART 2 - json files
# ============================================
import json

# saving a dictionary to json file
student = {
    "name":"Venkat",
    "age":"26",
    "skills":["Python", "LangChain","RAG"],
    "is_learning": True
}

with open("student.json","w") as file:
    json.dump(student, file, indent=4)

print("student.json created successfully!!")

# reading from json file
with open("student.json","r") as file:
    loaded_student = json.load(file)

print("\n--- Loaded from JSON ---")
print(f"Name: {loaded_student['name']}")
print(f"Skills: {loaded_student['skills']}")


# real AI use case - saving chat history to json
chat_history = [
    {"role":"user", "content":"What is RAG?"},
    {"role":"assistant","content":"RAG is retrieval augmented generation"},
    {"role":"user","content":"Give me an example"},
    {"role":"assistant","content":"Sure! Here is an example..."}
]

# save chat history
with open("chat_history.json","w") as file:
    json.dump(chat_history, file, indent=4)

print("\nChat history saved!")

# load chat history back
with open("chat_history.json","r") as file:
    loaded_history = json.load(file)

print("\n--- Loaded Chat History---")
for message in loaded_history:
    print(f"{message['role'].upper()}: {message['content']}")