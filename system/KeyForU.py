import customtkinter as ctk, tkinter as tk
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
import subprocess
totpkey=''
restoreCode=''
imageCode=1
fernetkey=b''
version = "1.0.0"
hotpPath = os.getcwd() + "\hotp.jpg"

# Current working directory as the default folder_path
folderPath = os.getcwd()

# Extract the folder name from the current working directory
folderName = os.path.basename(folderPath)

# Commit message for the changes
commitMessage = "Automatic commit"

### CONSTANTS ###
def ChangeAppearance():
    ctk.set_appearance_mode(config['appearance_mode'])
def Gak():
    if settingsSwitchQr.get() == 1:
        DecryptImage()
        myImage = ctk.CTkImage(dark_image=Image.open("hotp.jpg"), light_image=Image.open("hotp.jpg"), size=(150,150))
        global image
        image = ctk.CTkLabel(settingsFrameQr, image=myImage, text="")
        image.pack(expand=True)
    if settingsSwitchQr.get() == 0:
        image.destroy()
        time.sleep(0.1)
        EncryptImage()
def ShowRestore():
    if settingsSwitchRestore.get() == 1:
        global settingsLabelRestore
        settingsLabelRestore = ctk.CTkTextbox(settingsFrameRestore)
        settingsLabelRestore.insert("0.0", restoreCode)
        settingsLabelRestore.configure(state="disabled", border_spacing=4, wrap="word", height=50)
        settingsLabelRestore.pack(expand=True)
    if settingsSwitchRestore.get() == 0:
        settingsLabelRestore.destroy()
def EncryptImage():
    try:
        fin = open(hotpPath, 'rb')
        image = fin.read()
        fin.close()
        image = bytearray(image)
        for index, values in enumerate(image):
            image[index] = values ^ imageCode
        fin = open(hotpPath, 'wb')
        fin.write(image)
        fin.close()
    except Exception:
        print('Error caught : ', Exception.__name__)
def DecryptImage():
    try:
        fin = open(hotpPath, 'rb')
        image = fin.read()
        fin.close()
        image = bytearray(image)
        for index, values in enumerate(image):
            image[index] = values ^ imageCode
        fin = open(hotpPath, 'wb')
        fin.write(image)
        fin.close()
    except Exception:
        print('Error caught : ', Exception.__name__)
