from fastapi import FastAPI
from routes.auth_routes import auth_router
from routes.doc_routes import doc_router
from routes.chat_routes import chat_router
from models import model
from database.database import engine
import logging
from loggings.logging_config import setup_logging

# Initialize the logging setup
setup_logging()
logger = logging.getLogger(__name__)

# Create the database tables based on the models
model.Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI()

# Include the routers for different routes
app.include_router(auth_router)  # Authentication routes 
app.include_router(doc_router)   # Document-related routes 
app.include_router(chat_router)  # Chat-related routes   

@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    logging.info("Root endpoint accessed.")  # Log when the root endpoint is accessed
    return {"message": "Welcome to the RAG"}

