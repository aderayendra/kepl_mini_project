from flask import Flask, jsonify, request, render_template
import pymysql
import hashlib
from config import DB_CONFIG

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


# Web routes
@app.route("/")
def home():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mahasiswa")
            mahasiswa_list = cursor.fetchall()

        for m in mahasiswa_list:
            m.pop("password", None)
            if m.get("tanggal_masuk"):
                m["tanggal_masuk"] = m["tanggal_masuk"].strftime("%Y-%m-%d")

        return render_template("mahasiswa.html", mahasiswa=mahasiswa_list)
    finally:
        conn.close()

# ------------------------------------------------------


@app.route("/api/mahasiswa", methods=["GET"])
def get_all_mahasiswa():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mahasiswa")
            mahasiswa_list = cursor.fetchall()

        for m in mahasiswa_list:
            m.pop("password", None)
            if m.get("tanggal_masuk"):
                m["tanggal_masuk"] = m["tanggal_masuk"].strftime("%Y-%m-%d")

        return jsonify({
            "count": len(mahasiswa_list),
            "mahasiswa": mahasiswa_list
        })
    finally:
        conn.close()


@app.route("/api/mahasiswa/login", methods=["POST"])
def authenticate_mahasiswa():
    data = request.get_json()

    if not data or "nim" not in data or "password" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM mahasiswa
                WHERE nim = %s
                """,
                (data["nim"])
            )
            mahasiswa = cursor.fetchone()

        if not mahasiswa:
            return jsonify({"authenticated": False, "error": "Mahasiswa not found"}), 404

        if mahasiswa["password"] != hashlib.sha256(data["password"].encode('utf-8')).hexdigest():
            return jsonify({"authenticated": False, "error": "Wrong password"}), 401

        del mahasiswa["password"]
        mahasiswa['tanggal_masuk'] = mahasiswa['tanggal_masuk'].strftime('%Y-%m-%d')

        return jsonify({
            "authenticated": True,
            "mahasiswa": mahasiswa
        })
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
