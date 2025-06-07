from flask import Blueprint, request, jsonify
import mysql.connector
import os

admin_crud = Blueprint("admin_crud", __name__)

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

# --- CRUD for Cities ---
@admin_crud.route("/api/cities", methods=["GET", "POST"])
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
        data = request.json
        cursor.execute(
            "INSERT INTO cities (name, latitude, longitude, email) VALUES (%s, %s, %s, %s)",
            (data["name"], data["latitude"], data["longitude"], data.get("email", "")),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201

@admin_crud.route("/api/cities/<int:city_id>", methods=["PUT", "DELETE"])
def city_detail(city_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "PUT":
        data = request.json
        cursor.execute(
            "UPDATE cities SET name=%s, latitude=%s, longitude=%s, email=%s WHERE id=%s",
            (data["name"], data["latitude"], data["longitude"], data.get("email", ""), city_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    elif request.method == "DELETE":
        cursor.execute("DELETE FROM cities WHERE id=%s", (city_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})

# --- CRUD for Themes ---
@admin_crud.route("/api/themes", methods=["GET", "POST"])
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
        data = request.json
        cursor.execute("INSERT INTO themes (name) VALUES (%s)", (data["name"],))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201

@admin_crud.route("/api/themes/<int:theme_id>", methods=["PUT", "DELETE"])
def theme_detail(theme_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "PUT":
        data = request.json
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
@admin_crud.route("/api/city_themes", methods=["GET", "POST"])
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
        data = request.json
        cursor.execute(
            "INSERT INTO city_themes (city_id, theme_id) VALUES (%s, %s)",
            (data["city_id"], data["theme_id"]),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201

@admin_crud.route("/api/city_themes/<int:city_id>/<int:theme_id>", methods=["DELETE"])
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
@admin_crud.route("/api/contents", methods=["GET", "POST"])
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
        data = request.json
        cursor.execute(
            "INSERT INTO contents (theme_id, title, url) VALUES (%s, %s, %s)",
            (data["theme_id"], data["title"], data["url"]),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201

@admin_crud.route("/api/contents/<int:content_id>", methods=["PUT", "DELETE"])
def content_detail(content_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "PUT":
        data = request.json
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