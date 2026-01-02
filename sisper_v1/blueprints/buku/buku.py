from flask import Blueprint, render_template, request, redirect, session, flash
from ...db import get_db_conn

buku_bp = Blueprint('buku', __name__)

@buku_bp.route("/buku")
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
            buku_list = cur.fetchall()
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
            buku_list = cur.fetchall()
    except Exception as e:
        flash(f'{e}', 'error')
        return redirect("/dashboard")

    return render_template("buku.html", buku=buku_list)

@buku_bp.route("/buku/tambah", methods=["POST", "GET"])
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

@buku_bp.route('/buku/edit', methods=['POST'])
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

@buku_bp.route('/buku/hapus', methods=['GET'])
def hapus_buku():
    if not session.get('admin'):
        flash('Akses ditolak', 'error')
        return redirect('/buku')

    isbn = request.args.get('isbn')
    db = get_db_conn()

    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE buku SET waktu_hapus = now() WHERE isbn=%s",
            isbn
        )
        db.commit()
        flash('Buku berhasil dihapus!', 'success')
    except Exception as e:
        flash(f'{e}', 'error')

    return redirect('/buku')
