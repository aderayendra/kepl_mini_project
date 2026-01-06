from time import sleep

from flask import Flask, jsonify, request
import redis
import json
from db import get_db_conn
from config import REDIS_CONFIG, LOAD_TIME

import threading

app = Flask(__name__)
redis_client = redis.Redis(**REDIS_CONFIG)


def handle_book_status_update(data):
    isbn = data.get("isbn")
    status = data.get("status")
    if not isbn or not status:
        return

    from db import get_db
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE buku SET status = %s WHERE isbn = %s",
            (status, isbn)
        )
        db.commit()
        print(f"Updated book {isbn} status to {status}")
    except Exception as e:
        print(f"Error updating book status in DB: {e}")
    finally:
        db.close()


def start_subscriber():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("book_events")
    print("Subscribed to book_events channel...")
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                payload = json.loads(message["data"])
                if payload.get("event") == "book_status_updated":
                    print(f"Received book_status_updated event for ISBN {payload.get('data').get('isbn')}")
                    handle_book_status_update(payload.get("data"))
            except Exception as e:
                print(f"Error processing Redis message: {e}")


# Start subscriber in a background thread
subscriber_thread = threading.Thread(target=start_subscriber, daemon=True)
subscriber_thread.start()


def publish_book_event(event_type, data):
    try:
        event_payload = {
            "event": event_type,
            "data": data
        }
        print(f"Publishing book event {event_type} with payload {event_payload}")
        redis_client.publish("book_events", json.dumps(event_payload))
    except Exception as e:
        print(f"Error publishing to Redis: {e}")


@app.route("/buku", methods=["POST"])
def buku():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    data = request.get_json() or {}
    search_keyword = data.get('s')
    nim = data.get('nim')

    db = get_db_conn()
    cur = db.cursor()
    try:
        if search_keyword:
            if nim:
                publish_book_event("book_searched", {"nim": nim, "keyword": search_keyword})
            cur.execute(
                """
                SELECT b.*
                FROM buku b
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
                SELECT b.*
                FROM buku b
                WHERE b.waktu_hapus IS NULL
                GROUP BY b.isbn
                """,
            )
            buku_list = cur.fetchall()

        for b in buku_list:
            if b.get('waktu_edit'):
                b['waktu_edit'] = b['waktu_edit'].strftime('%Y-%m-%d %H:%M:%S')
            if b.get('waktu_input'):
                b['waktu_input'] = b['waktu_input'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(buku_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/buku/tambah", methods=["POST"])
def buku_tambah():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO buku (isbn, judul, penulis, kategori, sinopsis, tahun, status) VALUES (%s, %s, %s, %s, %s, %s, 'tersedia')",
            (
                data["isbn"],
                data["judul"],
                data["penulis"],
                data["kategori"],
                data["sinopsis"],
                data["tahun"]
            )
        )
        db.commit()
        publish_book_event("book_added", data)
        return jsonify({"message": "Buku berhasil ditambahkan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/buku/edit', methods=['POST'])
def edit_buku():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    isbn_original = data['isbn_original']
    judul = data['judul']
    penulis = data['penulis']
    kategori = data['kategori']
    sinopsis = data['sinopsis']
    tahun = data['tahun']
    db = get_db_conn()
    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE buku SET judul=%s, penulis=%s, kategori=%s, sinopsis=%s, tahun=%s, waktu_edit=now() WHERE isbn=%s",
            (judul, penulis, kategori, sinopsis, tahun, isbn_original)
        )
        db.commit()
        publish_book_event("book_updated", data)
        return jsonify({"message": "Buku berhasil diupdate!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/buku/hapus', methods=['DELETE'])
def hapus_buku():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    isbn = request.args.get('isbn')
    if not isbn:
        return jsonify({"error": "ISBN is required"}), 400

    db = get_db_conn()
    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE buku SET waktu_hapus = now() WHERE isbn=%s",
            isbn
        )
        db.commit()
        publish_book_event("book_deleted", {"isbn": isbn})
        return jsonify({"message": "Buku berhasil dihapus!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5003)
