# basic class - blueprint for a Student
class Student:
    
    # __init__ is the constructor - runs when you create an object
    # self is like 'this' in javascript
    def __init__(self, name, age, course):
        self.name= name
        self.age= age
        self.course= course

    # method - a function inside a class
    def introduce(self):
        print(f"Hi I am {self.name}, {self.age} years old, learning {self.course}")

    def study(self, topic):
        print(f"{self.name} is studying {topic}")
    
# creating objects from the class
student1 = Student("Venkat", 26, "Gen AI")
student2 = Student("Rahul", 25, "DPDM")

# calling methods
student1.introduce()
student2.introduce()
student1.study("Basics of AI Agent")
student2.study("Basics of Product Management")

# accessing properties
print(student1.name)
print(student1.course)

# modifying properties
student1.age=25
print(f"Updated age: {student1.age}")

# real AI use case - a simple Chatbot class
class Chatbot:

    def __init__(self, name, personality):
        self.name= name
        self.personality=personality
        self.chat_history=[] # empty list to store messages
    
    def add_message(self, role, content):
        message = {"role":role, "content": content}
        self.chat_history.append(message)
    
    def show_history(self):
        print(f"\n-- {self.name} Chat History ---")
        for message in self.chat_history:
            print(f"{message['role'].upper()}: {message['content']}")
    
    def respond(self, user_input):
        # add user message to history
        self.add_message("user",user_input)
        # simulate a response - in week 3 this calls real OpenAI API
        response = f"[{self.name}]: I am a {self.personality} bot. You asked:{user_input}"
        # add bot response to history
        self.add_message("assitant", response)
        print(response)

# create a chatbot object
bot = Chatbot("Studybot","Helpful AI Tutor")

# simulate a conversation
bot.respond("What is RAG?")
bot.respond("How do agents work")
bot.respond("What is Langchain?")

# show full conversation history
bot.show_history()
        

