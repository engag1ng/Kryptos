import tkinter as tk
from tkinter import ttk, messagebox, Button

import sqlite3

def App():
    main = tk.Tk()
    main.title("Kryptos")

    def connect_db():
        '''
        Establishes connection to the SQLite database.
        '''
        return sqlite3.connect('data.db')

    def initialize_db():
        '''
        Creates the database and table "passwords" if it doesn't already exists.
        The database has the following columns:
        id -- Integer, primary key, autoincrement
        service -- String
        username -- String
        password -- string
        '''
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT NOT NULL,
        password TEXT NOT NULL, 
        username TEXT NOT NULL,
        email TEXT NOT NULL
        )
        ''')

        conn.commit()
        conn.close()

    def create_entry(service, password, username="", email=""):
        '''
        Creates a new entry in the database data.db. 
        If an exact replica exists, it does nothing.
        If a similar entry exists, it asks if you want to continue. 
         - If yes, it creates a new entry. I no, it does nothing.
        It takes exactly 4 arguments.

        service -- Website / Service the information is for
        password -- password for the account
        username -- optional, username for the service
        email -- optional, Email for the service
        '''
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute('''
        SELECT COUNT(*) FROM passwords
        WHERE service = ? AND username = ? AND password = ? AND email = ?
        ''', (service, username, password, email))

        exact_count = cursor.fetchone()[0]

        if exact_count > 0:
            print("Already exists")
            conn.close()
            return

        cursor.execute('''
        SELECT COUNT(*) FROM passwords
        WHERE service = ? AND (username = ? OR email = ?)
        ''', (service, username, email))

        similar_count = cursor.fetchone()[0]

        if similar_count > 0:
            print("hello")
            continue_box = messagebox.askquestion("Continue?", "Similar entry found. You might consider editing. Do you want to continue?")

            if continue_box == "no":
                conn.close()
                return
            
        cursor.execute('''
        INSERT INTO passwords (service, username, password, email) 
        VALUES (?, ?, ?, ?)''', (service, username, password, email))
        
        conn.commit()
        conn.close()

    def delete_entry(service=None, username=None, password=None, email=None):
        '''
        Deletes database entry when all specified parameters match up. 
        If more than one entry is found print("Mutliple found").
        Takes 1-4 arguments:

        service -- optional, Website / Service the information is for
        password -- optional, password for the account
        username -- optional, username for the service
        email -- optional, Email for the service 
        '''
        if not any([service, username, password, email]):
            raise ValueError("At least one argument must be specified.")

        conn = connect_db()
        cursor = conn.cursor()

        query = 'DELETE FROM passwords WHERE '
        conditions = []
        params = []

        if service:
            conditions.append('service = ?')
            params.append(service)
        if username:
            conditions.append('username = ?')
            params.append(username)
        if password:
            conditions.append('password = ?')
            params.append(password)
        if email:
            conditions.append('email = ?')
            params.append(email)

        query += ' AND '.join(conditions)

        # Check how many rows match the criteria before deletion
        cursor.execute(f'SELECT COUNT(*) FROM passwords WHERE {" AND ".join(conditions)}', params)
        count = cursor.fetchone()[0]

        if count > 1:
            conn.close()
            print("multiple found")

        cursor.execute(query, params)

        conn.commit()
        conn.close()

    initialize_db() # Initializes the database when the program starts

    create_new_entry = ttk.Button(main, text="Create new entry")

    main.mainloop()

App()