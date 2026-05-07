import sqlite3
import bcrypt
from abc import ABC, abstractmethod
from typing import List, Optional
import json

DB_NAME = "studyplanner.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            task_type TEXT NOT NULL,
            extra_data TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


class BaseModel(ABC):
    @abstractmethod
    def save(self) -> int:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass


class User(BaseModel):
    def __init__(self, name: str, email: str, id: Optional[int] = None):
        self.id = id
        self._name = name
        self._email = email
        self.__password_hash = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.__password_hash = bcrypt.hashpw(
            password.encode("utf-8"), salt
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.__password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.__password_hash.encode("utf-8")
        )

    def _set_hashed_password(self, hashed: str):
        self.__password_hash = hashed

    def save(self) -> int:
        conn = get_db_connection()
        c = conn.cursor()
        if self.id is None:
            c.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (self.name, self.email, self.__password_hash),
            )
            self.id = c.lastrowid
        else:
            c.execute(
                "UPDATE users SET name=?, password_hash=? WHERE id=?",
                (self.name, self.__password_hash, self.id),
            )
        conn.commit()
        conn.close()
        return self.id

    def delete(self) -> None:
        if self.id is not None:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE user_id=?", (self.id,))
            c.execute("DELETE FROM users WHERE id=?", (self.id,))
            conn.commit()
            conn.close()

    @classmethod
    def find_by_email(cls, email: str) -> Optional["User"]:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        row = c.fetchone()
        conn.close()
        if row:
            user = cls(name=row["name"], email=row["email"], id=row["id"])
            user._set_hashed_password(row["password_hash"])
            return user
        return None

    @classmethod
    def find_by_id(cls, user_id: int) -> Optional["User"]:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            user = cls(name=row["name"], email=row["email"], id=row["id"])
            user._set_hashed_password(row["password_hash"])
            return user
        return None


class Task(BaseModel):
    def __init__(self, user_id: int, title: str, description: str,
                 status: str, priority: str, id: Optional[int] = None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority

    @abstractmethod
    def get_task_type(self) -> str:
        pass

    @abstractmethod
    def get_extra_data(self) -> str:
        pass

    def save(self) -> int:
        conn = get_db_connection()
        c = conn.cursor()
        if self.id is None:
            c.execute(
                """INSERT INTO tasks
                   (user_id, title, description, status, priority, task_type, extra_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.user_id, self.title, self.description, self.status,
                 self.priority, self.get_task_type(), self.get_extra_data()),
            )
            self.id = c.lastrowid
        else:
            c.execute(
                """UPDATE tasks
                   SET title=?, description=?, status=?, priority=?,
                       task_type=?, extra_data=?
                   WHERE id=?""",
                (self.title, self.description, self.status, self.priority,
                 self.get_task_type(), self.get_extra_data(), self.id),
            )
        conn.commit()
        conn.close()
        return self.id

    def delete(self) -> None:
        if self.id is not None:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id=?", (self.id,))
            conn.commit()
            conn.close()

    @classmethod
    def get_user_tasks(cls, user_id: int) -> List["Task"]:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
        rows = c.fetchall()
        conn.close()
        tasks: List[Task] = []
        for row in rows:
            extra = json.loads(row["extra_data"]) if row["extra_data"] else {}
            t_type = row["task_type"]
            if t_type == "Assignment":
                t = AssignmentTask(
                    row["user_id"], row["title"], row["description"],
                    row["status"], row["priority"],
                    extra.get("subject", ""), row["id"])
            elif t_type == "Exam Prep":
                t = ExamPrepTask(
                    row["user_id"], row["title"], row["description"],
                    row["status"], row["priority"],
                    extra.get("exam_date", ""), row["id"])
            else:
                t = GeneralTask(
                    row["user_id"], row["title"], row["description"],
                    row["status"], row["priority"], row["id"])
            tasks.append(t)
        return tasks


class GeneralTask(Task):
    def get_task_type(self) -> str:
        return "General"

    def get_extra_data(self) -> str:
        return "{}"


class AssignmentTask(Task):
    def __init__(self, user_id, title, description, status, priority,
                 subject: str = "", id=None):
        super().__init__(user_id, title, description, status, priority, id)
        self.subject = subject

    def get_task_type(self) -> str:
        return "Assignment"

    def get_extra_data(self) -> str:
        return json.dumps({"subject": self.subject})


class ExamPrepTask(Task):
    def __init__(self, user_id, title, description, status, priority,
                 exam_date: str = "", id=None):
        super().__init__(user_id, title, description, status, priority, id)
        self.exam_date = exam_date

    def get_task_type(self) -> str:
        return "Exam Prep"

    def get_extra_data(self) -> str:
        return json.dumps({"exam_date": self.exam_date})


init_db()
