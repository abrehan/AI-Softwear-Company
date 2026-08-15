# backend/app/database.py

import sqlite3

class Database:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        # SQL statements to create tables
        sql_create_users = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """

        sql_create_items = """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL
            );
        """

        self.cursor.execute(sql_create_users)
        self.cursor.execute(sql_create_items)

    def add_user(self, username, password):
        # SQL statement to add a user
        sql_insert_user = "INSERT INTO users (username, password) VALUES (?, ?)"
        self.cursor.execute(sql_insert_user, (username, password))

    def get_all_users(self):
        # SQL statement to retrieve all users
        sql_select_users = "SELECT * FROM users"
        self.cursor.execute(sql_select_users)
        return self.cursor.fetchall()

    def delete_user(self, username):
        # SQL statement to delete a user
        sql_delete_user = "DELETE FROM users WHERE username = ?"
        self.cursor.execute(sql_delete_user, (username,))