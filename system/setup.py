import sys
import subprocess
import os
import time
from random import randint
from cryptography.fernet import Fernet

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'customtkinter'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyotp'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'qrcode'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'cryptography'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pillow'])

time.sleep(2)
import pyotp
id = pyotp.random_base32() #Generate new TOTP Key
with open('KeyPass.py', 'a') as keypass:
    line_to_replace = 13 #the line we want to remplace
    my_file = 'KeyPass.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = "totpkey='"+id+"'"+'\n'

    with open(my_file, 'w') as file:
        file.writelines( lines )

restore_code = pyotp.random_base32()
with open('KeyPass.py', 'a') as restore:
    line_to_replace = 14 #the line we want to remplace
    my_file = 'KeyPass.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = f"restore_code='{restore_code}'\n"

    with open(my_file, 'w') as file:
        file.writelines( lines )

image_code = randint(0,99)
with open('KeyPass.py', 'a') as restore:
    line_to_replace = 15 #the line we want to remplace
    my_file = 'KeyPass.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = f"image_code={image_code}\n"

    with open(my_file, 'w') as file:
        file.writelines( lines )

file_code = Fernet.generate_key()
with open('KeyPass.py', 'a') as restore:
    line_to_replace = 16 #the line we want to remplace
    my_file = 'KeyPass.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = f"fernetkey={file_code}\n"

    with open(my_file, 'w') as file:
        file.writelines( lines )

def get_user():
    return os.getenv('USER', os.getenv('USERNAME', 'user'))
username = str(get_user())

subprocess.check_call([sys.executable, '-m', 'pip', 'show', 'customtkinter'])
customtkinter = input("Please input the Location shown above:\n")

subprocess.run(f'PyInstaller --noconfirm --onedir --windowed --add-data "{customtkinter}\customtkinter;customtkinter" --icon=keypassicon.ico KeyPass.py')
os.remove('KeyPass.py')