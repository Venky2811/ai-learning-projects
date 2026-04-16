from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# create FastAPI app - same as const app = express()
app=FastAPI(
     title="My AI API",
    description="A FastAPI backend for AI applications",
    version="1.0.0"
)

# ============================================
# PART 1 - Basic Routes
# ============================================

# GET route - same as app.get() in express
@app.get("/")
def home():
    return {"message": "Welcome to My AI API!", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# GET with path parameter - same as /user/:id in express
@app.get("/user/{user_id}")
def get_user(user_id : int):
    return{
        "user_id": user_id,
        "name": f"User {user_id}",
        "message": f"Profile of user {user_id}"        
    }

# GET with query parameters - same as req.query in express
@app.get("/search")
def search(query:str, limit:int=10):
    return {
        "query": query,
        "limit": limit,
        "results": [f"Result {i} for {query}" for i in range(1, limit+1)]
    }

# ============================================
# PART 2 - POST Routes with Request Body
# ============================================

# Pydantic model - defines the shape of request body
# same as defining a schema in mongoose!
class UserCreate(BaseModel):
    name:str
    email:str
    age:int
    course: Optional[str] = "Not Specified"

class MessageRequest(BaseModel):
    message:str
    user_id: Optional[int] = 1

# POST route - same as app.post() in express
@app.post("/users")
def create_user(user: UserCreate):
    # user is automatically parsed from request body!
    return{
        "message": "User created successfully!",
        "user": {
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "course": user.course
        }
    }

@app.post("chat")
def chat_endpoint(request: MessageRequest):
    # simulate AI response - will connect to real AI later!
    response = f"You said: {request.message}. This will connect to AI soon!"
    return {
        "user_id": request.user_id,
        "user_message": request.message,
        "ai_response": response
    }

# ============================================
# PART 3 - Error Handling
# ============================================

# fake database for demo
fake_users_db = {
    1: {"name": "Venkat", "course": "Gen AI"},
    2: {"name": "Rahul", "course": "MERN Stack"},
    3: {"name": "Priya", "course": "Data Science"}
}

@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    if user_id not in fake_users_db:
        # raise HTTP exception - same as res.status(404).json() in express
        raise HTTPException(
            status_code = 404,
            detail=f"User {user_id} not found!"
        )
    return fake_users_db[user_id]

# ============================================
# RUN THE SERVER
# ============================================
if __name__ == "__main__":
    uvicorn.run(
        "week5_fastapi_basics:app",
        host="0.0.0.0",
        port=8000,
        reload=True    # like nodemon - auto restarts on changes!
    )
