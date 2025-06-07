import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import mysql.connector
import requests
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_ENDPOINT = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"
import pickle, faiss, numpy as np
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)

# Clé secrète pour les sessions (en prod, utilise une vraie valeur stockée en variable d'env)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "valais_db")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "apppassword")

# ───── Assets RAG (PDFs) ──────────────────────────────────────────
EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Les fichiers ont été créés par ingest_pdfs.py
INDEX_FILE = "faiss.index"
STORE_FILE = "faiss_store.pkl"

FAISS_INDEX = faiss.read_index(INDEX_FILE)
with open(STORE_FILE, "rb") as f:
    _store = pickle.load(f)

CHUNKS = _store["chunks"]          # liste de str
METAS  = _store["metas"]           # liste de dicts (-> nom du PDF)

def retrieve_chunks(query: str, k: int = 4):
    """Retourne les k passages les + proches du query."""
    q_emb = EMBED_MODEL.encode([query]).astype("float32")
    _, I  = FAISS_INDEX.search(q_emb, k)
    return [CHUNKS[i] for i in I[0]]



def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4'
    )

@app.route("/api/public/cities", methods=["GET"])
def list_cities():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT DISTINCT c.id, c.name, c.latitude, c.longitude
        FROM cities c
        LEFT JOIN city_themes ct ON ct.city_id = c.id
        ORDER BY c.name;
    """
    cursor.execute(query)
    villes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(villes)


# --- CRUD for Cities ---
@app.route("/api/cities", methods=["GET", "POST"])
def cities():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "GET":
        cursor.execute("SELECT * FROM cities ORDER BY name;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    elif request.method == "POST":
        try:
            data = request.get_json()
            # Validate latitude and longitude
            try:
                latitude = float(data["latitude"])
                longitude = float(data["longitude"])
            except (ValueError, TypeError, KeyError):
                cursor.close()
                conn.close()
                return jsonify({"success": False, "error": "Latitude and longitude must be valid numbers."}), 400

            name = data.get("name")
            if not name:
                cursor.close()
                conn.close()
                return jsonify({"success": False, "error": "Name is required."}), 400

            cursor.execute(
                "INSERT INTO cities (latitude, longitude, name) VALUES (%s, %s, %s)",
                (latitude, longitude, name),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True}), 201
        except Exception as e:
            print("Error in POST /api/cities:", e)
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/cities/<int:city_id>", methods=["PUT", "DELETE"])
def city_detail(city_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "PUT":
        try:
            data = request.get_json()
            cursor.execute(
                "UPDATE cities SET name=%s, latitude=%s, longitude=%s WHERE id=%s",
                (data["name"], data["latitude"], data["longitude"], city_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            print("Error in PUT /api/cities:", e)
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": str(e)}), 500
    elif request.method == "DELETE":
        cursor.execute("DELETE FROM cities WHERE id=%s", (city_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})

# --- CRUD for Themes ---
@app.route("/api/themes", methods=["GET", "POST"])
def themes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "GET":
        cursor.execute("SELECT * FROM themes ORDER BY name;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    elif request.method == "POST":
        data = request.get_json()
        cursor.execute("INSERT INTO themes (name) VALUES (%s)", (data["name"],))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201

@app.route("/api/themes/<int:theme_id>", methods=["PUT", "DELETE"])
def theme_detail(theme_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "PUT":
        data = request.get_json()
        cursor.execute("UPDATE themes SET name=%s WHERE id=%s", (data["name"], theme_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    elif request.method == "DELETE":
        cursor.execute("DELETE FROM themes WHERE id=%s", (theme_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})

# --- CRUD for City_Themes ---
@app.route("/api/city_themes", methods=["GET", "POST"])
def city_themes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "GET":
        cursor.execute("SELECT * FROM city_themes;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    elif request.method == "POST":
        data = request.get_json()
        cursor.execute(
            "INSERT INTO city_themes (city_id, theme_id) VALUES (%s, %s)",
            (data["city_id"], data["theme_id"]),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201

@app.route("/api/city_themes/<int:city_id>/<int:theme_id>", methods=["DELETE"])
def city_theme_detail(city_id, theme_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "DELETE FROM city_themes WHERE city_id=%s AND theme_id=%s", (city_id, theme_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# --- CRUD for Contents ---
@app.route("/api/contents", methods=["GET", "POST"])
def contents():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "GET":
        cursor.execute("SELECT * FROM contents;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    elif request.method == "POST":
        data = request.get_json()
        cursor.execute(
            "INSERT INTO contents (theme_id, title, url) VALUES (%s, %s, %s)",
            (data["theme_id"], data["title"], data["url"]),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201

@app.route("/api/contents/<int:content_id>", methods=["PUT", "DELETE"])
def content_detail(content_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "PUT":
        data = request.get_json()
        cursor.execute(
            "UPDATE contents SET theme_id=%s, title=%s, url=%s WHERE id=%s",
            (data["theme_id"], data["title"], data["url"], content_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    elif request.method == "DELETE":
        cursor.execute("DELETE FROM contents WHERE id=%s", (content_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})

# --- Existing endpoints for public API ---
@app.route("/api/themes/<int:city_id>", methods=["GET"])
def themes_par_ville(city_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query_themes = """
        SELECT t.id AS theme_id, t.name AS theme_name
        FROM themes t
        JOIN city_themes ct ON ct.theme_id = t.id
        WHERE ct.city_id = %s;
    """
    cursor.execute(query_themes, (city_id,))
    themes = cursor.fetchall()
    for theme in themes:
        q2 = """
            SELECT id AS content_id, title, url
            FROM contents
            WHERE theme_id = %s;
        """
        cursor.execute(q2, (theme["theme_id"],))
        theme["contents"] = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(themes)

@app.route("/api/contents/<int:content_id>", methods=["GET"])
def get_content(content_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, title, url FROM contents WHERE id = %s;"
    cursor.execute(query, (content_id,))
    content = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(content) if content else ("Not found", 404)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    # Contrôle basique (à remplacer par un vrai mécanisme utilisateur)
    if username == "admin" and password == "admin123":
        session['user'] = username
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Identifiants invalides"}), 401

chat_history = []

@app.route("/api/chat", methods=["POST"])
def chat_with_gemma():
    user_input = request.json.get("message")

    chat_history.append({"role": "user", "content": user_input})
    response = requests.post(
        OLLAMA_ENDPOINT,
        json={
@app.route("/api/query", methods=["POST"])
def query_rag():
    try:
        user_input = request.json.get("message", "")
        passages = retrieve_chunks(user_input, k=4)
        if not passages:
            return jsonify({"response": "Je n’ai rien trouvé dans les documents."})

        context = "\n\n".join(passages)

        system_prompt = (
            "Tu es un assistant juridique valaisan. "
            "Réponds UNIQUEMENT avec les informations fournies. "
            "Si tu ne sais pas, dis « Je ne sais pas ».\n\n"
            f"CONTEXTE :\n{context}"
        )

        payload = {
            "model": "gemma3:12b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            "stream": False
        }

        ollama_url = "http://host.docker.internal:11434/api/chat"
        resp = requests.post(ollama_url, json=payload)
        resp.raise_for_status()
        answer = resp.json()["message"]["content"]
        return jsonify({"response": answer})

    except Exception as e:
        print("💥 ERREUR DANS /api/query :", e)
        return jsonify({"response": "Erreur interne avec le chatbot."}), 500


# @app.route("/api/chat", methods=["POST"])
# def chat_with_gemma():
#     user_input = request.json.get("message")

#     chat_history.append({"role": "user", "content": user_input})
#     response = requests.post(
#         "http://host.docker.internal:11434/api/chat",
#         json={
#             "model": "gemma3:12b",
#             "messages": chat_history,
#             "stream": False
#         }
#     )

#     reply = response.json()["message"]["content"]
#     chat_history.append({"role": "assistant", "content": reply})
#     return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)