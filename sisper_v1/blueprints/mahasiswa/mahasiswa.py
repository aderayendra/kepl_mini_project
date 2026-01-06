from time import sleep

import requests
from flask import Blueprint, render_template, redirect, session, flash
from ...db import get_db_conn
from ...config import LOAD_TIME

mahasiswa_bp = Blueprint('mahasiswa', __name__)


@mahasiswa_bp.route("/mahasiswa")
def mahasiswa():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    if "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    db = get_db_conn()
    cur = db.cursor()
    try:
        cur.execute("SELECT * FROM mahasiswa")
        mahasiswa_list = cur.fetchall()
    except Exception as e:
        flash(f'{e}', 'error')
        return redirect("/dashboard")

    return render_template("mahasiswa.html", mahasiswa_list=mahasiswa_list)


@mahasiswa_bp.route("/mahasiswa/sync")
def sync_mahasiswa():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    if "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

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

        flash('Berhasil sinkronisasi', 'success')
    except Exception as e:
        flash(f'{e}', 'error')

    return redirect("/mahasiswa")
