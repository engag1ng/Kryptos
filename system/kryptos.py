import tkinter as tk
from tkinter import ttk, messagebox
import string
import random
import base64
import sqlite3
import hashlib
import json

from cryptography.fernet import Fernet

version = "2.0.0"

decryption_key = ""

class PlaceholderEntry(tk.Entry):
    '''
    A copy of tk.Entry but with the added feature of being able to have a placeholder text.
    '''
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.insert(0, self.placeholder)
        self.configure(fg="grey")
    
    def on_focus_in(self, event):
        """Event handler for focus in."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg="black")

    def on_focus_out(self, event):
        """Event handler for focus out."""
        if self.get() == "":
            self.insert(0, self.placeholder)
            self.configure(fg="grey")


def connect_db():
    '''Establishes connection to the SQLite database.'''
    return sqlite3.connect('data.db')

def initialize_db():
    '''Creates the database and table PASSWORDS if it doesn't already exist.
    The table PASSWORDS has 5 columns:

    id       -- Integer, Primary key, Autoincrement
    service  -- String
    password -- String
    username -- String
    email    -- String
    '''
    with connect_db() as conn:
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

def generate_key_from_string(string):
    """
    Generates and returns a Fernet compatible base64-encoded 32-byte key from an input STRING.
    """
    key = hashlib.sha256(string.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_database(key):
    """
    Takes one argument KEY and uses the cryptography library to encrypt the data.db file using KEY.
    If the file is already encrypted, nothing happens.
    Returns True if file was encrypted and False otherwise.
    """
    fernet = Fernet(generate_key_from_string(key))

    with open('data.db', 'rb') as file:
        content = file.read()

    if content.startswith(b'SQLite'):
        encrypted_content = fernet.encrypt(content)

        with open('data.db', 'wb') as file:
            file.write(encrypted_content)

        return True 

    else:
        print("Already encrypted!")
        return False

def decrypt_database(key):
    """
    Takes one argument KEY and uses the cryptography library to deencrypt the data.db file using KEY. 
    If KEY does not correctly decrypt the file, nothing happens.
    Returns True if file was decrypted and False otherwise.
    """

    fernet = Fernet(generate_key_from_string(key))

    with open('data.db', 'rb') as file:
        encrypted_content = file.read()
        if encrypted_content.startswith(b'SQLite'):
            print("Already decrypted")
            return True
    try:
        decrypted_content = fernet.decrypt(encrypted_content)
        with open('data.db', 'wb') as file:
            file.write(decrypted_content)
        return True
    except Exception:
        print("Wrong Decryption key")
        return False
        

def App():
    '''
    Creates the main application Tkinter window. Also holds all functions necessary.
    '''
    main = tk.Tk()
    main.title("Kryptos")

    def create_entry(service, password, username="", email=""):
        '''
        Creates a new entry in the database. 
        If an exact replica exists, it does nothing.
        If a similar entry exists, it asks if you want to continue. 
         - If yes, it creates a new entry. I no, it does nothing.
        It takes exactly 4 arguments.

        service  -- Website / Service the information is for
        password -- password for the account
        username -- optional, username for the service
        email    -- optional, Email for the service
        '''
        if service == "" or password == "":
            return "Service or password not specified!"
        return_value = "Already exists"

        decrypt_database(decryption_key)

        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM passwords WHERE service = ? AND password = ? AND username = ? AND email = ?', 
                        (service, password, username, email))
            exact_count = cursor.fetchone()[0]

            if exact_count == 0:
                cursor.execute('SELECT COUNT(*) FROM passwords WHERE service = ? AND (username = ? OR email = ?)', 
                        (service, username, email))
                similar_count = cursor.fetchone()[0]

                if similar_count == 0:
                    cursor.execute('INSERT INTO passwords (service, password, username, email) VALUES (?, ?, ?, ?)', 
                                (service, password, username, email))
                    
                    return_value = "Added"
                else:
                    continue_box = messagebox.askquestion("Continue?", "Similar entry found. Do you want to continue?")
                    if continue_box == "yes":
                        cursor.execute('INSERT INTO passwords (service, password, username, email) VALUES (?, ?, ?, ?)', 
                                    (service, password, username, email))
                        return_value = "Added"

            conn.commit()
        encrypt_database(decryption_key)
        return return_value

    def delete_entry(entry_id):
        '''
        Deletes the entry with the specified ID from the database.

        entry_id -- Id of the entry that's being deleted
        '''
        decrypt_database(decryption_key)
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM passwords WHERE id = ?', (entry_id,))
            conn.commit()
        encrypt_database(decryption_key)

    def on_delete(entry_id, treeview):
        '''
        Deletes an entry after confirmation.
        
        entry_id -- Id of item that should be deleted
        treeview -- Table "passwords" from database displayed in treeview
        '''
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
            delete_entry(entry_id)
            # Remove the entry from the Treeview
            for item in treeview.get_children():
                if treeview.item(item, 'values')[0] == entry_id:
                    treeview.delete(item)
                    break

    def delete_selected_entry():
        '''
        Deletes the highlighted entry using on_delete().
        '''
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showwarning("Select Entry", "Please select an entry to delete.")
            return
        
        entry_id = treeview.item(selected_item, 'values')[0]
        on_delete(entry_id, treeview)

    def open_creation_window():
        '''
        Creates a new Tkinter window ENTRY_WINDOW used for creating a new entry.

        All 4 inputs have:
        _frame -- The frame for the input and all related items
        _label -- A label displaying what's supposed to go into the entry field
        _var -- A StringVar storing the input from the entry field
        _input -- The entry field

        service -- service or website
        password -- password
        username -- optional, username
        email -- optional, linked email address
        '''
        entry_window = tk.Toplevel(main)  # Use Toplevel for non-blocking
        entry_window.title("New account")
        entry_window.minsize(400, 175)

        service_frame = tk.Frame(entry_window)
        service_frame.pack(pady=5, expand=True, fill="both")
        service_label = tk.Label(service_frame, text="Service / Website")
        service_label.pack(side="left")
        service_var = tk.StringVar(service_frame)
        service_input = tk.Entry(service_frame, textvariable=service_var)
        service_input.pack(side="right", fill="x", expand=True)

        def generate_func():
            '''
            Wrapper for generating logic
            '''
            password_var.set(generate_password())
        password_frame = tk.Frame(entry_window)
        password_frame.pack(pady=5, expand=True, fill="both")
        password_label = tk.Label(password_frame, text="Password")
        password_label.pack(side="left")
        password_var = tk.StringVar(password_frame)
        password_input = tk.Entry(password_frame, textvariable=password_var)
        password_input.pack(side="right", fill="x", expand=True)
        generate_password_button = tk.Button(password_frame, text="Generate", command=generate_func)
        generate_password_button.pack()

        username_frame = tk.Frame(entry_window)
        username_frame.pack(pady=5, expand=True, fill="both")
        username_label = tk.Label(username_frame, text="Username")
        username_label.pack(side="left")
        username_var = tk.StringVar(username_frame)
        username_input = tk.Entry(username_frame, textvariable=username_var)
        username_input.pack(side="right", fill="x", expand=True)

        email_frame = tk.Frame(entry_window)
        email_frame.pack(pady=5, expand=True, fill="both")
        email_label = tk.Label(email_frame, text="Email")
        email_label.pack(side="left")
        email_var = tk.StringVar(email_frame)
        email_input = tk.Entry(email_frame, textvariable=email_var)
        email_input.pack(side="right", fill="x", expand=True)

        def submit_func():
            '''
            Wrapper for submitting logic. 
            '''
            result = create_entry(service_var.get(), password_var.get(), username_var.get(), email_var.get())
            warning_var.set(result)
            if result == "Added":
                refresh_treeview()  # Refresh the Treeview when a new entry is added
                entry_window.destroy()  # Close the creation window

        submit_button = tk.Button(entry_window, text="Submit", command=submit_func)
        submit_button.pack(pady=10)
        warning_var = tk.StringVar(entry_window)
        warning_label = tk.Label(entry_window, textvariable=warning_var)
        warning_label.pack()

    def populate_treeview(treeview):
        '''
        Fills the TREEVIEW with data from the table PASSWORDS in the database
        '''
        decrypt_database(decryption_key)
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * from passwords')
            entries = cursor.fetchall()
        encrypt_database(decryption_key)

        for row in entries:
            treeview.insert("", "end", values=row)

    def refresh_treeview():
        '''
        Clears and repopulates the TREEVIEW with current database entries using POPULATE_TREEVIEW().
        '''
        for item in treeview.get_children():
            treeview.delete(item)
        populate_treeview(treeview)

    def search_entries():
        '''
        Filters the TREEVIEW based on the search query.
        
        search_var -- StringVar holding query
        '''
        query = search_var.get().lower()
        for item in treeview.get_children():
            treeview.delete(item)

        decrypt_database(decryption_key)
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM passwords')
            entries = cursor.fetchall()
        encrypt_database(decryption_key)

        for row in entries:
            if any(query in str(value).lower() for value in row):
                treeview.insert("", "end", values=row)

    def edit_entry():
        '''
        Selectes item for editing and shows error if no item is selected. Calls OPEN_EDITING_WINDOW() with the selected item.
        '''
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showwarning("Select Entry", "Please select an entry to edit.")
            return

        open_editing_window(selected_item)

    def open_editing_window(selected_item):
        '''
        Creates a new Tkinter window EDITING_WINDOW used for editing an entry.

        All 4 inputs have:
        _frame -- The frame for the input and all related items
        _label -- A label displaying what's supposed to go into the entry field
        _var -- A StringVar storing the input from the entry field
        _input -- The entry field

        service -- service or website
        password -- password
        username -- optional, username
        email -- optional, linked email address
        '''
        editing_window = tk.Toplevel(main)  # Use Toplevel for non-blocking
        editing_window.title("Edit entry")

        service_frame = tk.Frame(editing_window)
        service_frame.pack(pady=5, expand=True, fill="both")
        service_label = tk.Label(service_frame, text="Service / Website")
        service_label.pack(side="left")
        service_var = tk.StringVar(service_frame)
        service_input = PlaceholderEntry(service_frame, textvariable=service_var, placeholder=treeview.item(selected_item, 'values')[1]) #Old value from database
        service_input.pack(side="right")

        password_frame = tk.Frame(editing_window)
        password_frame.pack(pady=5, expand=True, fill="both")
        password_label = tk.Label(password_frame, text="Password")
        password_label.pack(side="left")
        password_var = tk.StringVar(password_frame)
        password_input = PlaceholderEntry(password_frame, textvariable=password_var, placeholder=treeview.item(selected_item, 'values')[2]) #Old value from database
        password_input.pack(side="right")

        username_frame = tk.Frame(editing_window)
        username_frame.pack(pady=5, expand=True, fill="both")
        username_label = tk.Label(username_frame, text="Username")
        username_label.pack(side="left")
        username_var = tk.StringVar(username_frame)
        username_input = PlaceholderEntry(username_frame, textvariable=username_var, placeholder=treeview.item(selected_item, 'values')[3]) #Old value from database
        username_input.pack(side="right")

        email_frame = tk.Frame(editing_window)
        email_frame.pack(pady=5, expand=True, fill="both")
        email_label = tk.Label(email_frame, text="Email")
        email_label.pack(side="left")
        email_var = tk.StringVar(email_frame)
        email_input = PlaceholderEntry(email_frame, textvariable=email_var, placeholder=treeview.item(selected_item, 'values')[4]) #Old value from database
        email_input.pack(side="right")

        def submit_func():
            '''
            Wrapper for submitting logic.
            '''
            result = edit_entry_in_db(treeview.item(selected_item, 'values')[0], service_var.get(), password_var.get(), username_var.get(), email_var.get())
            warning_var.set(result)
            if result == "Edited":
                refresh_treeview()  # Refresh the Treeview when entry is edited
                editing_window.destroy()

        submit_button = tk.Button(editing_window, text="Submit", command=submit_func)
        submit_button.pack(pady=10)
        warning_var = tk.StringVar(editing_window)
        warning_label = tk.Label(editing_window, textvariable=warning_var)
        warning_label.pack()

    def edit_entry_in_db(id, service, password, username, email):
        '''
        Deletes the old entry and replaces it with new values or old values if no new one is specified.
        '''
        decrypt_database(decryption_key)
        with connect_db() as conn:
            cursor = conn.cursor()

            selected_item = cursor.execute('SELECT * FROM passwords WHERE id = ?', (id,))
            try:
                if service == "":
                    service = selected_item[1]
                if password == "":
                    passwords = selected_item[2]
                if username == "":
                    username = selected_item[3]
                if email == "":
                    email = selected_item[4]
            except TypeError:
                print("TypeError")
            cursor.execute('DELETE FROM passwords WHERE id = ?', (id,)) # Using delete_entry() raises 'Database is locked error'. I don't f** know why :)
            cursor.execute('INSERT INTO passwords (service, password, username, email) VALUES (?, ?, ?, ?)', 
                        (service, password, username, email))
            conn.commit()
        encrypt_database(decryption_key)
        return "Edited"

    def generate_password():
        '''
        Generates a random string GENERATED_PASSWORD of a specific length.
        
        characters -- Array holding list of possible characters for generation
        generated_password_length = Integer, length of generated string
        '''
        generated_password_length = 40
        characters = []
        characters.append(string.ascii_letters)
        characters.append(string.punctuation)
        characters.append(string.digits)
        characters = ''.join(characters)
        generated_password = ''.join(random.choice(characters) for i in range(generated_password_length))
        return generated_password

    try: # Initializes database in startup() on first execution -> this will raise error as database is encrypted.
        initialize_db()  # Initializes the database when the program starts
    except sqlite3.DatabaseError:
        print("Already initialized")

    # Tabview
    tabview = ttk.Notebook(main)
    tabview.pack(expand=True, fill="both", anchor="nw")

    ## Tabs
    home_tab = tk.Frame(tabview)
    home_tab.pack(expand=True, fill="both")

    config_tab = tk.Frame(tabview)
    config_tab.pack(expand=True, fill="both")

    ## Add Tabs
    tabview.add(home_tab, text="Home")
    tabview.add(config_tab, text="Config")

    # Home Tab
    add_entry_button = tk.Button(home_tab, text="New Account", command=open_creation_window)
    add_entry_button.pack(pady=10, padx=5)

    search_var = tk.StringVar()
    search_bar_frame = tk.Frame(home_tab)
    search_bar_frame.pack()
    search_entry = tk.Entry(search_bar_frame, textvariable=search_var, width=30)
    search_entry.pack(pady=10, padx=5, side="left")
    search_button = tk.Button(search_bar_frame, text="Search", command=search_entries)
    search_button.pack(pady=5, side="right")

    treeview_columns = ("ID", "Service", "Password", "Username", "Email")
    treeview = ttk.Treeview(home_tab, columns=treeview_columns, show='headings')
    for col in treeview_columns:
        treeview.heading(col, text=col)
        treeview.column(col, anchor="center")
    treeview.pack(expand=True, fill="both")
    populate_treeview(treeview)

    button_frame = tk.Frame(home_tab)
    button_frame.pack()

    delete_button = tk.Button(button_frame, text="Delete", command=delete_selected_entry)
    delete_button.pack(pady=10, padx=10, side="left")

    edit_button = tk.Button(button_frame, text="Edit", command=edit_entry)
    edit_button.pack(pady=10, padx= 10, side="right")

    treeview_scrollbar = ttk.Scrollbar(home_tab, orient="vertical", command=treeview.yview)
    treeview.configure(yscroll=treeview_scrollbar.set)
    treeview_scrollbar.pack(side="right", fill="y")

    # Config Tab
    

    main.mainloop()

def startup():
    '''
    Creates the CONFIG_FILE with the standard config if it doesn't exist already. Also creates the STARTUP_SCREEN if the database is unencrypted.
    Returns CONFIG.
    '''
    try:
        with open('config.json', 'x', encoding='utf-8') as config_file:
            standard_config = {"length": 40, "ascii_letters": True, "digits": True, "punctuation": True}
        with open('config.json', 'w', encoding='utf-8') as config_file:
            json.dump(standard_config, config_file)

        initialize_db()
    except FileExistsError:
        print("File already exists")
    with open('data.db', 'rb') as file:
        content = file.read()
    if content.startswith(b'SQLite'):
        setup_screen = tk.Tk()
        setup_screen.title("Setup")
        setup_screen.minsize(525, 200)

        intro_text = f"""WELCOME. Thank you for choosing Kryptos as your password manager. 
        This is version {version}. For updates, release notes or documentation please visit 
        https://github.com/engag1ng/Kryptos. To get started please set an encryption password.
        """

        introduction = tk.Label(setup_screen, text=intro_text)
        introduction.pack(padx=20, pady=20)

        password_input_label = tk.Label(setup_screen, text="Please input an encryption password for your database. Store this in a secure place.\nYou will need it everytime you login to your database. This can later be changed in the settings.")
        password_input_label.pack()
        password_input_var = tk.StringVar(setup_screen)
        password_input = tk.Entry(setup_screen, textvariable=password_input_var)
        password_input.pack()

        def done_func():
            '''Wrapper for DONE_BUTTON press logic'''
            if password_input_var.get() != "":
                encrypt_database(password_input_var.get())
                setup_screen.destroy()
        done_button = tk.Button(setup_screen, text="Done", command=done_func)
        done_button.pack()

        def on_closing():
            '''Prevents user from closing window without choosing password'''
            startup()
        setup_screen.protocol("WM_DELETE_WINDOW", on_closing)

        setup_screen.mainloop()

    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    return config

def decryption_window():
    '''Creates Tkinter window that asks for DECRYPTION_KEY when program is started. Sets the DECRYPTION_KEY variable for the rest of the execution.'''
    decryption_screen = tk.Tk()
    decryption_screen.title("Decrypt Database")

    password_input_label = tk.Label(decryption_screen, text="Input Database Password!")
    password_input_label.pack()
    password_input_var = tk.StringVar(decryption_screen)
    password_input = tk.Entry(decryption_screen, textvariable=password_input_var)
    password_input.pack()

    def on_button():
        '''Wrapper for button press logic'''
        if password_input_var.get() != "" and decrypt_database(password_input_var.get()):
            global decryption_key
            decryption_key = password_input_var.get()
            encrypt_database(decryption_key)
            decryption_screen.destroy()
    password_input_button = tk.Button(decryption_screen, text="Decrypt", command=on_button)
    password_input_button.pack()

    def on_closing():
        '''Prevents user from closing the window without decrypting'''
        print("No closing allowed -_-")
    decryption_screen.protocol("WM_DELETE_WINDOW", on_closing)

    decryption_screen.mainloop()

config = startup()

decryption_window()

App()