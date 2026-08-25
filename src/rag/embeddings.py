# from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse
from langchain_ollama import OllamaEmbeddings

from dotenv import load_dotenv

load_dotenv()

sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

# dense_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

dense_embeddings = OllamaEmbeddings(model="embeddinggemma")