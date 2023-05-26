import customtkinter as ctk
import pyotp
import qrcode
import time
import sqlite3
import string
import random
from tkinter import END, messagebox
import json
from PIL import Image
import os
from cryptography.fernet import Fernet

totpkey='C6DWX2WDSYSAMYSWJY4BIMOMFMW32JAJ'
restore_code='PVFZFFURVSECWVMQ6VDX2Y3IOCJSXFZ7'
image_code=99
fernetkey=b'aPMzWRS9lbCm8EN05jYKkYmrhuKKt47HdxOWEpJB3lc='
version = "0.2.0"
hotp_path = os.getcwd() + "\hotp.jpg"

### CONSTANTS ###
def change_appearance():
    ctk.set_appearance_mode(config['appearance_mode'])
def gak():
    if settings_switch_qr.get() == 1:
        decrypt_image()
        my_image = ctk.CTkImage(dark_image=Image.open("hotp.jpg"), light_image=Image.open("hotp.jpg"), size=(150,150))
        global image
        image = ctk.CTkLabel(settings_frame_qr, image=my_image, text="")
        image.pack(expand=True)
    if settings_switch_qr.get() == 0:
        image.destroy()
        time.sleep(0.1)
        encrypt_image()
def show_restore():
    if settings_switch_restore.get() == 1:
        global settings_label_restore
        settings_label_restore = ctk.CTkTextbox(settings_frame_restore)
        settings_label_restore.insert("0.0", restore_code)
        settings_label_restore.configure(state="disabled", border_spacing=4, wrap="word", height=50)
        settings_label_restore.pack(expand=True)
    if settings_switch_restore.get() == 0:
        settings_label_restore.destroy()
def encrypt_image():
    try:
        fin = open(hotp_path, 'rb')
        image = fin.read()
        fin.close()
        image = bytearray(image)
        for index, values in enumerate(image):
            image[index] = values ^ image_code
        fin = open(hotp_path, 'wb')
        fin.write(image)
        fin.close()
    except Exception:
        print('Error caught : ', Exception.__name__)
def decrypt_image():
    try:
        fin = open(hotp_path, 'rb')
        image = fin.read()
        fin.close()
        image = bytearray(image)
        for index, values in enumerate(image):
            image[index] = values ^ image_code
        fin = open(hotp_path, 'wb')
        fin.write(image)
        fin.close()
    except Exception:
        print('Error caught : ', Exception.__name__)
