from pydantic import BaseModel
from typing import Optional

class TaskSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    completed: bool = False