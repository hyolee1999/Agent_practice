# from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import FastEmbedEmbeddings


from dotenv import load_dotenv
import os

load_dotenv()

# OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

# OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

# dense_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# dense_embeddings = OllamaEmbeddings(
#     model="embeddinggemma", 
#     base_url = OLLAMA_BASE_URL,
#     client_kwargs={
#         "headers": {
#             "Authorization":
#                 f"Bearer {OLLAMA_API_KEY}"
#         }
#     })


dense_embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)