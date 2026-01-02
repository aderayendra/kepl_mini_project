import requests
from flask import Blueprint, render_template, request, redirect, session, flash

BUKU_SERVICE_URL = "http://127.0.0.1:5003"

buku_bp = Blueprint('buku', __name__)

@buku_bp.route("/buku")
def buku():
    if "nim" not in session and "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    search_keyword = request.args.get('s')
    nim = session.get("nim")

    try:
        url = f"{BUKU_SERVICE_URL}/buku"
        payload = {"s": search_keyword, "nim": nim}
        response = requests.post(url, json=payload)
        buku_list = response.json()
        if isinstance(buku_list, dict) and "error" in buku_list:
             flash(f"{buku_list['error']}", 'error')
             buku_list = []
    except Exception as e:
        flash(f'Error connecting to buku service: {e}', 'error')
        return redirect("/dashboard")

    return render_template("buku.html", buku=buku_list)

@buku_bp.route("/buku/tambah", methods=["POST", "GET"])
def buku_tambah():
    if request.method != "POST":
        return redirect("/buku")

    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")

    try:
        url = f"{BUKU_SERVICE_URL}/buku/tambah"
        payload = {
            "isbn": request.form["isbn"],
            "judul": request.form["judul"],
            "penulis": request.form["penulis"],
            "kategori": request.form["kategori"],
            "sinopsis": request.form["sinopsis"],
            "tahun": request.form["tahun"]
        }
        response = requests.post(url, json=payload)
        response_json = response.json()
        if response.status_code == 201:
            flash('Buku berhasil ditambahkan', 'success')
        else:
            flash(response_json.get("error", "Gagal menambahkan buku"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect("/buku")

@buku_bp.route('/buku/edit', methods=['POST'])
def edit_buku():
    if not session.get('admin'):
        flash('Akses ditolak', 'error')
        return redirect('/buku')

    try:
        url = f"{BUKU_SERVICE_URL}/buku/edit"
        payload = {
            "isbn_original": request.form['isbn_original'],
            "judul": request.form['judul'],
            "penulis": request.form['penulis'],
            "kategori": request.form['kategori'],
            "sinopsis": request.form['sinopsis'],
            "tahun": request.form['tahun']
        }
        response = requests.post(url, json=payload)
        response_json = response.json()
        if response.status_code == 200:
            flash('Buku berhasil diupdate!', 'success')
        else:
            flash(response_json.get("error", "Gagal mengupdate buku"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect('/buku')

@buku_bp.route('/buku/hapus', methods=['GET'])
def hapus_buku():
    if not session.get('admin'):
        flash('Akses ditolak', 'error')
        return redirect('/buku')

    isbn = request.args.get('isbn')
    try:
        url = f"{BUKU_SERVICE_URL}/buku/hapus"
        response = requests.delete(url, params={"isbn": isbn})
        response_json = response.json()
        if response.status_code == 200:
            flash('Buku berhasil dihapus!', 'success')
        else:
            flash(response_json.get("error", "Gagal menghapus buku"), 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect('/buku')
