// script.js - UI logic and CRUD operations for To‑Do List
// Base URL of the FastAPI backend
const BASE_URL = 'http://127.0.0.1:8000';

const taskListEl = document.getElementById('taskList');
const newTaskInput = document.getElementById('newTaskInput');
const addTaskBtn = document.getElementById('addTaskBtn');

// -------------------- Helper Functions --------------------
/**
 * Fetch JSON and handle HTTP errors
 */
async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        const err = await response.text();
        throw new Error(`Error ${response.status}: ${err}`);
    }
    // Some DELETE endpoints may return empty body
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        return response.json();
    }
    return null;
}

// -------------------- CRUD Operations --------------------
async function loadTasks() {
    try {
        const tasks = await fetchJSON(`${BASE_URL}/tasks`);
        renderTaskList(tasks);
    } catch (e) {
        console.error('Failed to load tasks', e);
    }
}

async function createTask(title) {
    try {
        const newTask = await fetchJSON(`${BASE_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        // Append the newly created task to the list
        renderTaskItem(newTask);
    } catch (e) {
        console.error('Failed to create task', e);
    }
}

async function updateTask(id, data) {
    try {
        const updated = await fetchJSON(`${BASE_URL}/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        // Replace the DOM element with the new data
        const li = document.querySelector(`li[data-id='${id}']`);
        if (li) {
            li.replaceWith(createTaskElement(updated));
        }
    } catch (e) {
        console.error('Failed to update task', e);
    }
}

async function deleteTask(id) {
    try {
        await fetchJSON(`${BASE_URL}/tasks/${id}`, { method: 'DELETE' });
        const li = document.querySelector(`li[data-id='${id}']`);
        if (li) li.remove();
    } catch (e) {
        console.error('Failed to delete task', e);
    }
}

// -------------------- UI Rendering --------------------
function renderTaskList(tasks) {
    taskListEl.innerHTML = '';
    tasks.forEach(task => {
        renderTaskItem(task);
    });
}

function renderTaskItem(task) {
    const li = createTaskElement(task);
    taskListEl.appendChild(li);
}

function createTaskElement(task) {
    const li = document.createElement('li');
    li.className = 'task-item';
    li.dataset.id = task.id;

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = task.completed;
    checkbox.addEventListener('change', () => toggleCompleted(task.id, checkbox.checked));

    const span = document.createElement('span');
    span.className = 'task-content' + (task.completed ? ' completed' : '');
    span.textContent = task.title;
    // Double‑click to edit
    span.addEventListener('dblclick', () => editTaskPrompt(task.id, task.title));

    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'task-actions';

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.addEventListener('click', () => editTaskPrompt(task.id, task.title));

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.addEventListener('click', () => {
        if (confirm('Delete this task?')) deleteTask(task.id);
    });

    actionsDiv.append(editBtn, delBtn);

    li.append(checkbox, span, actionsDiv);
    return li;
}

// -------------------- Interaction Handlers --------------------
function addTaskHandler() {
    const title = newTaskInput.value.trim();
    if (!title) return;
    createTask(title);
    newTaskInput.value = '';
}

function editTaskPrompt(id, currentTitle) {
    const newTitle = prompt('Edit task title:', currentTitle);
    if (newTitle === null) return; // user cancelled
    const trimmed = newTitle.trim();
    if (!trimmed) return alert('Title cannot be empty');
    updateTask(id, { title: trimmed, completed: false }); // keep completed status? we reset to false for simplicity
}

async function toggleCompleted(id, completed) {
    // We only need to send the new completed flag; keep title unchanged by fetching current title from DOM
    const li = document.querySelector(`li[data-id='${id}']`);
    const title = li ? li.querySelector('.task-content').textContent : '';
    await updateTask(id, { title, completed });
    // Update UI style
    const contentEl = li.querySelector('.task-content');
    if (completed) contentEl.classList.add('completed');
    else contentEl.classList.remove('completed');
}

// -------------------- Event Listeners --------------------
addTaskBtn.addEventListener('click', addTaskHandler);
newTaskInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') addTaskHandler();
});

// Initial load
loadTasks();