def EncryptData():
    fernet = Fernet(fernetkey)
    with open('data.db', 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open('data.db', 'wb') as encryptedFile:
        encryptedFile.write(encrypted)
def DecryptData():
    fernet = Fernet(fernetkey)
    with open('data.db', 'rb') as encFile:
        encrypted = encFile.read()
    decrypted = fernet.decrypt(encrypted)
    with open('data.db', 'wb') as decFile:
        decFile.write(decrypted)
def CommitAndPush(folderPath, commitMessage):
    os.chdir(folderPath)

    subprocess.run(["git", "add", "."])

    subprocess.run(["git", "commit", "-m", commitMessage])

    subprocess.run(["git", "push", "-u", "origin", "master"])

### FIRST STARTUP ###
try: #On first startup...
    with open('settings.json', 'x', encoding='utf-8') as f:
        config = {"length": 20, "ascii_letters": True, "digits": True, "punctuation": True, "appearance_mode": "system", "theme": "blue"}
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(config, f)
    totp = pyotp.TOTP(totpkey) #Create TOTP
    uri = pyotp.totp.TOTP(totpkey).provisioning_uri(name="Login", issuer_name="KeyForU") #Create URL for Google Auth
    qrcode.make(uri).save("hotp.jpg") #Create QR-Code from URL and save it to 'hotp.jpg'
    first = ctk.CTk()
    first.title("Setup")
    first.minsize(first.winfo_width(), first.winfo_height())
    scanLabel = ctk.CTkLabel(first, text="Scan this QR-Code with an Authenticator App, the code is your login key. DON'T SHARE THIS! \nClose this window to continue")
    scanLabel.pack()
    myImage = ctk.CTkImage(dark_image=Image.open("hotp.jpg"), light_image=Image.open("hotp.jpg"), size=(150,150))
    qrImage = ctk.CTkLabel(first, image=myImage, text="")
    qrImage.pack(expand=True)
    def OnClosing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            first.destroy()
            EncryptImage()
            global loop
            loop = False
    first.protocol("WM_DELETE_WINDOW", OnClosing)
    first.mainloop()
    loop = True
    while loop != True:
        time.sleep(0.1)
except FileExistsError: #If file exists -> Not first startup
    print("File already exists") #short message for tests
with open('settings.json', 'r') as f:
        config = json.load(f)
        genLength = config['length']

### MAIN GUI ###
def Root():
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
    startButtonFrame = ctk.CTkFrame(master = tabview.tab("Start"))
    startButtonFrame.pack(side="left", fill=ctk.BOTH, expand=True)
    global startTextFrame
    startTextFrame = ctk.CTkFrame(master = tabview.tab("Start"))
    startTextFrame.pack(side="right", fill=ctk.BOTH, expand=True)
    startSearchpwButton = ctk.CTkButton(master=startButtonFrame, text="Search Password", command=SearchPw)
    startSearchpwButton.pack(fill="x", expand=True)
    startNewpwButton = ctk.CTkButton(master=startButtonFrame, text="New Password", command=NewPw)
    startNewpwButton.pack(fill="x", expand=True)
    startDeletepwButton = ctk.CTkButton(master=startButtonFrame, text="Delete Password", command=DeletePw)
    startDeletepwButton.pack(fill="x", expand=True)
    startGenerateAlert = ctk.CTkTextbox(master=startButtonFrame, text_color="white")
    startGenerateAlert.insert("0.0", "SECURITY: You should always generate a random password to avoid doubling passwords and make cyberattacks more difficult for hackers.")
    startGenerateAlert.configure(state="disabled", border_spacing=4, wrap="word", height=50)
    startGenerateAlert.pack(fill="x", expand=True)
    global searchpwOutput
    searchpwOutput = ctk.CTkTextbox(master=startTextFrame, text_color="white")
    searchpwOutput.configure(state="disabled", border_spacing=4, wrap="word")
    searchpwOutput.pack(fill=ctk.BOTH, expand = True)

    #Settings Menu
    settingsFrame = ctk.CTkFrame(master = tabview.tab("Settings"))
    settingsFrame.pack(fill=ctk.BOTH, expand=True)
    settingsFrameLength = ctk.CTkFrame(master=settingsFrame)
    settingsFrameLength.pack(expand=True)
    def LengthCallback(newValue):
        settingsTextLength.configure(text=f"I want my passwords to be {round(newValue)} characters long.")
        config['length'] = round(newValue)
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    def AsciiCallback():
        config['ascii_letters'] = settingsSwitchCharacterAscii.get()
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    def DigitsCallback():
        config['digits'] = settingsSwitchCharacterDigits.get()
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    def PunctuationCallback():
        config['punctuation'] = settingsSwitchCharacterPunctuation.get()
        with open('settings.json', 'w') as f:
            json.dump(config,f)
    settingsSliderLength = ctk.CTkSlider(master=settingsFrameLength, from_=5, to=50, number_of_steps=46, command=LengthCallback)
    settingsSliderLength.set(genLength)
    settingsTextLength = ctk.CTkLabel(master=settingsFrameLength, text=f"I want my password to be {round(settingsSliderLength.get())} characters long.")
    settingsTextLength.pack(side="left", expand=True, padx=3)
    settingsSliderLength.pack(side="right", expand=True, padx=3)
    settingsFrameCharacters = ctk.CTkFrame(master=settingsFrame)
    settingsFrameCharacters.pack(expand=True)
    settingsSwitchCharacterAscii = ctk.CTkSwitch(master=settingsFrameCharacters, text="Uppercase and Lowercase Letters", command = AsciiCallback)
    settingsSwitchCharacterAscii.pack(expand=True, padx=3)
    if config['ascii_letters'] == 1:
        settingsSwitchCharacterAscii.select()
    settingsSwitchCharacterDigits = ctk.CTkSwitch(master=settingsFrameCharacters, text="Numbers", command = DigitsCallback)
    settingsSwitchCharacterDigits.pack(expand=True, padx=3)
    if config['digits'] == 1:
        settingsSwitchCharacterDigits.select()
    settingsSwitchCharacterPunctuation = ctk.CTkSwitch(master=settingsFrameCharacters, text="Punctuation", command = PunctuationCallback)
    settingsSwitchCharacterPunctuation.pack(expand=True, padx=3)
    if config['punctuation'] == 1:
        settingsSwitchCharacterPunctuation.select()
    def AppearanceCallback(new_apperance_mode):
        config['appearance_mode'] = new_apperance_mode
        with open('settings.json', 'w') as f:
            json.dump(config,f)
        ChangeAppearance()
    settingsFrameAppearance = ctk.CTkFrame(master=settingsFrame)
    settingsFrameAppearance.pack(expand=True)
    settingsLabelAppearance = ctk.CTkLabel(settingsFrameAppearance, text="Appearance Mode")
    settingsLabelAppearance.pack(expand=True)
    settingsOptionAppearance = ctk.CTkOptionMenu(settingsFrameAppearance, values=["System", "Dark", "Light"], command = AppearanceCallback)
    settingsOptionAppearance.pack(expand=True)
    global settingsFrameQr
    settingsFrameQr = ctk.CTkFrame(master=settingsFrame)
    settingsFrameQr.pack(expand=True)
    global settingsSwitchQr
    settingsSwitchQr = ctk.CTkSwitch(settingsFrameQr, text="Show Google Authenticator QR-Code!", command = Gak)
    settingsSwitchQr.pack(expand=True)
    global settingsFrameRestore
    settingsFrameRestore = ctk.CTkFrame(master=settingsFrame)
    settingsFrameRestore.pack(expand=True)
    global settingsSwitchRestore
    settingsSwitchRestore = ctk.CTkSwitch(settingsFrameRestore, text="Show restoring code!", command=ShowRestore)
    settingsSwitchRestore.pack(expand=True)

    #Help Menu
    helpTextbox = ctk.CTkTextbox(master= tabview.tab("Help"))
    helpTextbox.insert("0.0", "How does everything work?\n\nAs you may already noticed on top of the screen you have to Navigation menu. You can switch to the 3 screens Start, Settings and this Help menu.\n\nSearch Password:\nWhen clicking the 'Search Password' Button a new window opens, which asks for 2 inputs. So for example you saved a password '1234' with the Username 'MyUsernameForGoogle'. If you now want to search the password you can just type 'MyUsernameForGoogle' in the Searchbar for Username and Email, press search and a list will display all of your Passwords with the Username/Email 'MyUsernameForGoogle' assigned to it. Remember the Searchbar is case-sensitive, that means that 'myusernameforgoogle' wouldn't provide any results as well as 'myusername'.\n\nNew Password:\nIf you want to search you first have to create. That's where the New Password Button comes in. When clicking it a new window opens. The first entry field is for the password you want to save. As the Warning on the Start screen says. It is recommended to use a generated password. You can easily generate one with the Generate Button. The Username/Email field is pretty self-explanatory. Just put in a Username or Email you want to associate with the password. As an example Password: '<b$W'$pfoRkL' and Username/Email: 'MyUsernameForGoogle'.\n\nThe Settings tab:\nIn the settings you can change, drum roll, your settings. You have a slider to change the length of generated passwords. 3 Switches to select what types of characters you want your generated password to contain. The appearance mode of the program. And you can also see your Authenticator QR-Code that is needed to login. And you can also see you Restoring Code. The Restoring Code should be stored savely on your computer and is used to enter the program without the Authenticator if you accidently deleted your Authenticator or lost your phone.\n\nDelete Password:\nWhen deleting a password it is important to understand how this function works. Lets say you have a database with '1234' as a password and 'Google' as a name and another with '5678' and 'Google'. When you put in Google to delete field and press `Enter` it will delete both passwords. If you only want to delete a specific password it is recommended to search for it, copy the password and put e.x. '1234' in. This will only delete '1234', 'Google' but '5678', 'Google' will stay.")
    helpTextbox.configure(state="disabled", border_spacing=4, wrap="word")
    helpTextbox.pack(fill=ctk.BOTH, expand = True)
    root.mainloop()

### GENERATE PASSWORD ###
def GenPw():
    genLength = config['length']
    characters = []
    if config['ascii_letters'] == 1:
        characters.append(string.ascii_letters)
    if config['digits'] == 1:
        characters.append(string.digits)
    if config['punctuation'] == 1:
        characters.append(string.punctuation)
    genChar = ''.join(characters)
    global resultStr
    resultStr = ''.join(random.choice(genChar) for i in range(genLength))
    newpwEntryPassword.delete(0, END)
    newpwEntryPassword.insert(0, resultStr)

### NEW PASSWORD GUI ###
def NewPw():
    global newpw
    newpw = ctk.CTk()
    newpw.title("New Password")
    newpw.geometry("500x200")
    newpw.resizable(False, False)
    newpw.grab_set()
    global newpwEntryPassword
    newpwEntryPassword = ctk.CTkEntry(master=newpw, placeholder_text="Password", width=300)
    newpwEntryPassword.pack(pady=10)
    newpwButtonGenerate = ctk.CTkButton(master=newpw, text="Generate", command=GenPw)
    newpwButtonGenerate.pack()
    global newpwEntryExtra
    newpwEntryExtra = ctk.CTkEntry(master=newpw, placeholder_text="Username or Email", width=300)
    newpwEntryExtra.pack(pady=10)

    newpwButtonSave = ctk.CTkButton(master=newpw, text="Save", command=NewDb)
    newpwButtonSave.pack()

    newpwImportant = ctk.CTkLabel(master=newpw, text="Username or Email is important for later searching in your database.\nIt is recommended to choose either of them and be consistent.")
    newpwImportant.pack()
    loginCredit = ctk.CTkLabel(master=newpw, text=f"Created by engag1ng - Version {version}")
    loginCredit.pack(side="bottom")

    def returnPressedNew(event):   	#Enter -> New Database Entry
        NewDb()
    newpw.bind('<Return>', returnPressedNew)

    newpw.mainloop()
    newpw.grab_release

### CREATE NEW DATABASE ENTRY ###
def NewDb():
    if newpwEntryPassword.get() and newpwEntryExtra.get():
        try:
            with open('data.db', 'x'):
                print("File exists")
        except FileExistsError:
            DecryptData()
        conn = sqlite3.connect('data.db')

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passes (
                password TEXT,
                extra TEXT
            )
        """)
        cursor.execute("INSERT INTO passes VALUES (:password, :extra)", {'password': newpwEntryPassword.get(), 'extra': newpwEntryExtra.get()})

        conn.commit()

        print(cursor.fetchall())

        conn.close()
        EncryptData()
        #commit_and_push(folder_path, commit_message)
        time.sleep(0.25)
        newpw.destroy()
    else:
        newpw.grab_release()
        inputError = ctk.CTk()
        inputError.grab_set()
        inputErrorLabel = ctk.CTkLabel(master=inputError, text="Please input something!")
        inputErrorLabel.pack()
        inputError.mainloop()
        def OnClosingInputError():
            inputError.grab_release()
            newpw.grab_set()
        inputError.protocol("WM_DELETE_WINDOW", OnClosingInputError)

### SEARCH PASSWORD ###
def SearchPw():
    global searchpw
    searchpw = ctk.CTk()
    searchpw.title("Search Password")
    searchpw.geometry("500x200")
    searchpw.resizable(False, False)
    searchpw.grab_set()
    global searchpwEntry
    searchpwEntry = ctk.CTkEntry(master=searchpw, placeholder_text="Search Database", width=250)
    searchpwEntry.pack(pady = 5)
    
    searchpwSearchButton = ctk.CTkButton(master=searchpw, text="Search", command=SearchDb, width=250)
    searchpwSearchButton.pack(pady=5)
    def returnPressedSearch(event):   	#Enter -> Search Database
        SearchDb()
    searchpw.bind('<Return>', returnPressedSearch)
    loginCredit = ctk.CTkLabel(master=searchpw, text=f"Created by engag1ng - Version {version}")
    loginCredit.pack(side="bottom")
    searchpw.mainloop()

### SEARCH DATABASE ###
def SearchDb():
    query = searchpwEntry.get()
    try:
        with open('data.db', 'x'):
            print("File exists")
    except FileExistsError:
        DecryptData()
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passes WHERE password LIKE (:entry) OR extra LIKE (:entry)", {'entry': query})
    conn.commit()
    results = cursor.fetchall()
    conn.close()
    EncryptData()
    searchpwOutput.configure(state="normal")
    searchpwOutput.delete("0.0", END)  # clear the previous contents of the widget
    for row in results:
        password = row[0]
        extra = row[1]
        entry_text = f"Password: {password}   |   Extra: {extra}\n"
        searchpwOutput.insert(END, entry_text)
        searchpwOutput.insert(END, "\n")
    searchpwOutput.configure(state="disabled")
    time.sleep(0.25)
    searchpw.destroy()

### DELETE PASSWORD ###
def DeletePw():
    global deletepw
    deletepw = ctk.CTk()
    deletepw.title("Delete Password")
    deletepw.geometry("500x200")
    deletepw.resizable(False, False)
    deletepw.grab_set()
    global deletepwEntry
    deletepwEntry = ctk.CTkEntry(master=deletepw, placeholder_text="Password to delete", width=250)
    deletepwEntry.pack(pady = 5)

    dpwSearchButton = ctk.CTkButton(master=deletepw, text="Delete", command=DeleteDb, width=250)
    dpwSearchButton.pack(pady = 5)
    def returnPressedDelete(event):   	#Enter -> Delete Etry
            DeleteDb()
    deletepw.bind('<Return>', returnPressedDelete)
    dpwAttention = ctk.CTkLabel(master=deletepw, text="WARNING: When deleting a password EVERYTHING that the database can find with that name WILL BE DELETED.\nFor further information look in the Help Menu.")
    dpwAttention.pack()
    loginCredit = ctk.CTkLabel(master=deletepw, text=f"Created by engag1ng - Version {version}")
    loginCredit.pack(side="bottom")
    deletepw.mainloop()

### DELETE DATABASE ###
def DeleteDb():
    query = deletepwEntry.get()
    try:
        with open('data.db', 'x'):
            print("File exists")
    except FileExistsError:
        DecryptData()
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passes WHERE password LIKE (:entry) OR extra LIKE (:entry)", {'entry': query})
    conn.commit()
    conn.close()
    EncryptData()
    time.sleep(0.25)
    deletepw.destroy()

### CREATE KEY FOR LOGIN ###
totp = pyotp.TOTP(totpkey) #Create TOTP
resultTOTP = False #Set resultTOTP to False so it doesn't skip loop

### VERIFY CODE ENTRY ###
def verifyCode():
    resultTOTP = totp.verify(loginEntry.get()) #Asks for verifaction code and verifys it
    print(resultTOTP) #prints out the result
    if resultTOTP == True or loginEntry.get() == restoreCode:
        time.sleep(0.5)
        app.destroy()
        Root()

### LOGIN SCREEN ###
app = ctk.CTk()
ctk.set_appearance_mode(config['appearance_mode'])
app.title("Login")
app.minsize(app.winfo_width(), app.winfo_height())
app.geometry("300x200")
app.resizable(False, False)
loginHeading = ctk.CTkLabel(master = app, text="Login", font=("",25), pady = 10, padx = 10)
loginHeading.pack()
loginCode = ""
loginEntry = ctk.CTkEntry(master=app, placeholder_text="Verification code")
loginEntry.pack()
loginButton = ctk.CTkButton(master=app, text="Login", command=verifyCode)
loginButton.pack()
loginCredit = ctk.CTkLabel(master=app, text=f"Created by engag1ng - Version {version}")
loginCredit.pack(side="bottom")
def returnPressed(event):   	#Enter -> Login
    verifyCode()
app.bind('<Return>', returnPressed)
def onClose():
    CommitAndPush(folderPath, commitMessage)
    time.sleep(0.25)
#app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()