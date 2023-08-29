import sys
import subprocess
import os
import time
from random import randint
from cryptography.fernet import Fernet
import requests

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'customtkinter'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyotp'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'qrcode'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'cryptography'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pillow'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])

time.sleep(2)
import pyotp
id = pyotp.random_base32() #Generate new TOTP Key
with open('KeyForU.py', 'a') as keypass:
    line_to_replace = 13 #the line we want to remplace
    my_file = 'KeyForU.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = "totpkey='"+id+"'\n"

    with open(my_file, 'w') as file:
        file.writelines( lines )

restore_code = pyotp.random_base32()
with open('KeyForU.py', 'a') as restore:
    line_to_replace = 14 #the line we want to remplace
    my_file = 'KeyForU.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = f"restore_code='{restore_code}'\n"

    with open(my_file, 'w') as file:
        file.writelines( lines )

image_code = randint(0,99)
with open('KeyForU.py', 'a') as restore:
    line_to_replace = 15 #the line we want to remplace
    my_file = 'KeyForU.py'

    with open(my_file, 'r') as file:
        lines = file.readlines()

    if len(lines) > int(line_to_replace):
        lines[line_to_replace] = f"image_code={image_code}\n"

    with open(my_file, 'w') as file:
        file.writelines( lines )

file_code = Fernet.generate_key()
with open('KeyForU.py', 'a') as restore:
    line_to_replace = 16 #the line we want to remplace
    my_file = 'KeyForU.py'

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
# GitHub access token with repo scope
GitHubCheck = input("Do you want to backup your password manager to GitHub? Yes/No ")
if GitHubCheck == "Yes" or GitHubCheck == "yes":
    access_token = input("Please enter GitHub access token (Found under Settings->Developer Settings->Personal access tokens->Generate a personal access token) ")
    GitHubUsername = input("Whats your GitHub Username? ")
else:
    print("Continueing...")

subprocess.run(f'PyInstaller --noconfirm --onedir --windowed --add-data "{customtkinter}\customtkinter;customtkinter" --icon=keyforuicon.ico KeyForU.py')
#os.remove('KeyForU.py')

### GITHUB BACKUP
def create_repository(folder_name):
    # API endpoint for creating a repository
    url = "https://api.github.com/user/repos"

    # Headers for the API request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Request payload for creating the repository
    data = {
        "name": folder_name,
        "private": True
    }

    # Send the API request to create the repository
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Repository '{folder_name}' created successfully on GitHub.")
    else:
        print(f"Failed to create repository. Status code: {response.status_code}")
        print(response.text)


def commit_and_push(folder_path, commit_message):
    os.chdir(folder_path)

    subprocess.run(["git", "add", "."])

    subprocess.run(["git", "commit", "-m", commit_message])

    subprocess.run(["git", "push", "-u", "origin", "master"])

folder_path = os.getcwd()

folder_name = os.path.basename(folder_path)

if not os.path.exists(os.path.join(folder_path, ".git")):
    create_repository(folder_name)

    subprocess.run(["git", "init"], cwd=folder_path)

    remote_url = f"https://github.com/{GitHubUsername}/{folder_name}.git"
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=folder_path)

commit_message = "Automatic commit"

commit_and_push(folder_path, commit_message)
print("Changes committed and pushed to GitHub.")
input()