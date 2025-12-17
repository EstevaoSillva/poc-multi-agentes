# To‑Do List Frontend

This is a very simple static frontend for the **To‑Do List** API built with FastAPI.

## Files
- **index.html** – The main page with the UI.
- **style.css** – Basic styling.
- **script.js** – JavaScript that performs CRUD operations using the Fetch API.
- **README.md** – This file.

## How to run
1. **Open directly**
   - Just double‑click `index.html` or open it in a browser (Chrome/Firefox/Edge).
   - The page will try to communicate with the backend at `http://127.0.0.1:8000`. Make sure the FastAPI server is running.

2. **Serve with a simple static server (recommended for CORS handling)**
   ```bash
   # From the `my_app/frontend` directory
   python -m http.server 8080
   ```
   Then navigate to `http://localhost:8080` in your browser.

## Backend API contract (FastAPI)
| Method | Endpoint            | Body (JSON)                | Description               |
|--------|---------------------|----------------------------|---------------------------|
| GET    | `/tasks`            | –                          | List all tasks            |
| POST   | `/tasks`            | `{ "title": "..." }`    | Create a new task         |
| PUT    | `/tasks/{id}`       | `{ "title": "...", "completed": true|false }` | Update a task |
| DELETE | `/tasks/{id}`       | –                          | Delete a task             |

The frontend expects each task object to have at least:
```json
{ "id": number, "title": string, "completed": boolean }
```

## Notes
- All files are UTF‑8 encoded.
- No additional dependencies are required.
- If you encounter CORS errors, make sure the FastAPI backend includes the appropriate CORS middleware (e.g., `fastapi.middleware.cors.CORSMiddleware`).