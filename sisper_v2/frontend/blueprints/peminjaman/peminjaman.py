import requests
from flask import Blueprint, render_template, request, redirect, session, flash

PEMINJAMAN_SERVICE_URL = "http://127.0.0.1:5004"

peminjaman_bp = Blueprint('peminjaman', __name__)


@peminjaman_bp.route("/peminjaman")
def peminjaman():
    if "nim" not in session and "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    nim = session.get("nim")
    search_keyword = request.args.get('s')

    try:
        url = f"{PEMINJAMAN_SERVICE_URL}/peminjaman"
        payload = {"nim": nim, "s": search_keyword}
        response = requests.post(url, json=payload)
        peminjaman_list = response.json()
        if isinstance(peminjaman_list, dict) and "error" in peminjaman_list:
            flash(f"{peminjaman_list['error']}", 'error')
            peminjaman_list = []
    except Exception as e:
        flash(f'Error connecting to peminjaman service: {e}', 'error')
        peminjaman_list = []

    return render_template("peminjaman.html", peminjaman_list=peminjaman_list)


@peminjaman_bp.route("/peminjaman/tambah", methods=["POST"])
def peminjaman_tambah():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")
    if request.method != "POST":
        return redirect("/peminjaman")

    try:
        url = f"{PEMINJAMAN_SERVICE_URL}/peminjaman/tambah"
        payload = {
            "isbn": request.form["isbn"],
            "nim": request.form["nim"]
        }
        response = requests.post(url, json=payload)
        response_json = response.json()
        if response.status_code == 201:
            flash('Peminjaman berhasil ditambahkan', 'success')
        else:
            flash(response_json.get("error", "Gagal menambahkan peminjaman"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect("/peminjaman")


@peminjaman_bp.route("/peminjaman/booking", methods=["POST"])
def peminjaman_booking():
    if "nim" not in session:
        flash('Anda belum login sebagai mahasiswa', 'error')
        return redirect("/dashboard")
    if request.method != "POST":
        return redirect("/peminjaman")

    try:
        url = f"{PEMINJAMAN_SERVICE_URL}/peminjaman/booking"
        payload = {
            "isbn": request.form["isbn"],
            "nim": session["nim"]
        }
        response = requests.post(url, json=payload)
        response_json = response.json()
        if response.status_code == 201:
            flash('Booking berhasil ditambahkan', 'success')
        else:
            flash(response_json.get("error", "Gagal melakukan booking"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect("/peminjaman")


@peminjaman_bp.route("/peminjaman/setujui-booking", methods=["GET"])
def setujui_booking():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")

    idPinjam = request.args.get('id')
    try:
        url = f"{PEMINJAMAN_SERVICE_URL}/peminjaman/setujui-booking"
        response = requests.post(url, json={"id": idPinjam})
        response_json = response.json()
        if response.status_code == 200:
            flash('Peminjaman berhasil disetujui', 'success')
        else:
            flash(response_json.get("error", "Gagal menyetujui booking"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect("/peminjaman")


@peminjaman_bp.route("/peminjaman/tolak-booking", methods=["GET"])
def tolak_booking():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")

    idPinjam = request.args.get('id')
    try:
        url = f"{PEMINJAMAN_SERVICE_URL}/peminjaman/tolak-booking"
        response = requests.post(url, json={"id": idPinjam})
        response_json = response.json()
        if response.status_code == 200:
            flash('Booking Peminjaman berhasil ditolak', 'success')
        else:
            flash(response_json.get("error", "Gagal menolak booking"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect("/peminjaman")


@peminjaman_bp.route("/peminjaman/kembalikan", methods=["GET"])
def kembalikan_buku():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")

    idPinjam = request.args.get('id')
    try:
        url = f"{PEMINJAMAN_SERVICE_URL}/peminjaman/kembalikan"
        response = requests.post(url, json={"id": idPinjam})
        response_json = response.json()
        if response.status_code == 200:
            flash('Buku berhasil dikembalikan', 'success')
        else:
            flash(response_json.get("error", "Gagal mengembalikan buku"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect("/peminjaman")


@peminjaman_bp.route("/peminjaman/hapus-booking", methods=["GET"])
def hapus_booking():
    if "nim" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/dashboard")

    idPinjam = request.args.get('id')
    nim = session["nim"]
    try:
        url = f"{PEMINJAMAN_SERVICE_URL}/peminjaman/hapus-booking"
        response = requests.delete(url, params={"id": idPinjam, "nim": nim})
        response_json = response.json()
        if response.status_code == 200:
            flash('Booking Peminjaman berhasil dihapus', 'success')
        else:
            flash(response_json.get("error", "Gagal menghapus booking"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect("/peminjaman")
