import hashlib
from time import sleep

import requests
from flask import Blueprint, render_template, request, redirect, session, flash
from ...db import get_db_conn
from ...config import LOAD_TIME

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------

    if "nim" in session or "admin" in session:
        return redirect("/dashboard")

    if request.method != "POST":
        session.clear()
        return render_template('login.html')

    nim = request.form["nim"]
    password = request.form["password"]
    jenis = request.form["jenis"]

    db = get_db_conn()
    cur = db.cursor()

    if jenis == "admin":
        cur.execute("SELECT * FROM admin WHERE username=%s", nim)
        admin = cur.fetchone()
        if admin and admin["password"] == hashlib.sha256(password.encode('utf-8')).hexdigest():
            session["admin"] = admin["username"]
            session["nama"] = admin["nama"]
            return redirect("/dashboard")
        flash('Username atau password salah', 'error')
        return render_template("login.html")

    try:
        url = "http://127.0.0.1:5000/api/mahasiswa/login"
        payload = {"nim": nim, "password": password}
        response = requests.post(url, json=payload)
        response_json = response.json()
        if response_json["authenticated"]:
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
            session["nim"] = nim
            session["nama"] = mahasiswa["nama"]
            return redirect("/dashboard")
        flash('NIM atau password salah', 'error')
    except Exception as e:
        flash(f'{e}', 'error')

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    session.clear()
    return redirect("/")
