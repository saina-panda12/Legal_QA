from qdrant_client.models import Distance, VectorParams
from database.q_client import client


# create a collection
vectors_config = VectorParams(  #"bge-large-en" has a dimension of 1024
    size=768,                   #"bge-small-en" has a dimension of 384 
    distance=Distance.COSINE)   #"bge-base-en" has a dimension of 768


def create_collection(docid):
    collection_name = f"collection{docid}"
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
        )
    return collection_name