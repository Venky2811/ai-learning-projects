age = 25
score = 45
is_Student = True

# basic if/else - no curly braces, just colon and indent
if age >=18:
    print("You are an adult")
else:
    print("You are a minor")

# if / elif / else - elif is same as else if in javascript
if score >=90:
    print("Grade: A")
elif score >=75:
    print("Grade: B")
elif score >=60:
    print("Grade: C")
else:
    print("Grade: F")
    
# multiple conditions - and / or instead of && / ||
if age >=18 and is_Student:
    print("Major Student")

if age <=18 or score <=50:
    print("Needs Attention")
else:
    print("All Good!")

# not keyword - same as ! in javascript
if not is_Student:
    print("Not a Student")
else:
    print("Is a student")

# checking if a value exists / is empty
name="Venkat"
empty_name=""

if name:
    print(f"Name is {name}")
else:
    print("Name is empty!")

# real AI use case - checking API response
api_response={
    "status":"success",
    "content":"AI is amazing"
}

if api_response["status"]== "success":
    print(f"AI Replied: {api_response['content']}")
elif api_response["status"]== "error":
    print("Something is Wrong!")
else:
    print("Unkown Status")

    

