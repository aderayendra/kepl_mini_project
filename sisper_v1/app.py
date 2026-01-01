import curses
import hashlib
from re import search

from flask import Flask, render_template, request, redirect, session, url_for, flash, g
from db import get_db
import requests

app = Flask(__name__)
app.secret_key = "KZN-%d""7A[3J(90e$AF6~O#Z8grVsqqUuuf{#Qy>}URL_;ZEJnOz/-vP+*^EPE"  # required for sessions


def get_db_conn():
    if 'db' not in g:
        g.db = get_db()
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# -------------------------
# LOGIN MAHASISWA
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
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
        url = "http://127.0.0.1:5001/api/mahasiswa/login"
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "nim" not in session and "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")
    return render_template(
        "dashboard.html",
        nim=session["nim"] if "nim" in session else session["admin"],
        nama=session["nama"]
    )


# -------------------------
# DAFTAR BUKU
# -------------------------
@app.route("/buku")
def buku():
    if "nim" not in session and "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    search_keyword = request.args.get('s')

    db = get_db_conn()
    cur = db.cursor()
    try:
        if search_keyword:
            cur.execute(
                """
                SELECT b.*,
                       CASE
                           WHEN SUM(pem.status = 'dipinjam') > 0 THEN 'Dipinjam'
                           WHEN SUM(pem.status = 'dibooking') > 0 THEN 'Dibooking'
                           ELSE 'Tersedia'
                           END AS status
                FROM buku b
                         LEFT JOIN peminjaman pem ON pem.isbn = b.isbn
                WHERE (b.judul LIKE %s OR b.penulis LIKE %s)
                  AND b.waktu_hapus IS NULL
                GROUP BY b.isbn
                """,
                (f"%{search_keyword}%", f"%{search_keyword}%")
            )
            buku = cur.fetchall()
        else:
            cur.execute(
                """
                SELECT b.*,
                       CASE
                           WHEN SUM(pem.status = 'dipinjam') > 0 THEN 'Dipinjam'
                           WHEN SUM(pem.status = 'dibooking') > 0 THEN 'Dibooking'
                           ELSE 'Tersedia'
                           END AS status
                FROM buku b
                         LEFT JOIN peminjaman pem ON pem.isbn = b.isbn
                WHERE b.waktu_hapus IS NULL
                GROUP BY b.isbn
                """,
            )
            buku = cur.fetchall()
    except Exception as e:
        flash(f'{e}', 'error')
        return redirect("/dashboard")

    return render_template("buku.html", buku=buku)


@app.route("/buku/tambah", methods=["POST", "GET"])
def buku_tambah():
    if request.method != "POST":
        return redirect("/buku")

    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")

    db = get_db_conn()
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO buku (isbn, judul, penulis, kategori, sinopsis, tahun) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                request.form["isbn"],
                request.form["judul"],
                request.form["penulis"],
                request.form["kategori"],
                request.form["sinopsis"],
                request.form["tahun"]
            )
        )
        db.commit()
        flash('Buku berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f'{e}', 'error')

    return redirect("/buku")


# Route untuk edit buku
@app.route('/buku/edit', methods=['POST'])
def edit_buku():
    if not session.get('admin'):
        flash('Akses ditolak', 'error')
        return redirect('/buku')

    isbn_original = request.form['isbn_original']
    judul = request.form['judul']
    penulis = request.form['penulis']
    kategori = request.form['kategori']
    sinopsis = request.form['sinopsis']
    tahun = request.form['tahun']
    db = get_db_conn()
    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE buku SET judul=%s, penulis=%s, kategori=%s, sinopsis=%s, tahun=%s, waktu_edit=now() WHERE isbn=%s",
            (judul, penulis, kategori, sinopsis, tahun, isbn_original)
        )
        db.commit()
        flash('Buku berhasil diupdate!', 'success')
    except Exception as e:
        flash(f'{e}', 'error')

    return redirect('/buku')


