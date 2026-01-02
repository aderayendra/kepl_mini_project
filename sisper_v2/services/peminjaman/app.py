from flask import Flask, jsonify, request
import redis
import json
import threading
from db import get_db_conn
from config import REDIS_CONFIG

app = Flask(__name__)
redis_client = redis.Redis(**REDIS_CONFIG)


def publish_peminjaman_event(isbn, status):
    try:
        event_payload = {
            "event": "book_status_updated",
            "data": {
                "isbn": isbn,
                "status": status
            }
        }
        redis_client.publish("book_events", json.dumps(event_payload))
    except Exception as e:
        print(f"Error publishing to Redis: {e}")


def handle_mahasiswa_update(data):
    from db import get_db
    db = get_db()
    try:
        cur = db.cursor()
        for mhs in data:
            cur.execute("""
                        INSERT INTO mahasiswa (nim, nama, jurusan)
                        VALUES (%s, %s, %s) ON DUPLICATE KEY
                        UPDATE nama = %s, jurusan = %s
                        """, [
                            mhs["nim"], mhs["nama"], mhs["jurusan"],
                            mhs["nama"], mhs["jurusan"],
                        ])
        db.commit()
        print(f"Synced {len(data)} mahasiswa records.")
    except Exception as e:
        print(f"Error syncing mahasiswa in DB: {e}")
    finally:
        db.close()


def handle_book_event(event_type, data):
    from db import get_db
    db = get_db()
    try:
        cur = db.cursor()
        if event_type == "book_added":
            cur.execute("""
                        INSERT INTO buku (isbn, judul, penulis)
                        VALUES (%s, %s, %s)
                        """, (data["isbn"], data["judul"], data["penulis"]))
        elif event_type == "book_updated":
            cur.execute("""
                        UPDATE buku
                        SET judul=%s,
                            penulis=%s
                        WHERE isbn = %s
                        """, (data["judul"], data["penulis"], data["isbn_original"]))
        elif event_type == "book_deleted":
            cur.execute("UPDATE buku SET waktu_hapus = now() WHERE isbn=%s", (data["isbn"],))

        db.commit()
        print(f"Processed book event {event_type} for ISBN {data.get('isbn') or data.get('isbn_original')}")
    except Exception as e:
        print(f"Error processing book event in DB: {e}")
    finally:
        db.close()


def start_subscriber():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("mahasiswa_events", "book_events")
    print("Subscribed to mahasiswa_events and book_events channels...")
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                payload = json.loads(message["data"])
                event_type = payload.get("event")
                if event_type == "mahasiswa_updated":
                    handle_mahasiswa_update(payload.get("data"))
                elif event_type in ["book_added", "book_updated", "book_deleted"]:
                    handle_book_event(event_type, payload.get("data"))
            except Exception as e:
                print(f"Error processing Redis message: {e}")


# Start subscriber in a background thread
subscriber_thread = threading.Thread(target=start_subscriber, daemon=True)
subscriber_thread.start()


