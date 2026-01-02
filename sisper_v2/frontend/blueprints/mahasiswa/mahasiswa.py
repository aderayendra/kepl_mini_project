import requests
from flask import Blueprint, render_template, redirect, session, flash

PENGGUNA_SERVICE_URL = "http://127.0.0.1:5002"

mahasiswa_bp = Blueprint('mahasiswa', __name__)


@mahasiswa_bp.route("/mahasiswa")
def mahasiswa():
    if "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    try:
        url = f"{PENGGUNA_SERVICE_URL}/mahasiswa"
        response = requests.get(url)
        response_json = response.json()
        mahasiswa_list = response_json.get("mahasiswa", [])
    except Exception as e:
        flash(f'Error connecting to pengguna service: {e}', 'error')
        return redirect("/dashboard")

    return render_template("mahasiswa.html", mahasiswa_list=mahasiswa_list)


@mahasiswa_bp.route("/mahasiswa/sync")
def sync_mahasiswa():
    if "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    try:
        url = f"{PENGGUNA_SERVICE_URL}/sync-mahasiswa"
        response = requests.post(url)
        response_json = response.json()
        if response.status_code == 200:
            flash(f"Berhasil sinkronisasi {response_json.get('count', 0)} mahasiswa", 'success')
        else:
            flash(response_json.get("error", "Gagal sinkronisasi"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect("/mahasiswa")
