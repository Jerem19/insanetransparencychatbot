import os, glob, pickle, faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Important : mets bien ./pdfs car tu copies dans ce dossier via Dockerfile
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
for pdf_path in glob.glob(os.path.join(PDF_DIR, "*.pdf")):
    txt = pdf_to_text(pdf_path)
    if not txt.strip():
        print(f"⚠️ Aucun texte trouvé dans {os.path.basename(pdf_path)}")
        continue
    for c in chunk(txt):
        chunks.append(c)
        metas.append({"source": os.path.basename(pdf_path)})

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

# 4. Sauvegarde
with open(STORE_FILE, "wb") as f:
    pickle.dump({"chunks": chunks, "metas": metas}, f)

print(f"✅ {len(chunks)} passages indexés depuis {len(metas)} fichiers.")
