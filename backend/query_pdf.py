# query_pdf.py
import pickle, faiss
from sentence_transformers import SentenceTransformer
from typing import List

CHUNK_PATH = "faiss_store.pkl"
INDEX_PATH = "faiss.index"

# Charger index et store
with open(CHUNK_PATH, "rb") as f:
    store = pickle.load(f)

chunks = store["chunks"]
metas = store["metas"]

index = faiss.read_index(INDEX_PATH)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def search_similar_chunks(query: str, top_k: int = 5) -> List[str]:
    emb = model.encode([query])
    D, I = index.search(emb, top_k)
    return [chunks[i] for i in I[0]]
