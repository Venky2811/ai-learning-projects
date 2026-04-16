import requests
import json

# basic GET request - same as fetch() in javascript
response = requests.get("https://httpbin.org/get")

# check status code - 200 means success
print(f"Status code: {response.status_code}")

# convert response to dictionary - same as response.json() in javascript
data = response.json()
print(f"Response type:{type(data)}")

# GET request with parameters
params={
    "name":"Venkat",
    "course":"GenAI"
}
response=requests.get("https://httpbin.org/get", params=params)
data= response.json()
print(f"\nSent params: {data['args']}")

# POST request - sending data to an API
payload={
    "question":"What is RAG?",
    "user":"Venkat"
}
response=requests.post("https://httpbin.org/post", json=payload)
data=response.json()
print(f"\nPost data sent:{data['json']}")

# real world use case - calling a free public API
# this gets a random joke
response=requests.get("https://official-joke-api.appspot.com/random_joke")

if response.status_code == 200:
    joke=response.json()
    print(f"\n-- Random Joke --")
    print(f"Setup: {joke['setup']}")
    print(f"Punchline: {joke['punchline']}")
else:
    print("Failed to get joke!")

# always use try/except with API calls
def fetch_joke():
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        response.raise_for_status()   # raises error if status is not 200
        joke=response.json()
        return f"{joke['setup']} ... {joke['punchline']}"
    except requests.exceptions.ConnectionError:
        return "No Internet Connection!"
    except requests.exceptions.HTTPError as e:
        return f"HTTP error: {e}"
    except Exception as e:
        return f"Something went wrong: {e}"
    
result = fetch_joke()
print(f"\nFetched joke: {result}")