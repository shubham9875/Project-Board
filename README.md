# 🧩 Project Board — Flask Version

A lightweight **Kanban-style task management web app** built with **Flask**, **SQLite**, and **Vanilla JavaScript**.  
Users can sign up, log in, create projects, and manage tasks visually across **To Do → In Progress → Done** boards.

---

## 🚀 Features

- 🔐 User authentication (Signup / Login) via JWT  
- 🧱 Kanban-style task board with drag-and-drop  
- 🗂️ Manage multiple projects per user  
- 💾 SQLite backend (no setup required)  
- ⚙️ REST API built with Flask  
- 🌐 Clean, responsive frontend served by Flask  
- 🪶 Minimal dependencies — runs anywhere Python does  

---

## 🏗️ Project Structure

project-board-flask/
├── backend/ # Flask backend (API + DB)
│ ├── app.py # Main Flask entry point
│ ├── auth.py # Authentication logic (JWT)
│ ├── config.py # Config class (SECRET_KEY, DB URL, etc.)
│ ├── db.py # Database initialization
│ ├── models.py # SQLAlchemy models (User, Project, Task)
│ ├── requirements.txt # Backend dependencies
│ ├── init.py # Makes backend a Python package (for Flask CLI)
│ ├── app.db # SQLite database (auto-created on first run)
│ └── .venv/ # Virtual environment (not committed)
│
├── frontend/ # Frontend (served via Flask or statically)
│ ├── index.html # Landing / Login / Signup page
│ ├── projects.html # Project dashboard
│ ├── board.html # Task board (ToDo / InProgress / Done)
│ ├── css/
│ │ ├── styles.css
│ │ └── board.css
│ └── js/
│ ├── auth.js
│ ├── projects.js
│ ├── board.js
│ └── utils.js
│
└── README.md # This file 😄


