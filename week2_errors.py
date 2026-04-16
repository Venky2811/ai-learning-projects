# basic try/except - same as try/catch in javascript
try:
    number = int("hello")  # this will fail - cant convert text to number
except:
    print("Something went wrong!")

# catching specific error with message
try:
    number=int("hello")
except ValueError as e:
    print(f"Value error caught: {e}")

# multiple except blocks - different errors handled differently
try:
    result = 10/0 # division by zero error
except ZeroDivisionError:
    print("Cannot divide by Zero!")
except ValueError:
    print("Wrong value type!")
except Exception as e:
    print(f"Unkown error: {e}")

# finally - always runs no matter what, same as javascript
try:
    number=int('123') # this works fine
    print(f"Number is: {number}")
except ValueError:
    print("Conversion failed!")
finally:
    print("This always runs - Success or Fail !")

# real use case - reading a file safely
try:
    with open("notes.txt","r") as file:
        content=file.read()
        print("\n--- notes.txt loaded safely---")
        print(content)
except FileNotFoundError:
    print("notes.txt file not found!")

# real AI use case - safe API call simulation
def call_ai_api(question):
    try:
        # simulating what could go wrong with a real API
        if question == "":
            raise ValueError("Question cannot be empty!")
        
        if len(question) >100:
            raise ValueError("Question is too long! keep it under 100 characters.")
        
        # simulate successful response
        response = f"AI answer to: {question}"
        return response
    
    except ValueError as e:
        print(f"Input error: {e}")
        return None
    
    except Exception as e:
        print(f"API call failed: {e}")
        return None
    
# test the function
result1 = call_ai_api("What is RAG?")
print(f"\nResult 1: {result1}")

result2=call_ai_api("")
print(f"\nResult 2:{result2}")

result3=call_ai_api("What is RAG?" * 20) # very long question
print(f"Result 3:{result3}")