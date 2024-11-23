import os
import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from api.shared import load_users
from dotenv import load_dotenv
import logging

# Specify the path to the .env file
dotenv_path = "myenv/.env"

# Load environment variables from the specified .env file
load_dotenv(dotenv_path)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fetch the SECRET_KEY from the environment
SECRET_KEY = os.getenv("SECRET_KEY")
logging.info(f"This is the Secret Key: {SECRET_KEY}")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables.")

# Create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Verify token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}
        )

# Authenticate user
def authenticate_user(username: str, password: str):
    users = load_users()
    if username in users and pwd_context.verify(password, users[username]["password"]):
        return {"username": username}
    return None
