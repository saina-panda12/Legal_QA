import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import model
from schemas import schemas
from database.database import get_db
from auth.jwt import get_current_active_user
# from llms.response_model2 import model
from vector.vectorization import get_response
import datetime
from typing import List
from loggings.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create an APIRouter instance for chat routes
chat_router = APIRouter(prefix="/chat", tags=["chat"])


# Function to store the chat history
def store_chat_history(db: Session, user_id: int, document_id: int, message: str, response: str):
    try:
        chat_history = model.ChatHistory(
            user_id=user_id,
            document_id=document_id,
            message=message,
            response=response,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)
        logging.info(f"Stored chat history for document ID: {document_id} and user ID: {user_id}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error while saving chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving chat history: {str(e)}"
        )

# Endpoint to chat with the document
@chat_router.post("/", response_model=schemas.ChatResponse)
async def chat_with_document(
    chat_message: schemas.ChatMessage,  # Accepting the ChatMessage schema here
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_active_user)
):
    """
    Chat with a document's content using a Gemini model.
    
    - **document_id**: The ID of the document to chat with.
    - **message**: The user’s message to interact with the document.
    """
    try:
        logging.info(f"User {current_user.id} is attempting to chat with document ID: {chat_message.document_id}")
        
        # Fetch the document from the database
        document = db.query(model.Document).filter(
            model.Document.id == chat_message.document_id,
            model.Document.user_id == current_user.id
        ).first()

        if not document:
            logging.warning(f"Document ID {chat_message.document_id} not found or does not belong to user ID {current_user.id}.")
            raise HTTPException(status_code=404, detail="Document not found.")
        
        # Attempt to retrieve collection information
        try:
            collection_row = db.query(model.CollectionDocRelation).filter(model.CollectionDocRelation.doc_id == chat_message.document_id).first()
            collection = collection_row.collection_name
        except Exception as e:
            logging.error(f"Error retrieving collection for document ID: {chat_message.document_id}. {str(e)}")
            raise HTTPException(status_code=404, detail=f"An error occurred while retrieving the collection: {str(e)}")
        
        # Get the response from the Gemini model
        response = get_response(query=chat_message.message, collection=collection)
        result = response['result']
        
        # Store chat history
        store_chat_history(db, current_user.id, chat_message.document_id, chat_message.message, result)
        
        # Log successful chat interaction
        logging.info(f"Successfully generated response for document ID: {chat_message.document_id}")

        # Return the chat response
        return schemas.ChatResponse(
            id=chat_message.document_id,
            user_id=current_user.id,
            document_id=chat_message.document_id,
            message=chat_message.message,
            response=result,
            timestamp=datetime.datetime.utcnow()
        )
    
    # except Exception as e:
    #     logging.error(f"Error occurred while chatting with document ID: {chat_message.document_id}. {str(e)}")
    #     raise HTTPException(
    #         status_code=e.status_code,
    #         detail=f"An error occurred while chatting with the document: {str(e)}"
    #     ) from e
    except HTTPException as e:
        # Handle HTTPException specifically
        logging.error(f"HTTP error occurred while chatting with document ID: {chat_message.document_id}. {str(e)}")
        raise e 

# Endpoint to get chat history for a specific document
@chat_router.get("/history/{document_id}", response_model=List[schemas.ChatResponse])
async def get_chat_history(
    document_id: int,  # The document ID whose chat history we want to fetch
    db: Session = Depends(get_db),  # Database session
    current_user: model.User = Depends(get_current_active_user)  # Current authenticated user
):
    """
    Get the chat history for a specific document uploaded by the authenticated user.
    
    - **document_id**: The ID of the document whose chat history we want to fetch.
    """
    try:
        logging.info(f"Fetching chat history for document ID: {document_id} by user ID: {current_user.id}")
        
        # Fetch the document from the database to ensure it belongs to the authenticated user
        document = db.query(model.Document).filter(
            model.Document.id == document_id,
            model.Document.user_id == current_user.id
        ).first()

        if not document:
            logging.warning(f"Document ID {document_id} not found or does not belong to user ID {current_user.id}.")
            raise HTTPException(status_code=404, detail="Document not found or does not belong to the authenticated user.")
        
        # Fetch the chat history related to the document
        chat_histories = db.query(model.ChatHistory).filter(
            model.ChatHistory.document_id == document_id,
            model.ChatHistory.user_id == current_user.id
        ).all()

        if not chat_histories:
            logging.warning(f"No chat history found for document ID: {document_id}")
            raise HTTPException(status_code=404, detail="No chat history found for this document.")

        # Return the chat history
        logging.info(f"Successfully retrieved chat history for document ID: {document_id}")
        return chat_histories

    except Exception as e:
        logging.error(f"Error retrieving chat history for document ID: {document_id}. {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail=f"An error occurred while retrieving the chat history: {str(e)}"
        )
