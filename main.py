from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.tech_lead import tech_lead

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = tech_lead.run(request.message)
        return {
            "answer": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
