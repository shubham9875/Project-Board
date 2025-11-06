from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SAEnum
from db import db

class TaskStatus(Enum):
    todo = "todo"
    inprogress = "inprogress"
    done = "done"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False, index=True)
    name = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    projects = db.relationship("Project", back_populates="owner", lazy="dynamic")

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String, default="")
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", back_populates="projects")
    tasks = db.relationship("Task", back_populates="project", cascade="all, delete-orphan", lazy="dynamic")

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, default="")
    status = db.Column(SAEnum(TaskStatus), default=TaskStatus.todo, index=True, nullable=False)
    order = db.Column(db.Integer, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True, nullable=False)
    project = db.relationship("Project", back_populates="tasks")
