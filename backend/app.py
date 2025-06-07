import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import mysql.connector
from admin.crud import admin_crud

app = Flask(__name__)
CORS(app)

# Clé secrète pour les sessions (en prod, utilise une vraie valeur stockée en variable d'env)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "valais_db")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "apppassword")

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4'
    )

@app.route("/api/cities", methods=["GET"])
def list_cities():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT DISTINCT c.id, c.name, c.latitude, c.longitude
        FROM cities c
        JOIN city_themes ct ON ct.city_id = c.id
        ORDER BY c.name;
    """
    cursor.execute(query)
    villes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(villes)

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

app.register_blueprint(admin_crud)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)