# To-Do List API

This is a simple FastAPI backend for managing a to‑do list. It provides CRUD (Create, Read, Update, Delete) endpoints for tasks stored in an in‑memory list.

## Project Structure
```
my_app/
└─ backend/
   ├─ main.py          # FastAPI application and routes
   ├─ models.py        # Pydantic models
   ├─ requirements.txt # Python dependencies
   └─ README.md        # This file
```

## Prerequisites
- Python 3.9+ installed on your system.
- `git` (optional, for cloning the repository).

## Setup
1. **Create a virtual environment**
   ```bash
   cd my_app/backend
   python -m venv venv
   ```
2. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server
Start the FastAPI development server with auto‑reload:
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

You can explore the automatically generated documentation at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST`   | `/tasks`          | Create a new task. |
| `GET`    | `/tasks`          | Retrieve all tasks. |
| `GET`    | `/tasks/{task_id}`| Retrieve a task by ID. |
| `PUT`    | `/tasks/{task_id}`| Update a task (title and/or completed). |
| `DELETE` | `/tasks/{task_id}`| Delete a task. |

## Notes
- The data is stored in‑memory, so it will be lost when the server restarts.
- This project is a minimal example intended for learning and quick prototyping.

## License
This code is provided under the MIT License.