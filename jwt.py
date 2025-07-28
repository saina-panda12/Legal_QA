from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import model
from schemas import schemas
from database.database import get_db
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Secret key and algorithm used for encoding and decoding JWTs
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Default expiration time for access tokens

# Password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Function to verify if a plain password matches a hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash a password
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to create a new JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create an access token with an expiration time.
    - If expires_delta is provided, it will use that expiration time.
    - Otherwise, it will use the default expiration time (30 minutes).
    """
    to_encode = data.copy()  # Make a copy of the data dictionary
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # Use provided expiration time
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Default expiration time (30 minutes)
    
    to_encode.update({"exp": expire})  # Add expiration timestamp to the payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode the token using the secret key and algorithm
    return encoded_jwt

# Function to get a user from the database by username
def get_user(db: Session, username: str):
    """
    Query the database to find a user by their username.
    """
    return db.query(model.User).filter(model.User.username == username).first()

# Function to authenticate a user by verifying the password
def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user by checking the username and the password.
    Returns the user if successful, otherwise False.
    """
    user = get_user(db, username)  # Fetch the user from the database
    if not user:  # If the user doesn't exist, authentication fails
        return False
    if not verify_password(password, user.hashed_password):  # Verify the provided password with the stored hashed password
        return False
    return user  # If authentication is successful, return the user

# Function to get the current user from the JWT token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Get the current authenticated user by decoding the JWT token.
    If the token is invalid or the user is not found, raise an HTTP 401 Unauthorized error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token to extract the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # Get the "sub" field from the payload (which is the username)
        if username is None:  # If the username is missing from the token, raise an exception
            raise credentials_exception
    except JWTError:
        raise credentials_exception  # If JWT decoding fails, raise an exception
    
    user = get_user(db, username)  # Fetch the user from the database using the username
    if user is None:  # If the user doesn't exist, raise an exception
        raise credentials_exception
    
    return user  # Return the authenticated user

# Function to get the current active user (ensures the user is authenticated)
def get_current_active_user(current_user: model.User = Depends(get_current_user)):
    """
    Ensure the user is authenticated and active.
    If the user is not authenticated, raise an HTTP 401 Unauthorized error.
    """
    if current_user is None:  # If the current user is not found, raise an exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user  # Return the current active user
