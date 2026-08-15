from typing import Optional, List
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, status

# Database connection (SQLite in this case)
DATABASE_URL = "sqlite:///customer_management.db"
conn = sqlite3.connect(DATABASE_URL)

class UserService:
    def __init__(self):
        self._db = conn

    async def create_user(self, user: dict) -> None:
        """
        Create a new user in the database.

        :param user: A dictionary containing the user's information.
        :return: None
        """
        try:
            cursor = self._db.cursor()
            query = "INSERT INTO users (name, email, password)" \
                      f"VALUES (?, ?, ?)"
            values = (user['name'], user['email'], user['password'])
            await cursor.execute(query, values)
            self._db.commit()
            print("User created successfully.")
        except sqlite3.Error as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_user(self, user_id: int) -> Optional[dict]:
        """
        Retrieve a user from the database.

        :param user_id: The ID of the user to retrieve.
        :return: A dictionary containing the user's information or None if not found.
        """
        try:
            cursor = self._db.cursor()
            query = "SELECT * FROM users WHERE id = ?"
            values = (user_id,)
            result = await cursor.execute(query, values)
            return result.fetchone()
        except sqlite3.Error as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    async def update_user(self, user_id: int, updated_data: dict) -> None:
        """
        Update a user in the database.

        :param user_id: The ID of the user to update.
        :param updated_data: A dictionary containing the new user's information.
        :return: None
        """
        try:
            cursor = self._db.cursor()
            query = "UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?"
            values = (updated_data['name'], updated_data['email'], updated_data['password'], user_id)
            await cursor.execute(query, values)
            self._db.commit()
            print("User updated successfully.")
        except sqlite3.Error as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def delete_user(self, user_id: int) -> None:
        """
        Delete a user from the database.

        :param user_id: The ID of the user to delete.
        :return: None
        """
        try:
            cursor = self._db.cursor()
            query = "DELETE FROM users WHERE id = ?"
            values = (user_id,)
            await cursor.execute(query, values)
            self._db.commit()
            print("User deleted successfully.")
        except sqlite3.Error as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))