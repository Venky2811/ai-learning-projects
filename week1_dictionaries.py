# creating a dictionary - same as object in javascript
student={
    "name":"Venkat",
    "age":"25",
    "course":"Gen AI",
    "is_learning":True
}

# accessing values by key
print(student["name"]) # Venkat
print(student["age"])   # 25

# another way to access - safer, won't crash if key missing
print(student.get("course")) # Gen AI    
print(student.get("score","N/A")) # N/A - default if key not found

# adding a new key
student["city"]="Hyderabad"
print(student)

# updating an existing key
student["age"]=26
print(student["age"])

# deleting a key
del student["city"]
print(student)

# checking if a key exists
print("name" in student) # True
print("score" in student) # False

# looping through keys
for key in student:
    print(f"{key}={student[key]}")

# real AI use case - this is what an LLM API response looks like
api_response={
    "model":"gpt-4",
    "usage":{
        "prompt_tokens":10,
        "completion_tokens":50
    },
    "message":{
        "role":"assistant",
        "content":"AI stands for Artificial Intelligence"
    }
}

# accessing nested dictionary
print(api_response["message"]["content"])
print(api_response["usage"]["prompt_tokens"])