import os, pickle, faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Dossier racine contenant les sous-dossiers par commune
PDF_DIR        = "./pdfs"
INDEX_FILE     = "faiss.index"
STORE_FILE     = "faiss_store.pkl"
CHUNK_SIZE     = 1024
CHUNK_OVERLAP  = 128

def pdf_to_text(path):
    reader = PdfReader(path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def chunk(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    start = 0
    while start < len(text):
        end = start + size
        yield text[start:end]
        start += size - overlap

# 1. Extraction + chunking
chunks, metas = [], []
for dirpath, _, files in os.walk(PDF_DIR):
    commune = os.path.basename(dirpath).lower()
    for filename in files:
        if not filename.endswith(".pdf"):
            continue
        pdf_path = os.path.join(dirpath, filename)
        text = pdf_to_text(pdf_path)
        if not text.strip():
            print(f"⚠️ Aucun texte trouvé dans {filename}")
            continue
        for c in chunk(text):
            chunks.append(c)
            metas.append({
                "source": filename,
                "commune": commune
            })

# 2. Embeddings
print("🔎 Génération des embeddings...")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
emb = embedder.encode(chunks, show_progress_bar=True, batch_size=64)

# 3. Indexation FAISS
print("📦 Création de l’index FAISS...")
dim = emb.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(emb.astype("float32"))
faiss.write_index(index, INDEX_FILE)

# 4. Sauvegarde des chunks + métadonnées
with open(STORE_FILE, "wb") as f:
    pickle.dump({"chunks": chunks, "metas": metas}, f)

print(f"✅ {len(chunks)} passages indexés depuis {len(metas)} fichiers.")
