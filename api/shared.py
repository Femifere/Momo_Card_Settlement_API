import json
import os

USERS_FILE = r"data/users.json"

def initialize_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as file:
            json.dump({}, file)

initialize_users_file()

def load_users():
    with open(USERS_FILE, "r") as file:
        return json.load(file)

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)