# Route untuk hapus buku
@app.route('/buku/hapus', methods=['GET'])
def hapus_buku():
    if not session.get('admin'):
        flash('Akses ditolak', 'error')
        return redirect('/buku')

    isbn = request.args.get('isbn')
    db = get_db_conn()

    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE buku SET waktu_hapus = now()WHERE isbn=%s",
            isbn
        )
        db.commit()
        flash('Buku berhasil dihapus!', 'success')
    except Exception as e:
        flash(f'{e}', 'error')

    return redirect('/buku')


# -------------------------
# DAFTAR PEMINJAMAN
# -------------------------

@app.route("/peminjaman")
def peminjaman():
    if "nim" not in session and "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    db = get_db_conn()
    cur = db.cursor()
    try:
        query = """
                SELECT p.*, b.judul, m.nama
                FROM peminjaman p
                         JOIN buku b ON p.isbn = b.isbn
                         JOIN mahasiswa m ON p.nim = m.nim \
                """
        params = []
        where_clauses = []

        if "nim" in session:
            where_clauses.append("p.nim = %s")
            params.append(session["nim"])

        search_keyword = request.args.get('s')
        if search_keyword:
            where_clauses.append("(p.id LIKE %s OR p.isbn LIKE %s OR m.nama LIKE %s)")
            params.extend([f"%{search_keyword}%", f"%{search_keyword}%", f"%{search_keyword}%"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cur.execute(query, tuple(params))
        peminjaman_list = cur.fetchall()
    except Exception as e:
        flash(f'{e}', 'error')
        peminjaman_list = []

    return render_template("peminjaman.html", peminjaman_list=peminjaman_list)


@app.route("/peminjaman/tambah", methods=["POST"])
def peminjaman_tambah():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")
    if request.method != "POST":
        return redirect("/peminjaman")
    db = get_db_conn()
    try:
        cur = db.cursor()
        isbn = request.form["isbn"]
        nim = request.form["nim"]

        if not isbn.isdigit() or len(isbn) != 13:
            flash('ISBN harus terdiri dari 13 digit angka', 'error')
            return redirect("/peminjaman")

        if not nim.isdigit():
            flash('NIM harus berupa angka', 'error')
            return redirect("/peminjaman")

        # Periksa apakah buku ada dan belum dihapus
        cur.execute("SELECT isbn FROM buku WHERE isbn = %s AND waktu_hapus IS NULL", (isbn,))
        if not cur.fetchone():
            flash('Buku tidak ditemukan atau sudah dihapus', 'error')
            return redirect("/peminjaman")

        # Periksa apakah buku sedang dipinjam atau dibooking
        cur.execute(
            "SELECT status FROM peminjaman WHERE isbn = %s AND status IN ('dipinjam', 'dibooking')",
            (isbn,)
        )
        if cur.fetchone():
            flash('Buku sedang dipinjam atau dibooking', 'error')
            return redirect("/peminjaman")

        cur.execute(
            "INSERT INTO peminjaman (nim, isbn, waktu_pinjam, status) VALUES (%s, %s, now(), 'dipinjam')",
            (nim, isbn)
        )
        db.commit()
        flash('Peminjaman berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f'{e}', 'error')

    return redirect("/peminjaman")


@app.route("/peminjaman/booking", methods=["POST"])
def peminjaman_booking():
    if "nim" not in session:
        flash('Anda belum login sebagai mahasiswa', 'error')
        return redirect("/dashboard")
    if request.method != "POST":
        return redirect("/peminjaman")
    db = get_db_conn()
    try:
        cur = db.cursor()
        isbn = request.form["isbn"]
        nim = session["nim"]

        if not isbn.isdigit() or len(isbn) != 13:
            flash('ISBN harus terdiri dari 13 digit angka', 'error')
            return redirect("/peminjaman")

        cur.execute("SELECT isbn FROM buku WHERE isbn = %s AND waktu_hapus IS NULL", (isbn,))
        if not cur.fetchone():
            flash('Buku tidak ditemukan atau sudah dihapus', 'error')
            return redirect("/peminjaman")
        cur.execute("SELECT status FROM peminjaman WHERE isbn = %s AND status IN ('dipinjam', 'dibooking')", (isbn,))
        if cur.fetchone():
            flash('Buku sedang dipinjam atau dibooking', 'error')
            return redirect("/peminjaman")
        cur.execute("INSERT INTO peminjaman (nim, isbn, waktu_booking, status) VALUES (%s, %s, now(), 'dibooking')",
                    (nim, isbn))
        db.commit()
        flash('Peminjaman berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f'{e}', 'error')
    return redirect("/peminjaman")


@app.route("/peminjaman/setujui-booking", methods=["GET"])
def setujui_booking():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")
    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = request.args.get('id')

        # Check current status
        cur.execute("SELECT status FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            flash('Data peminjaman tidak ditemukan', 'error')
            return redirect("/peminjaman")

        if row['status'] != 'dibooking':
            flash(f'Gagal menyetujui: Status saat ini adalah {row["status"]}', 'error')
            return redirect("/peminjaman")

        cur.execute("UPDATE peminjaman SET status='dipinjam', waktu_pinjam=now() WHERE id=%s", (idPinjam,))
        db.commit()
        flash('Peminjaman berhasil disetujui', 'success')
    except Exception as e:
        flash(f'{e}', 'error')
    return redirect("/peminjaman")


@app.route("/peminjaman/tolak-booking", methods=["GET"])
def tolak_booking():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")
    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = request.args.get('id')

        cur.execute("SELECT status FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            flash('Data peminjaman tidak ditemukan', 'error')
            return redirect("/peminjaman")

        if row['status'] != 'dibooking':
            flash(f'Gagal menolak: Status saat ini adalah {row["status"]}', 'error')
            return redirect("/peminjaman")

        cur.execute("UPDATE peminjaman SET status='booking_ditolak' WHERE id=%s", (idPinjam,))
        db.commit()
        flash('Booking Peminjaman berhasil ditolak', 'success')
    except Exception as e:
        flash(f'{e}', 'error')
    return redirect("/peminjaman")


@app.route("/peminjaman/kembalikan", methods=["GET"])
def kembalikan_buku():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")
    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = request.args.get('id')

        cur.execute("SELECT status FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            flash('Data peminjaman tidak ditemukan', 'error')
            return redirect("/peminjaman")

        if row['status'] != 'dipinjam':
            flash(f'Gagal mengembalikan: Status saat ini adalah {row["status"]}', 'error')
            return redirect("/peminjaman")

        cur.execute(
            "UPDATE peminjaman SET status='dikembalikan', waktu_kembali=now() WHERE id=%s",
            (idPinjam,))
        db.commit()
        flash('Buku berhasil dikembalikan', 'success')
    except Exception as e:
        flash(f'{e}', 'error')
    return redirect("/peminjaman")


@app.route("/peminjaman/hapus-booking", methods=["GET"])
def hapus_booking():
    if "nim" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/dashboard")

    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = request.args.get('id')

        cur.execute("SELECT nim, status FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            flash('Data peminjaman tidak ditemukan', 'error')
            return redirect("/peminjaman")

        if row['status'] != 'dibooking':
            flash(f'Gagal menghapus: Status saat ini adalah {row["status"]}', 'error')
            return redirect("/peminjaman")

        nim = session["nim"]
        if str(row['nim']) != str(nim):
            flash('Anda tidak memiliki akses untuk menghapus booking ini', 'error')
            return redirect("/peminjaman")
        cur.execute("DELETE FROM peminjaman WHERE id=%s", (idPinjam,))
        flash('Booking Peminjaman berhasil dihapus', 'success')

        db.commit()
    except Exception as e:
        flash(f'{e}', 'error')
    return redirect("/peminjaman")


# -------------------------
# DAFTAR MAHASISWA
# -------------------------
@app.route("/mahasiswa")
def mahasiswa():
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


@app.route("/mahasiswa/sync")
def sync_mahasiswa():
    if "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    db = get_db_conn()
    cur = db.cursor()
    try:
        url = "http://127.0.0.1:5001/api/mahasiswa"
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


if __name__ == "__main__":
    app.run(debug=True)
