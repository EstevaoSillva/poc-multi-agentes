import uvicorn
from fastapi import FastAPI, HTTPException
from pathlib import Path
from typing import List

# Absolute import of models
from my_app.backend.models import Task, TaskCreate, TaskUpdate

app = FastAPI(title="To-Do List API")

# In-memory storage
tasks: List[Task] = []
current_id: int = 1

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    global current_id
    new_task = Task(id=current_id, title=task.title, completed=task.completed)
    tasks.append(new_task)
    current_id += 1
    return new_task

@app.get("/tasks", response_model=List[Task])
def list_tasks():
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            updated_data = task.dict()
            if task_update.title is not None:
                updated_data["title"] = task_update.title
            if task_update.completed is not None:
                updated_data["completed"] = task_update.completed
            updated_task = Task(**updated_data)
            tasks[idx] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    # Resolve the path to the current file for any future DB usage
    base_path = Path(__file__).parent
    uvicorn.run("my_app.backend.main:app", host="0.0.0.0", port=8000, reload=True)