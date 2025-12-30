from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/users/")
def create_user(user: dict):
    # Process the user data here
    return {"message": "User created successfully", "user": user}