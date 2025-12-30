from pydantic import BaseModel

def Task(BaseModel):
    id: int
    name: str
    description: str = None
    completed: bool = False