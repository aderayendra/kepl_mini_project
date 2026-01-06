from time import sleep

from flask import Flask, jsonify, request, render_template
import hashlib
import requests
from db import get_db_conn
from config import LOAD_TIME

app = Flask(__name__)


# Web routes
@app.route("/")
def home():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    conn = get_db_conn()
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


@app.route("/cek-pinjaman/<int:nim>", methods=["GET"])
def cek_pinjaman(nim):
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    try:
        response = requests.post("http://localhost:5004/peminjaman/cek-pinjaman", json={"nim": nim})
        if response.status_code == 200:
            return render_template("pinjaman.html", pinjaman=response.json())
        else:
            return render_template("pinjaman.html", error="Failed to fetch from loan service",
                                   details=response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return render_template("pinjaman.html", error=f"Loan service unavailable: {str(e)}"), 503


# ------------------------------------------------------


@app.route("/api/mahasiswa", methods=["GET"])
def get_all_mahasiswa():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    conn = get_db_conn()
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
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    data = request.get_json()
    if not data or "nim" not in data or "password" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    conn = get_db_conn()
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
    app.run(debug=True, port=5000)
