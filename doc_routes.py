import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from models.model import User, Document, CollectionDocRelation
from schemas import schemas
from database.database import get_db
from auth.jwt import get_current_active_user
from vector.collection import create_collection
from vector.vectorization import add_to_vectordb
from loggings.logging_config import setup_logging
from database.q_client import client
from typing import List
import pandas as pd
import shutil
import os

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create an APIRouter instance for document-related routes
doc_router = APIRouter(prefix="/documents", tags=["docs"])

UPLOAD_DIRECTORY = "uploaded_files"
SUPPORTED_EXTENTIONS = ['.pdf', '.csv', '.xlsx', 'xls']

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Endpoint to upload a document
@doc_router.post("/upload", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a document (PDF, Excel, CSV).
    
    - **file**: The file to upload.
    """
    try:
        file_extension = os.path.splitext(file.filename)[1]  # Extract file extension
        logging.info(f"User {current_user.id} is uploading a file: {file.filename}")

        # Validate supported file extension
        if file_extension in SUPPORTED_EXTENTIONS:
            name = os.path.splitext(file.filename)[0]

            # Check if the file already exists in the user's documents
            existing_document = db.query(Document).filter(
                Document.user_id == current_user.id,
                Document.file_name == name
            ).first()

            if existing_document:
                logging.warning(f"File with the same name already exists for user {current_user.id}.")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="File with the same name already exists."
                )

            file_with_extension = f"{name}{file_extension}"
            file_path = os.path.join(UPLOAD_DIRECTORY, file_with_extension)

            # Save the file to the server
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Create a new document record in the database
            new_document = Document(
                user_id=current_user.id,
                file_name=name,
                file_type=file_extension,
                file_path=file_path
            )

            # Add the new document to the session and commit
            db.add(new_document)
            db.commit()
            db.refresh(new_document)

            logging.info(f"Document {new_document.id} uploaded successfully for user {current_user.id}")

            # Create a new document collection in the vectorDB and add the vector
            data = extract_document_content(file_path, file_extension)
            doc_id = new_document.id
            collection = create_collection(docid=doc_id)
            add_to_vectordb(collection=collection, data=data)

            # Add the new collection and its corresponding doc id to the database
            new_data = CollectionDocRelation(
                collection_name=collection,
                doc_id=doc_id,
            )
            db.add(new_data)
            db.commit()
            db.refresh(new_data)

            return new_document
        else:
            logging.error(f"Unsupported file type: {file_extension} for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported document type. Only PDF, Excel, and CSV are supported."
            )

    # except Exception as e:
    #     logging.error(f"Error occurred while uploading document for user {current_user.id}: {str(e)}")
    #     raise HTTPException(
    #         status_code=e.status_code,
    #         detail=f"An error occurred while uploading the document: {str(e)}"
    #     ) from e
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error occurred while uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while uploading the document: {str(e)}"
    )


# Endpoint to list uploaded documents
@doc_router.get("/", response_model=List[schemas.DocumentResponse])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a list of uploaded documents.
    """
    try:
        logging.info(f"Fetching documents for user {current_user.id}")
        documents = db.query(Document).filter(Document.user_id == current_user.id).all()
        return documents
    except Exception as e:
        logging.error(f"Error occurred while fetching documents for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving documents.") from e

# Endpoint to delete a document
@doc_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an uploaded document.
    
    - **document_id**: The ID of the document to delete.
    """
    try:
        logging.info(f"User {current_user.id} is attempting to delete document {document_id}")

        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()

        if not document:
            logging.warning(f"Document {document_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Document not found.")

        collection_row = db.query(CollectionDocRelation).filter(CollectionDocRelation.doc_id == document_id).first()

        if collection_row is None:
            # If no collection found, log it and handle the case
            logging.warning(f"No collection found for document {document_id}")
            raise HTTPException(status_code=404, detail="Collection not found for this document.")
    
        # Remove the file from the server
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
            logging.info(f"File {document.file_path} deleted from the server.")

        # Delete the record from the database
        db.delete(document)
        db.commit()
        logging.info(f"Document {document_id} deleted from the database.")

        # Delete the vector record of the document from the vector DB
        collection_name = collection_row.collection_name
        client.delete_collection(collection_name)
        logging.info(f"Collection {collection_name} deleted from vector DB.")

    except Exception as e:
        logging.error(f"Error occurred while deleting document {document_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=f"An error occurred while deleting the document. {str(e)}") from e


# Helper function to extract document content
def extract_document_content(file_path, extension) -> str:
    """
    Extract content from the document based on the file type (e.g., PDF, Excel, CSV).
    Returns a string with extracted content.
    """
    try:
        logging.info(f"Extracting content from file {file_path} with extension {extension}")

        if extension == ".pdf":
            return extract_pdf_content(file_path)
        elif extension == ".xlsx" or extension == ".xls":
            return extract_excel_content(file_path)
        elif extension == ".csv":
            return extract_csv_content(file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported document type. Only PDF, Excel, and CSV are supported."
            )

    except Exception as e:
        logging.error(f"Error occurred while extracting document content from {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while extracting document content: {str(e)}"
        )

# Example function to extract PDF content
def extract_pdf_content(file_path: str) -> str:
    from PyPDF2 import PdfReader
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        logging.error(f"Error extracting PDF content from {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while extracting PDF content: {str(e)}"
        )

# Example function to extract Excel content (using pandas)
def extract_excel_content(file_path: str) -> str:
    try:
        df = pd.read_excel(file_path)
        return df.to_string()  # Return the content as a string (could also be formatted)
    except Exception as e:
        logging.error(f"Error extracting Excel content from {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while extracting Excel content: {str(e)}"
        )

# Example function to extract CSV content
def extract_csv_content(file_path: str) -> str:
    try:
        df = pd.read_csv(file_path)
        return df.to_string()  # Return the content as a string (could also be formatted)
    except Exception as e:
        logging.error(f"Error extracting CSV content from {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while extracting CSV content: {str(e)}"
        )
