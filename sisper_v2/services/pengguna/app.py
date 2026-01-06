from time import sleep

from flask import Flask, jsonify, request
import hashlib
import requests
import redis
import json
from db import get_db_conn
from config import REDIS_CONFIG, LOAD_TIME

app = Flask(__name__)
redis_client = redis.Redis(**REDIS_CONFIG)


def publish_mahasiswa_event(mahasiswa_list=None):
    db = get_db_conn()
    cur = db.cursor()
    try:
        # if mahasiswa_list empty or not a list
        if not mahasiswa_list or type(mahasiswa_list) != list:
            cur.execute("SELECT * FROM mahasiswa")
            mahasiswa_list = cur.fetchall()

        for mhs in mahasiswa_list:
            if mhs.get("tanggal_masuk"):
                mhs["tanggal_masuk"] = mhs["tanggal_masuk"].strftime("%Y-%m-%d")

        event_data = {
            "event": "mahasiswa_updated",
            "data": mahasiswa_list
        }
        print(f"Publishing mahasiswa_updated event: {event_data}")
        redis_client.publish("mahasiswa_events", json.dumps(event_data))
    except Exception as e:
        print(f"Error publishing to Redis: {e}")


@app.route("/login", methods=["POST"])
def login():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    data = request.get_json()
    if not data or "nim" not in data or "password" not in data or "jenis" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    nim = data["nim"]
    password = data["password"]
    jenis = data["jenis"]

    db = get_db_conn()
    cur = db.cursor()

    if jenis == "admin":
        cur.execute("SELECT * FROM admin WHERE username=%s", nim)
        admin = cur.fetchone()
        if admin and admin["password"] == hashlib.sha256(password.encode('utf-8')).hexdigest():
            return jsonify({
                "authenticated": True,
                "user": {
                    "username": admin["username"],
                    "nama": admin["nama"],
                    "jenis": "admin"
                }
            })
        return jsonify({"authenticated": False, "error": "Username atau password salah"}), 401

    try:
        url = "http://127.0.0.1:5000/api/mahasiswa/login"
        payload = {"nim": nim, "password": password}
        response = requests.post(url, json=payload)
        response_json = response.json()
        if response_json.get("authenticated"):
            mahasiswa = response_json["mahasiswa"]
            cur.execute("""
                        INSERT INTO mahasiswa (nim, nama, jenis_kelamin, jurusan, prodi, tanggal_masuk, no_hp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                        UPDATE nama = %s, jenis_kelamin = %s, jurusan = %s, prodi = %s, tanggal_masuk = %s, no_hp = %s
                        """,
                        [
                            nim,
                            mahasiswa["nama"],
                            mahasiswa["jenis_kelamin"],
                            mahasiswa["jurusan"], mahasiswa["prodi"],
                            mahasiswa["tanggal_masuk"], mahasiswa["no_hp"],
                            mahasiswa["nama"],
                            mahasiswa["jenis_kelamin"],
                            mahasiswa["jurusan"], mahasiswa["prodi"],
                            mahasiswa["tanggal_masuk"], mahasiswa["no_hp"]
                        ])
            db.commit()
            publish_mahasiswa_event(mahasiswa_list=[mahasiswa])
            return jsonify({
                "authenticated": True,
                "user": {
                    "nim": nim,
                    "nama": mahasiswa["nama"],
                    "jenis": "mahasiswa"
                }
            })
        return jsonify({"authenticated": False, "error": "NIM atau password salah"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sync-mahasiswa", methods=["POST"])
def sync_mahasiswa():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    db = get_db_conn()
    cur = db.cursor()
    try:
        url = "http://127.0.0.1:5000/api/mahasiswa"
        response = requests.get(url)
        response_json = response.json()
        mahasiswa_list = response_json["mahasiswa"]
        for mhs in mahasiswa_list:
            cur.execute("""
                        INSERT INTO mahasiswa (nim, nama, jenis_kelamin, jurusan, prodi, tanggal_masuk, no_hp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                        UPDATE nama = %s, jenis_kelamin = %s, jurusan = %s, prodi = %s, tanggal_masuk = %s, no_hp = %s
                        """,
                        [
                            mhs["nim"],
                            mhs["nama"],
                            mhs["jenis_kelamin"],
                            mhs["jurusan"], mhs["prodi"],
                            mhs["tanggal_masuk"], mhs["no_hp"],
                            mhs["nama"],
                            mhs["jenis_kelamin"],
                            mhs["jurusan"], mhs["prodi"],
                            mhs["tanggal_masuk"], mhs["no_hp"]
                        ])
            db.commit()

        publish_mahasiswa_event()
        return jsonify({"message": "Berhasil sinkronisasi", "count": len(mahasiswa_list)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/mahasiswa", methods=["GET"])
def get_mahasiswa():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    db = get_db_conn()
    cur = db.cursor()
    try:
        cur.execute("SELECT * FROM mahasiswa")
        mahasiswa_list = cur.fetchall()

        for mhs in mahasiswa_list:
            if mhs.get("tanggal_masuk"):
                mhs["tanggal_masuk"] = mhs["tanggal_masuk"].strftime("%Y-%m-%d")

        return jsonify({
            "count": len(mahasiswa_list),
            "mahasiswa": mahasiswa_list
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5002)
