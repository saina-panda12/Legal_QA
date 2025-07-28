from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain.chains import RetrievalQA
from database.q_client import client
from llms.embedding_model import embedding_model
from llms.response_model2 import model

# add documents to vector store
def get_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 512,
        chunk_overlap = 50,
        separators=["\n\n", "\n"],
    )
    chunks = text_splitter.split_text(text=text)
    return chunks

def add_to_vectordb(collection: str, data: str):
    vector_store = QdrantVectorStore(
        client=client,
        collection_name= collection,
        embedding=embedding_model,

    )
    text = get_chunks(data)
    vector_store.add_texts(text)

def get_response(query: str, collection: str):
    vector_store = QdrantVectorStore(
        client=client,
        collection_name= collection,
        embedding=embedding_model,

    )
    qa = RetrievalQA.from_chain_type(
        llm=model,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )
    prompt = f"""
        You are a legal QA chatbot specialized in indian legal system. Answer the question based on the provided context with is related to Indian legal system. If the context contains relevant information, provide a concise and accurate response. If the question is out of context then say "Out of the context question. Please ask relevant question.". Dont use external information to answer the question.

        Question: {query}
    """
    response = qa.invoke(prompt)
    return response