def encrypt_data():
    fernet = Fernet(fernetkey)
    with open('data.db', 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open('data.db', 'wb') as encrypted_file:
        encrypted_file.write(encrypted)
def decrypt_data():
    fernet = Fernet(fernetkey)
    with open('data.db', 'rb') as enc_file:
        encrypted = enc_file.read()
    decrypted = fernet.decrypt(encrypted)
    with open('data.db', 'wb') as dec_file:
        dec_file.write(decrypted)

### FIRST STARTUP ###
try: #On first startup...
    with open('settings.json', 'x', encoding='utf-8') as f:
        config = {"length": 20, "ascii_letters": True, "digits": True, "punctuation": True, "appearance_mode": "system", "theme": "blue"}
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(config, f)
    totp = pyotp.TOTP(totpkey) #Create TOTP
    uri = pyotp.totp.TOTP(totpkey).provisioning_uri(name="Code", issuer_name="KeyPass") #Create URL for Google Auth
    qrcode.make(uri).save("hotp.jpg") #Create QR-Code from URL and save it to 'hotp.jpg'
    first = ctk.CTk()
    first.title("Setup")
    first.minsize(first.winfo_width(), first.winfo_height())
    scan_label = ctk.CTkLabel(first, text="Scan this QR-Code with an Authenticator App, the code is your login key. DON'T SHARE THIS! \nClose this window to continue")
    scan_label.pack()
    my_image = ctk.CTkImage(dark_image=Image.open("hotp.jpg"), light_image=Image.open("hotp.jpg"), size=(150,150))
    qrcode_image = ctk.CTkLabel(first, image=my_image, text="")
    qrcode_image.pack(expand=True)
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            first.destroy()
            encrypt_image()
            global loop
            loop = False
    first.protocol("WM_DELETE_WINDOW", on_closing)
    first.mainloop()
    loop = True
    while loop != True:
        time.sleep(0.1)
except FileExistsError: #If file exists -> Not first startup
    print("File already exists") #short message for tests
with open('settings.json', 'r') as f:
        config = json.load(f)
        gen_length = config['length']

### MAIN GUI ###
def ROOT():
    #GUI
    ctk.set_appearance_mode(config["appearance_mode"])
    ctk.set_default_color_theme(config["theme"])
    root = ctk.CTk()
    root.title("Key Pass 0.1.1")
    root.minsize(root.winfo_width(), root.winfo_height())
    root.geometry("1280x720")

    #Tabview
    tabview = ctk.CTkTabview(root)
    tabview.add("Start")
    tabview.add("Settings")
    tabview.add("Help")
    tabview.pack(fill=ctk.BOTH, expand=True)

    #Start Menu
    s_button_frame = ctk.CTkFrame(master = tabview.tab("Start"))
    s_button_frame.pack(side="left", fill=ctk.BOTH, expand=True)
    global s_text_frame
    s_text_frame = ctk.CTkFrame(master = tabview.tab("Start"))
    s_text_frame.pack(side="right", fill=ctk.BOTH, expand=True)
    s_searchpw_button = ctk.CTkButton(master=s_button_frame, text="Search Password", command=SEARCHPW)
    s_searchpw_button.pack(fill="x", expand=True)
    s_newpw_button = ctk.CTkButton(master=s_button_frame, text="New Password", command=NEWPW)
    s_newpw_button.pack(fill="x", expand=True)
    s_generatealert = ctk.CTkTextbox(master=s_button_frame, text_color="white")
    s_generatealert.insert("0.0", "SECURITY: You should always generate a random password to avoid doubling passwords and make cyberattacks more difficult for hackers.")
    s_generatealert.configure(state="disabled", border_spacing=4, wrap="word", height=50)
    s_generatealert.pack(fill="x", expand=True)
    global spw_output
    spw_output = ctk.CTkTextbox(master=s_text_frame, text_color="white")
    spw_output.configure(state="disabled", border_spacing=4, wrap="word")
    spw_output.pack(fill=ctk.BOTH, expand = True)

    #Settings Menu
    settings_frame = ctk.CTkFrame(master = tabview.tab("Settings"))
    settings_frame.pack(fill=ctk.BOTH, expand=True)
    settings_frame_length = ctk.CTkFrame(master=settings_frame)
    settings_frame_length.pack(expand=True)
    def length_callback(new_value):
        settings_text_length.configure(text=f"I want my passwords to be {round(new_value)} characters long.")
        config['length'] = round(new_value)
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    def ascii_callback():
        config['ascii_letters'] = settings_switch_character_ascii.get()
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    def digits_callback():
        config['digits'] = settings_switch_character_digits.get()
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    def punctuation_callback():
        config['punctuation'] = settings_switch_character_punctuation.get()
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    settings_slider_length = ctk.CTkSlider(master=settings_frame_length, from_=5, to=50, number_of_steps=46, command=length_callback)
    settings_slider_length.set(gen_length)
    settings_text_length = ctk.CTkLabel(master=settings_frame_length, text=f"I want my password to be {round(settings_slider_length.get())} characters long.")
    settings_text_length.pack(side="left", expand=True, padx=3)
    settings_slider_length.pack(side="right", expand=True, padx=3)
    settings_frame_characters = ctk.CTkFrame(master=settings_frame)
    settings_frame_characters.pack(expand=True)
    settings_switch_character_ascii = ctk.CTkSwitch(master=settings_frame_characters, text="Uppercase and Lowercase Letters", command = ascii_callback)
    settings_switch_character_ascii.pack(expand=True, padx=3)
    if config['ascii_letters'] == 1:
        settings_switch_character_ascii.select()
    settings_switch_character_digits = ctk.CTkSwitch(master=settings_frame_characters, text="Numbers", command = digits_callback)
    settings_switch_character_digits.pack(expand=True, padx=3)
    if config['digits'] == 1:
        settings_switch_character_digits.select()
    settings_switch_character_punctuation = ctk.CTkSwitch(master=settings_frame_characters, text="Punctuation", command = punctuation_callback)
    settings_switch_character_punctuation.pack(expand=True, padx=3)
    if config['punctuation'] == 1:
        settings_switch_character_punctuation.select()
    def appearance_callback(new_apperance_mode):
        config['appearance_mode'] = new_apperance_mode
        with open('settings.json', 'w') as f:
            json.dump(config,f)
        change_appearance()
    settings_frame_appearance = ctk.CTkFrame(master=settings_frame)
    settings_frame_appearance.pack(expand=True)
    settings_label_appearance = ctk.CTkLabel(settings_frame_appearance, text="Appearance Mode")
    settings_label_appearance.pack(expand=True)
    settings_option_appearance = ctk.CTkOptionMenu(settings_frame_appearance, values=["System", "Dark", "Light"], command = appearance_callback)
    settings_option_appearance.pack(expand=True)
    global settings_frame_qr
    settings_frame_qr = ctk.CTkFrame(master=settings_frame)
    settings_frame_qr.pack(expand=True)
    global settings_switch_qr
    settings_switch_qr = ctk.CTkSwitch(settings_frame_qr, text="Show Google Authenticator QR-Code!", command = gak)
    settings_switch_qr.pack(expand=True)
    global settings_frame_restore
    settings_frame_restore = ctk.CTkFrame(master=settings_frame)
    settings_frame_restore.pack(expand=True)
    global settings_switch_restore
    settings_switch_restore = ctk.CTkSwitch(settings_frame_restore, text="Show restoring code!", command=show_restore)
    settings_switch_restore.pack(expand=True)

    #Help Menu
    help_textbox = ctk.CTkTextbox(master= tabview.tab("Help"))
    help_textbox.insert("0.0", """
    How does everything work?

    As you may already noticed on top of the screen you have to Navigation menu. You can switch to the 3 screens Start, Settings and this Help menu.

    Search Password:
    When clicking the 'Search Password' Button a new window opens, which asks for 2 inputs. So for example you saved a password '1234' with the Username 'MyUsernameForGoogle'. If you now want to search the password you can just type 'MyUsernameForGoogle' in the Searchbar for Username and Email, press search and a list will display all of your Passwords with the Username/Email 'MyUsernameForGoogle' assigned to it. Remember the Searchbar is case-sensitive, that means that 'myusernameforgoogle' wouldn't provide any results as well as 'myusername'.

    New Password:
    If you want to search you first have to create. That's where the New Password Button comes in. When clicking it a new window opens. The first entry field is for the password you want to save. As the Warning on the Start screen says. It is recommended to use a generated password. You can easily generate one with the Generate Button. The Username/Email field is pretty self-explanatory. Just put in a Username or Email you want to associate with the password. As an example Password: '<b$W'$pfoRkL' and Username/Email: 'MyUsernameForGoogle'.

    The Settings tab:
    In the settings you can change, drum roll, your settings. You have a slider to change the length of generated passwords. 3 Switches to select what types of characters you want your generated password to contain. The appearance mode of the program. And you can also see your Authenticator QR-Code that is needed to login. And you can also see you Restoring Code. The Restoring Code should be stored savely on your computer and is used to enter the program without the Authenticator if you accidently deleted your Authenticator or lost your phone.""")
    help_textbox.configure(state="disabled", border_spacing=4, wrap="word")
    help_textbox.pack(fill=ctk.BOTH, expand = True)
    root.mainloop()

### GENERATE PASSWORD ###
def GENPW():
    gen_length = config['length']
    characters = []
    if config['ascii_letters'] == 1:
        characters.append(string.ascii_letters)
    if config['digits'] == 1:
        characters.append(string.digits)
    if config['punctuation'] == 1:
        characters.append(string.punctuation)
    gen_char = ''.join(characters)
    global result_str
    result_str = ''.join(random.choice(gen_char) for i in range(gen_length))
    npw_entry_password.delete(0, END)
    npw_entry_password.insert(0, result_str)

### NEW PASSWORD GUI ###
def NEWPW():
    global npw
    npw = ctk.CTk()
    npw.title("New Password")
    npw.geometry("500x200")
    npw.resizable(False, False)
    npw.grab_set()
    global npw_entry_password
    npw_entry_password = ctk.CTkEntry(master=npw, placeholder_text="Password", width=300)
    npw_entry_password.pack(pady=10)
    npw_button_generate = ctk.CTkButton(master=npw, text="Generate", command=GENPW)
    npw_button_generate.pack()
    global npw_entry_extra
    npw_entry_extra = ctk.CTkEntry(master=npw, placeholder_text="Username or Email", width=300)
    npw_entry_extra.pack(pady=10)

    npw_button_save = ctk.CTkButton(master=npw, text="Save", command=NEWDB)
    npw_button_save.pack()

    npw_imp = ctk.CTkLabel(master=npw, text="Username or Email is important for later searching in your database.\nIt is recommended to choose either of them and be consistent.")
    npw_imp.pack()
    login_credit = ctk.CTkLabel(master=npw, text=f"Created by engag1ng - Version {version}")
    login_credit.pack(side="bottom")

    def returnPressedNew(event):   	#Enter -> New Database Entry
        NEWDB()
    npw.bind('<Return>', returnPressedNew)

    npw.mainloop()
    npw.grab_release

### CREATE NEW DATABASE ENTRY ###
def NEWDB():
    if npw_entry_password.get() and npw_entry_extra.get():
        try:
            with open('data.db', 'x'):
                print("File exists")
        except FileExistsError:
            decrypt_data()
        conn = sqlite3.connect('data.db')

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passes (
                password TEXT,
                extra TEXT
            )
        """)
        cursor.execute("INSERT INTO passes VALUES (:password, :extra)", {'password': npw_entry_password.get(), 'extra': npw_entry_extra.get()})

        conn.commit()

        print(cursor.fetchall())

        conn.close()
        encrypt_data()
        time.sleep(0.25)
        npw.destroy()
    else:
        npw.grab_release()
        att = ctk.CTk()
        att.grab_set()
        att_label = ctk.CTkLabel(master=att, text="Please input something!")
        att_label.pack()
        att.mainloop()
        def on_closing():
            att.grab_release()
            npw.grab_set()
        att.protocol("WM_DELETE_WINDOW", on_closing)

### SEARCH PASSWORD ###
def SEARCHPW():
    global spw
    spw = ctk.CTk()
    spw.title("Search Password")
    spw.geometry("500x200")
    spw.resizable(False, False)
    spw.grab_set()
    global spw_entry_password
    spw_entry_password = ctk.CTkEntry(master=spw, placeholder_text="Search for Password", width=250)
    spw_entry_password.pack(pady = 5)
    global spw_entry_extra
    spw_entry_extra = ctk.CTkEntry(master=spw, placeholder_text="Search Username or Email", width=250)
    spw_entry_extra.pack()
    
    spw_search_button = ctk.CTkButton(master=spw, text="Search", command=SEARCHDB, width=250)
    spw_search_button.pack(pady=5)
    def returnPressedSearch(event):   	#Enter -> Search Database
        SEARCHDB()
    spw.bind('<Return>', returnPressedSearch)
    login_credit = ctk.CTkLabel(master=spw, text=f"Created by engag1ng - Version {version}")
    login_credit.pack(side="bottom")
    spw.mainloop()

### SEARCH DATABASE ###
def SEARCHDB():
    try:
        with open('data.db', 'x'):
            print("File exists")
    except FileExistsError:
        decrypt_data()
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passes WHERE password = (:password) or extra = (:extra)", {'password': spw_entry_password.get(), 'extra': spw_entry_extra.get()})
    conn.commit()
    list1 = cursor.fetchall()
    spw_out = '\n'.join(['          Email/Username: '.join(row) for row in list1])
    conn.close()
    encrypt_data()
    spw_output.configure(state="normal")
    print("test")
    spw_output.delete("0.0", END)  # clear the previous contents of the widget
    spw_output.insert("0.0", spw_out)
    spw_output.configure(state="disabled")
    time.sleep(0.25)
    spw.destroy()

### CREATE KEY FOR LOGIN ###
totp = pyotp.TOTP(totpkey) #Create TOTP
resultTOTP = False #Set resultTOTP to False so it doesn't skip loop

### VERIFY CODE ENTRY ###
def verifyCode():
    resultTOTP = totp.verify(login_entry.get()) #Asks for verifaction code and verifys it
    print(resultTOTP) #prints out the result
    if resultTOTP == True or login_entry.get() == restore_code:
        time.sleep(0.5)
        app.destroy()
        ROOT()

### LOGIN SCREEN ###
app = ctk.CTk()
ctk.set_appearance_mode(config['appearance_mode'])
app.title("Login")
app.minsize(app.winfo_width(), app.winfo_height())
app.geometry("300x200")
app.resizable(False, False)
login_heading = ctk.CTkLabel(master = app, text="Login", font=("",25), pady = 10, padx = 10)
login_heading.pack()
login_code = ""
login_entry = ctk.CTkEntry(master=app, placeholder_text="Verification code")
login_entry.pack()
login_button = ctk.CTkButton(master=app, text="Login", command=verifyCode)
login_button.pack()
login_credit = ctk.CTkLabel(master=app, text=f"Created by engag1ng - Version {version}")
login_credit.pack(side="bottom")
def returnPressed(event):   	#Enter -> Login
    verifyCode()
app.bind('<Return>', returnPressed)
app.mainloop()