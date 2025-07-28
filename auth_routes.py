from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.model import User
from schemas.schemas import UserResponse, UserCreate, LoginCreate
from auth.jwt import create_access_token, get_password_hash, authenticate_user, get_current_user
from database.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from loggings.logging_config import setup_logging
import logging

# Initialize the logging setup
setup_logging()
logger = logging.getLogger(__name__)

# Create an APIRouter instance for authentication routes
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Log incoming registration request
    logging.info(f"Registering user with email: {user.email}")
    
    # Basic validation for invalid inputs
    if user.username == "string" or user.email == "string" or user.password == "string":
        logging.warning(f"Invalid registration attempt for email: {user.email} - Invalid credentials")
        raise HTTPException(status_code=400, detail="Enter valid credentials")
    if user.username == "" or user.email == "" or user.password == "":
        logging.warning(f"Invalid registration attempt for email: {user.email} - Empty fields")
        raise HTTPException(status_code=400, detail="Enter valid credentials")
    
    # Check if email is already registered
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logging.warning(f"Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password and save the new user to the database
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, 
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Log successful registration
    logging.info(f"User registered successfully: {user.email}")
    
    return db_user

@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Log login attempt
    logging.info(f"Login attempt for user: {form_data.username}")
    
    # Authenticate user credentials
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logging.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.username})

    # Log successful login
    logging.info(f"User {form_data.username} logged in successfully.")
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    # Log profile access
    logging.info(f"Profile accessed for user: {current_user.email}")
    
    return current_user
