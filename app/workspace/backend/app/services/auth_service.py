from passlib.hash import pbkdf2
import sqlite3
from typing import Optional, List
from models.user import User

def create_user(db: sqlite3.Connection, username: str, password: str) -> bool:
    # Create a new user in the database
    cursor = db.cursor()
    query = "INSERT INTO users (username, password) VALUES (?, ?)"
    cursor.execute(query, (username, pbkdf2.hash(password)))
    db.commit()
    return True

def get_user(db: sqlite3.Connection, username: str) -> Optional[User]:
    # Retrieve a user from the database
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result is None:
        return None
    return User(
        id=result[0],
        username=result[1],
        password=pbkdf2.checkpw(result[2], password)
    )

def update_user(db: sqlite3.Connection, user_id: int, new_username: str, new_password: str) -> bool:
    # Update an existing user in the database
    cursor = db.cursor()
    query = "UPDATE users SET username = ?, password = ? WHERE id = ?"
    cursor.execute(query, (new_username, new_password, user_id))
    db.commit()
    return True

def delete_user(db: sqlite3.Connection, user_id: int) -> bool:
    # Delete a user from the database
    cursor = db.cursor()
    query = "DELETE FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    db.commit()
    return True