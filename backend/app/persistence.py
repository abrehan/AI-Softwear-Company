"""Small, dependency-free persistence layer for the AI Softwear Company core."""

import os
import sqlite3
import base64
import hashlib
import hmac
import secrets
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


DEFAULT_DATABASE = Path(__file__).resolve().parents[1] / "data" / "office.db"


class OfficeStore:
    def __init__(self, database_path: str | None = None) -> None:
        self.database_path = Path(database_path or os.getenv("OFFICE_DATABASE", DEFAULT_DATABASE))

    @contextmanager
    def connection(self):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, brief TEXT NOT NULL,
                    client TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, project_id TEXT,
                    owner TEXT, department TEXT NOT NULL, status TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
                CREATE TABLE IF NOT EXISTS organizations (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS memberships (organization_id TEXT NOT NULL, user_id TEXT NOT NULL, role TEXT NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY (organization_id, user_id));
                CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires_at TEXT NOT NULL, created_at TEXT NOT NULL);
                """
            )

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def record(row: sqlite3.Row | None) -> dict | None:
        return dict(row) if row else None

    @staticmethod
    def password_hash(password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
        return f"{base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

    @staticmethod
    def password_matches(password: str, stored: str) -> bool:
        salt_text, digest_text = stored.split("$", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt_text), 310_000)
        return hmac.compare_digest(base64.b64encode(digest).decode(), digest_text)

    def register_user(self, email: str, name: str, password: str, organization_name: str) -> dict | None:
        user_id, organization_id, now = str(uuid4()), str(uuid4()), self.now()
        with self.connection() as connection:
            try:
                connection.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user_id, email.lower(), name, self.password_hash(password), now))
            except sqlite3.IntegrityError:
                return None
            connection.execute("INSERT INTO organizations VALUES (?, ?, ?)", (organization_id, organization_name, now))
            connection.execute("INSERT INTO memberships VALUES (?, ?, ?, ?)", (organization_id, user_id, "owner", now))
        return self.get_user(user_id)

    def get_user(self, user_id: str) -> dict | None:
        with self.connection() as connection:
            user = self.record(connection.execute("SELECT id, email, name, created_at FROM users WHERE id = ?", (user_id,)).fetchone())
            if user:
                user["organizations"] = [dict(row) for row in connection.execute("SELECT o.id, o.name, m.role FROM organizations o JOIN memberships m ON m.organization_id = o.id WHERE m.user_id = ?", (user_id,))]
            return user

    def authenticate(self, email: str, password: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute("SELECT id, password_hash FROM users WHERE email = ?", (email.lower(),)).fetchone()
        return self.get_user(row["id"]) if row and self.password_matches(password, row["password_hash"]) else None

    def create_session(self, user_id: str) -> str:
        token, now = secrets.token_urlsafe(32), self.now()
        with self.connection() as connection:
            connection.execute("INSERT INTO sessions VALUES (?, ?, datetime('now', '+7 days'), ?)", (hashlib.sha256(token.encode()).hexdigest(), user_id, now))
        return token

    def get_session_user(self, token: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute("SELECT user_id FROM sessions WHERE token_hash = ? AND expires_at > datetime('now')", (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
        return self.get_user(row["user_id"]) if row else None

    def revoke_session(self, token: str) -> None:
        with self.connection() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (hashlib.sha256(token.encode()).hexdigest(),))

    def list_projects(self) -> list[dict]:
        with self.connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM projects ORDER BY updated_at DESC")]

    def get_project(self, project_id: str) -> dict | None:
        with self.connection() as connection:
            return self.record(connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())

    def create_project(self, name: str, brief: str, client: str | None) -> dict:
        project_id, now = str(uuid4()), self.now()
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project_id, name, brief, client, "discovery", now, now),
            )
        return self.get_project(project_id) or {}

    def update_project(self, project_id: str, changes: dict) -> dict | None:
        if not changes:
            return self.get_project(project_id)
        changes["updated_at"] = self.now()
        assignments = ", ".join(f"{field} = ?" for field in changes)
        with self.connection() as connection:
            result = connection.execute(
                f"UPDATE projects SET {assignments} WHERE id = ?", (*changes.values(), project_id)
            )
        return self.get_project(project_id) if result.rowcount else None

    def list_tasks(self, project_id: str | None = None) -> list[dict]:
        query, args = "SELECT * FROM tasks", ()
        if project_id:
            query, args = f"{query} WHERE project_id = ?", (project_id,)
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(f"{query} ORDER BY updated_at DESC", args)]

    def get_task(self, task_id: str) -> dict | None:
        with self.connection() as connection:
            return self.record(connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

    def create_task(self, title: str, project_id: str | None, owner: str | None, department: str) -> dict:
        task_id, now = str(uuid4()), self.now()
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (task_id, title, project_id, owner, department, "backlog", now, now),
            )
        return self.get_task(task_id) or {}

    def update_task(self, task_id: str, changes: dict) -> dict | None:
        if not changes:
            return self.get_task(task_id)
        changes["updated_at"] = self.now()
        assignments = ", ".join(f"{field} = ?" for field in changes)
        with self.connection() as connection:
            result = connection.execute(
                f"UPDATE tasks SET {assignments} WHERE id = ?", (*changes.values(), task_id)
            )
        return self.get_task(task_id) if result.rowcount else None


store = OfficeStore()
