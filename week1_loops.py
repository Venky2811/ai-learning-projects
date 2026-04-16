# for loop over a list - most common in AI
skills = ["Python","Langchain","RAG","Agents"]

for skill in skills:
    print(f"Learning: {skill}")

# loop with index - when you need the position too
for index, skill in enumerate(skills):
    print(f"{index +1}. {skill}")

# range - loop a specific number of times
for i in range(5):
    print(f"Round{i}")

# range with start and end
for i in range(1,6):
    print(f"Week {i}")

# while loop - runs until condition is false
count =0
while count<3:
    print(f"Count is {count}")
    count+=1      # same as count++ in javascript

# break - stop the loop early
for skill in skills:
    if skill == "Langchain":
        print("Skipping Langchain for now")
        continue
    print(f"Studying: {skill}")
    
# real AI use case - looping through chat history
chat_history=[
    {"role":"user","content":"what is RAG?"},
    {"role":"assistant","content":"RAG is Retrieval Augmented Generation"},
    {"role":"user","content":"give me an example"},
    {"role":"assitant","content":"Sure! Here is an example...."}
]

print("\n-- Chat History ---")
for message in chat_history:
    role=message["role"]
    content=message["content"]
    print(f"{role.upper()}:{content}")

