from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from pathlib import Path

from config import Config
from db import db
from models import User, Project, Task, TaskStatus
from auth import create_access_token, auth_required

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ---- Auth ----
    @app.post("/api/auth/signup")
    def signup():
        data = request.get_json(force=True)
        email = (data.get("email") or "").strip().lower()
        name = (data.get("name") or "").strip()
        password = data.get("password") or ""
        if not email or not name or len(password) < 6:
            return jsonify({"detail": "Invalid input"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"detail": "Email already registered"}), 400
        user = User(email=email, name=name, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id, "email": user.email, "name": user.name})

    @app.post("/api/auth/login")
    def login():
        # Accept both form encoded and JSON for convenience
        if request.content_type and "application/x-www-form-urlencoded" in request.content_type:
            email = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")
        else:
            data = request.get_json(force=True, silent=True) or {}
            email = (data.get("username") or data.get("email") or "").strip().lower()
            password = data.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"detail": "Invalid credentials"}), 401
        token = create_access_token(str(user.id), app.config["ACCESS_TOKEN_EXPIRE_MINUTES"])
        return jsonify({"access_token": token, "token_type": "bearer"})

    @app.get("/api/me")
    @auth_required
    def me():
        user = User.query.get_or_404(request.user_id)
        return jsonify({"id": user.id, "email": user.email, "name": user.name})

    # ---- Projects ----
    @app.post("/api/projects")
    @auth_required
    def create_project():
        data = request.get_json(force=True)
        name = (data.get("name") or "").strip()
        description = data.get("description") or ""
        if not name:
            return jsonify({"detail": "Project name required"}), 400
        p = Project(name=name, description=description, owner_id=request.user_id)
        db.session.add(p)
        db.session.commit()
        return jsonify({"id": p.id, "name": p.name, "description": p.description})

    @app.get("/api/projects")
    @auth_required
    def list_projects():
        q = request.args.get("q")
        query = Project.query.filter(Project.owner_id == request.user_id)
        if q:
            like = f"%{q}%"
            query = query.filter(Project.name.ilike(like))
        items = query.order_by(Project.id.desc()).all()
        return jsonify([{"id": p.id, "name": p.name, "description": p.description} for p in items])

    @app.get("/api/projects/<int:project_id>")
    @auth_required
    def get_project(project_id: int):
        p = Project.query.filter_by(id=project_id, owner_id=request.user_id).first()
        if not p:
            return jsonify({"detail": "Project not found"}), 404
        return jsonify({"id": p.id, "name": p.name, "description": p.description})

    # ---- Board / Tasks ----
    @app.get("/api/projects/<int:project_id>/board")
    @auth_required
    def get_board(project_id: int):
        p = Project.query.filter_by(id=project_id, owner_id=request.user_id).first()
        if not p:
            return jsonify({"detail": "Project not found"}), 404
        tasks = Task.query.filter_by(project_id=project_id).order_by(Task.order.asc(), Task.id.asc()).all()
        def to_dict(t):
            return {"id": t.id, "title": t.title, "description": t.description, "status": t.status.value, "order": t.order, "project_id": t.project_id}
        board = {"todo": [], "inprogress": [], "done": []}
        for t in tasks:
            board[t.status.value].append(to_dict(t))
        return jsonify(board)

    @app.post("/api/tasks")
    @auth_required
    def create_task():
        data = request.get_json(force=True)
        project_id = data.get("project_id")
        title = (data.get("title") or "").strip()
        description = data.get("description") or ""
        if not project_id or not title:
            return jsonify({"detail": "project_id and title required"}), 400
        p = Project.query.filter_by(id=project_id, owner_id=request.user_id).first()
        if not p:
            return jsonify({"detail": "Project not found"}), 404
        # next order within 'todo'
        count = Task.query.filter_by(project_id=project_id, status=TaskStatus.todo).count()
        t = Task(title=title, description=description, project_id=project_id, status=TaskStatus.todo, order=count)
        db.session.add(t)
        db.session.commit()
        return jsonify({"id": t.id, "title": t.title, "description": t.description, "status": t.status.value, "order": t.order, "project_id": t.project_id})

    @app.patch("/api/tasks/<int:task_id>")
    @auth_required
    def update_task(task_id: int):
        t = Task.query.join(Project, Task.project_id == Project.id).filter(Task.id == task_id, Project.owner_id == request.user_id).first()
        if not t:
            return jsonify({"detail": "Task not found"}), 404
        data = request.get_json(force=True, silent=True) or {}
        if "title" in data and data["title"] is not None:
            t.title = str(data["title"])
        if "description" in data and data["description"] is not None:
            t.description = str(data["description"])
        if "status" in data and data["status"] is not None:
            try:
                t.status = TaskStatus(data["status"])
            except Exception:
                return jsonify({"detail": "Invalid status"}), 400
        if "order" in data and data["order"] is not None:
            try:
                t.order = int(data["order"])
            except Exception:
                return jsonify({"detail": "Invalid order"}), 400
        db.session.commit()
        return jsonify({"id": t.id, "title": t.title, "description": t.description, "status": t.status.value, "order": t.order, "project_id": t.project_id})

    @app.delete("/api/tasks/<int:task_id>")
    @auth_required
    def delete_task(task_id: int):
        t = Task.query.join(Project, Task.project_id == Project.id).filter(Task.id == task_id, Project.owner_id == request.user_id).first()
        if not t:
            return jsonify({"detail": "Task not found"}), 404
        db.session.delete(t)
        db.session.commit()
        return jsonify({"ok": True})

    # ---- Serve frontend (../frontend) ----
    BASE_DIR = Path(__file__).resolve().parent.parent
    FRONTEND_DIR = BASE_DIR / "frontend"

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def static_proxy(path):
        # Allow direct file serving
        if path and (FRONTEND_DIR / path).exists():
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
