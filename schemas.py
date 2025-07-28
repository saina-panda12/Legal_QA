from pydantic import BaseModel, EmailStr
from typing_extensions import TypedDict
from typing import Annotated
import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class DocumentUpload(BaseModel):
    file_name: str
    file_type: str

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    uploaded_at: datetime.datetime

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    document_id: int
    message: str

class ChatResponse(BaseModel):
    id: int
    user_id: int
    document_id: int
    message: str
    response: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class SQLQuery(BaseModel):
    query: str

class SQLQueryResponse(BaseModel):
    id: int
    user_id: int
    query: str
    response: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


# Define the State class using TypedDict to structure the expected data
class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

# Define the QueryOutput class for the SQL query result
class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]