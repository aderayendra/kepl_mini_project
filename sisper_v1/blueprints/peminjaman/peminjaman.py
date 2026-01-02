from flask import Blueprint, render_template, request, redirect, session, flash
from ...db import get_db_conn

peminjaman_bp = Blueprint('peminjaman', __name__)


@peminjaman_bp.route("/peminjaman")
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


@peminjaman_bp.route("/peminjaman/tambah", methods=["POST"])
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


@peminjaman_bp.route("/peminjaman/booking", methods=["POST"])
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
            flash('Buku sedang dipinjam or dibooking', 'error')
            return redirect("/peminjaman")
        cur.execute("INSERT INTO peminjaman (nim, isbn, waktu_booking, status) VALUES (%s, %s, now(), 'dibooking')",
                    (nim, isbn))
        db.commit()
        flash('Peminjaman berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f'{e}', 'error')
    return redirect("/peminjaman")


@peminjaman_bp.route("/peminjaman/setujui-booking", methods=["GET"])
def setujui_booking():
    if "admin" not in session:
        flash('Anda bukan admin', 'error')
        return redirect("/dashboard")
    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = request.args.get('id')

        # Check the current status
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


@peminjaman_bp.route("/peminjaman/tolak-booking", methods=["GET"])
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


@peminjaman_bp.route("/peminjaman/kembalikan", methods=["GET"])
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


@peminjaman_bp.route("/peminjaman/hapus-booking", methods=["GET"])
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
