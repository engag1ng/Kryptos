import pyotp
import sys
import subprocess
import os

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'customtkinter'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'pyotp'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'qrcode'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'cryptography'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'pyinstaller'])

id = pyotp.random_base32() #Generate new TOTP Key
with open('KeyPass.py', 'a') as keypass:
    line_to_replace = 11 #the line we want to remplace
    my_file = 'KeyPass.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = "totpkey='"+id+"'"+'\n'

    with open(my_file, 'w') as file:
        file.writelines( lines )

restore_code = pyotp.random_base32()
with open('KeyPass.py', 'a') as restore:
    line_to_replace = 12 #the line we want to remplace
    my_file = 'KeyPass.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = "restore_code='"+restore_code+"'"+'\n'

    with open(my_file, 'w') as file:
        file.writelines( lines )

def get_user():
    return os.getenv('USER', os.getenv('USERNAME', 'user'))
username = str(get_user())
print(username)

subprocess.run(f'pyinstaller --noconfirm --onedir --windowed --icon=keypassicon.ico --add-data "C:/Users/{username}/AppData/Local/Programs/Python/Python311/Lib/site-packages/customtkinter;customtkinter/" KeyPass.py')
os.remove('KeyPass.py')