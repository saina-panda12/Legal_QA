# from langchain_core.embeddings import Embeddings
# from transformers import AutoTokenizer, AutoModel
# import torch

# class InLegalBERTEmbedding(Embeddings):  # ✅ Subclass LangChain's Embeddings interface
#     def __init__(self, model_name="law-ai/InLegalBERT"):
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.model = AutoModel.from_pretrained(model_name)

#     def embed_documents(self, texts):
#         """Create embeddings for a list of documents"""
#         return [self.embed_query(text) for text in texts]

#     def embed_query(self, text):
#         """Create embedding for a query"""
#         inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
#         with torch.no_grad():
#             outputs = self.model(**inputs)
        
#         # Use the [CLS] token embedding
#         embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
#         return embeddings[0].tolist()


# embedding_model = InLegalBERTEmbedding()


from langchain_huggingface import HuggingFaceEmbeddings

# # load the BGE embedding model 
# # model_name = "BAAI/bge-base-en"
# # model_kwargs = {'device':'cpu'}
# # encode_kwargs = {'normalize_embeddings':False}
# # embedding_model = HuggingFaceEmbeddings(
# #     model_name=model_name,
# #     model_kwargs=model_kwargs,
# #     encode_kwargs=encode_kwargs
# # )


embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")