@app.route("/peminjaman", methods=["POST"])
def peminjaman():
    data = request.get_json() or {}
    nim = data.get("nim")
    search_keyword = data.get("s")

    db = get_db_conn()
    cur = db.cursor()
    try:
        query = """
                SELECT p.*, b.judul, m.nama
                FROM peminjaman p
                         JOIN buku b ON p.isbn = b.isbn
                         JOIN mahasiswa m ON p.nim = m.nim
                """
        params = []
        where_clauses = []

        if nim:
            where_clauses.append("p.nim = %s")
            params.append(nim)

        if search_keyword:
            where_clauses.append("(p.id LIKE %s OR p.isbn LIKE %s OR m.nama LIKE %s)")
            params.extend([f"%{search_keyword}%", f"%{search_keyword}%", f"%{search_keyword}%"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cur.execute(query, tuple(params))
        peminjaman_list = cur.fetchall()

        for p in peminjaman_list:
            if p.get("waktu_pinjam"):
                p["waktu_pinjam"] = p["waktu_pinjam"].strftime("%Y-%m-%d %H:%M:%S")
            if p.get("waktu_kembali"):
                p["waktu_kembali"] = p["waktu_kembali"].strftime("%Y-%m-%d %H:%M:%S")
            if p.get("waktu_booking"):
                p["waktu_booking"] = p["waktu_booking"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify(peminjaman_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/peminjaman/tambah", methods=["POST"])
def peminjaman_tambah():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()
        isbn = data.get("isbn")
        nim = data.get("nim")

        if not isbn or not isbn.isdigit() or len(isbn) != 13:
            return jsonify({"error": "ISBN harus terdiri dari 13 digit angka"}), 400

        if not nim or not nim.isdigit():
            return jsonify({"error": "NIM harus berupa angka"}), 400

        # Periksa apakah buku ada dan belum dihapus
        cur.execute("SELECT isbn FROM buku WHERE isbn = %s AND waktu_hapus IS NULL", (isbn,))
        if not cur.fetchone():
            return jsonify({"error": "Buku tidak ditemukan atau sudah dihapus"}), 404

        # Periksa apakah buku sedang dipinjam atau dibooking
        cur.execute(
            "SELECT status FROM peminjaman WHERE isbn = %s AND status IN ('dipinjam', 'dibooking')",
            (isbn,)
        )
        if cur.fetchone():
            return jsonify({"error": "Buku sedang dipinjam atau dibooking"}), 409

        cur.execute(
            "INSERT INTO peminjaman (nim, isbn, waktu_pinjam, status) VALUES (%s, %s, now(), 'dipinjam')",
            (nim, isbn)
        )
        db.commit()
        publish_peminjaman_event(isbn, 'dipinjam')
        return jsonify({"message": "Peminjaman berhasil ditambahkan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/peminjaman/booking", methods=["POST"])
def peminjaman_booking():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()
        isbn = data.get("isbn")
        nim = data.get("nim")

        if not nim:
            return jsonify({"error": "NIM is required"}), 400

        if not isbn or not isbn.isdigit() or len(isbn) != 13:
            return jsonify({"error": "ISBN harus terdiri dari 13 digit angka"}), 400

        cur.execute("SELECT isbn FROM buku WHERE isbn = %s AND waktu_hapus IS NULL", (isbn,))
        if not cur.fetchone():
            return jsonify({"error": "Buku tidak ditemukan atau sudah dihapus"}), 404

        cur.execute("SELECT status FROM peminjaman WHERE isbn = %s AND status IN ('dipinjam', 'dibooking')", (isbn,))
        if cur.fetchone():
            return jsonify({"error": "Buku sedang dipinjam atau dibooking"}), 409

        cur.execute("INSERT INTO peminjaman (nim, isbn, waktu_booking, status) VALUES (%s, %s, now(), 'dibooking')",
                    (nim, isbn))
        db.commit()
        publish_peminjaman_event(isbn, 'dibooking')
        return jsonify({"message": "Booking berhasil ditambahkan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/peminjaman/setujui-booking", methods=["POST"])
def setujui_booking():
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "ID is required"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = data["id"]

        # Check the current status and get ISBN
        cur.execute("SELECT status, isbn FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Data peminjaman tidak ditemukan"}), 404

        if row['status'] != 'dibooking':
            return jsonify({"error": f"Gagal menyetujui: Status saat ini adalah {row['status']}"}), 400

        cur.execute("UPDATE peminjaman SET status='dipinjam', waktu_pinjam=now() WHERE id=%s", (idPinjam,))
        db.commit()
        publish_peminjaman_event(row['isbn'], 'dipinjam')
        return jsonify({"message": "Peminjaman berhasil disetujui"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/peminjaman/tolak-booking", methods=["POST"])
def tolak_booking():
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "ID is required"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = data["id"]

        cur.execute("SELECT status, isbn FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Data peminjaman tidak ditemukan"}), 404

        if row['status'] != 'dibooking':
            return jsonify({"error": f"Gagal menolak: Status saat ini adalah {row['status']}"}), 400

        cur.execute("UPDATE peminjaman SET status='booking_ditolak' WHERE id=%s", (idPinjam,))
        db.commit()
        publish_peminjaman_event(row['isbn'], 'tersedia')
        return jsonify({"message": "Booking Peminjaman berhasil ditolak"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/peminjaman/kembalikan", methods=["POST"])
def kembalikan_buku():
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "ID is required"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()
        idPinjam = data["id"]

        cur.execute("SELECT status, isbn FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Data peminjaman tidak ditemukan"}), 404

        if row['status'] != 'dipinjam':
            return jsonify({"error": f"Gagal mengembalikan: Status saat ini adalah {row['status']}"}), 400

        cur.execute(
            "UPDATE peminjaman SET status='dikembalikan', waktu_kembali=now() WHERE id=%s",
            (idPinjam,))
        db.commit()
        publish_peminjaman_event(row['isbn'], 'tersedia')
        return jsonify({"message": "Buku berhasil dikembalikan"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/peminjaman/hapus-booking", methods=["DELETE"])
def hapus_booking():
    idPinjam = request.args.get('id')
    nim = request.args.get('nim')

    if not idPinjam:
        return jsonify({"error": "ID is required"}), 400
    if not nim:
        return jsonify({"error": "NIM is required"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()

        cur.execute("SELECT nim, status, isbn FROM peminjaman WHERE id=%s", (idPinjam,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Data peminjaman tidak ditemukan"}), 404

        if row['status'] != 'dibooking':
            return jsonify({"error": f"Gagal menghapus: Status saat ini adalah {row['status']}"}), 400

        if str(row['nim']) != str(nim):
            return jsonify({"error": "Anda tidak memiliki akses untuk menghapus booking ini"}), 403

        cur.execute("DELETE FROM peminjaman WHERE id=%s", (idPinjam,))
        db.commit()
        publish_peminjaman_event(row['isbn'], 'tersedia')
        return jsonify({"message": "Booking Peminjaman berhasil dihapus"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/peminjaman/cek-pinjaman", methods=["POST"])
def cek_pinjaman():
    data = request.get_json()
    if not data or "nim" not in data:
        return jsonify({"error": "NIM is required"}), 400

    nim = data["nim"]
    db = get_db_conn()
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT COUNT(*) as count FROM peminjaman WHERE nim = %s AND status = 'dipinjam'",
            (nim,)
        )
        result = cur.fetchone()
        count = result["count"] if result else 0
        return jsonify({
            "nim": nim,
            "belum_mengembalikan_buku": count > 0,
            "jumlah": count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5004)
