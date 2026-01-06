from time import sleep

from flask import Flask, jsonify, request
import redis
import json
from db import get_db_conn
from config import REDIS_CONFIG
from config import LOAD_TIME

app = Flask(__name__)
redis_client = redis.Redis(**REDIS_CONFIG)


def handle_book_event(event_type, data):
    from db import get_db
    db = get_db()
    try:
        cur = db.cursor()
        if event_type == "book_added":
            cur.execute("""
                        INSERT INTO buku (isbn, judul, penulis, status)
                        VALUES (%s, %s, %s, 'tersedia') ON DUPLICATE KEY
                        UPDATE judul=%s, penulis=%s
                        """, (data["isbn"], data["judul"], data["penulis"], data["judul"], data["penulis"]))
        elif event_type == "book_updated":
            cur.execute("""
                        UPDATE buku
                        SET judul=%s,
                            penulis=%s
                        WHERE isbn = %s
                        """, (data["judul"], data["penulis"], data["isbn_original"]))
        elif event_type == "book_deleted":
            cur.execute("UPDATE buku SET waktu_hapus = now() WHERE isbn=%s", (data["isbn"],))
        elif event_type == "book_status_updated":
            cur.execute("UPDATE buku SET status = %s WHERE isbn = %s", (data["status"], data["isbn"]))
        elif event_type == "book_searched":
            cur.execute("""
                        INSERT INTO riwayat_pencarian (nim, kata_kunci)
                        VALUES (%s, %s)
                        """, (data["nim"], data["keyword"]))

        db.commit()
        print(f"Processed book event {event_type}")
    except Exception as e:
        print(f"Error processing book event in DB: {e}")
    finally:
        db.close()


def start_subscriber():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("book_events")
    print("Subscribed to mahasiswa_events and book_events channels...")
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                payload = json.loads(message["data"])
                event_type = payload.get("event")
                if event_type in ["book_added", "book_updated", "book_deleted", "book_status_updated",
                                  "book_searched"]:
                    print(f"Received book event {event_type}...")
                    handle_book_event(
                        event_type,
                        payload.get("data") if event_type != "book_searched" else payload.get("data")
                    )
                    # Note: book_searched data is already the inner dict
            except Exception as e:
                print(f"Error processing Redis message: {e}")


import threading

subscriber_thread = threading.Thread(target=start_subscriber, daemon=True)
subscriber_thread.start()


@app.route("/rekomendasi", methods=["POST"])
def rekomendasi():
    # simulate high load
    sleep(LOAD_TIME)
    # --------------
    data = request.get_json()
    if not data or "nim" not in data:
        return jsonify({"error": "NIM is required"}), 400

    nim = data["nim"]
    db = get_db_conn()
    cur = db.cursor()
    try:
        # Get search history for this student
        cur.execute("SELECT kata_kunci FROM riwayat_pencarian WHERE nim = %s ORDER BY waktu_cari DESC LIMIT 10", (nim,))
        history = cur.fetchall()

        if not history:
            # Default recommendation: most recent available books if no history
            cur.execute(
                "SELECT * FROM buku WHERE status = 'tersedia' AND waktu_hapus IS NULL ORDER BY isbn DESC LIMIT 5")
            books = cur.fetchall()
            return jsonify(books)

        # Build query based on keywords
        keywords = [h["kata_kunci"] for h in history]

        # Simple recommendation logic: find books matching any of the recent keywords
        # and currently available
        query = "SELECT * FROM buku WHERE status = 'tersedia' AND waktu_hapus IS NULL AND ("
        clauses = []
        params = []
        for kw in keywords:
            clauses.append("judul LIKE %s OR penulis LIKE %s")
            params.extend([f"%{kw}%", f"%{kw}%"])

        query += " OR ".join(clauses) + ") GROUP BY isbn LIMIT 5"

        cur.execute(query, tuple(params))
        recommendations = cur.fetchall()

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5005)
