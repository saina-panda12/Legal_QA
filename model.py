from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to Document (Cascading delete)
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    # Relationship to ChatHistory (Cascading delete)
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String)
    file_type = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to User
    user = relationship("User", back_populates="documents")

    # Relationship to ChatHistory (Cascading delete)
    chat_histories = relationship("ChatHistory", back_populates="document", cascade="all, delete-orphan")

    # Relationship to CollectionDocRelation (Cascading delete)
    collection_doc_relations = relationship("CollectionDocRelation", back_populates="document", cascade="all, delete-orphan")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    message = Column(String)
    response = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to User
    user = relationship("User", back_populates="chat_histories")

    # Relationship to Document
    document = relationship("Document", back_populates="chat_histories")


class CollectionDocRelation(Base):
    __tablename__ = "col_doc_relation"
    id = Column(Integer, primary_key=True, index=True)
    collection_name = Column(String, unique=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), unique=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to Document
    document = relationship("Document", back_populates="collection_doc_relations")



