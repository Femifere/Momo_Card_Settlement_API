import json
import os
from dotenv import load_dotenv


# Specify the path to the .env file
dotenv_path = "myenv/.env"

# Load environment variables from the specified .env file
load_dotenv(dotenv_path)

# Users file path
USERS_FILE = os.getenv("USERS_FILE", "data/users.json")


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
