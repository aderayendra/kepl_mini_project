import requests
from flask import Blueprint, render_template, session, flash, redirect

REKOMENDASI_SERVICE_URL = "http://127.0.0.1:5005"

main_bp = Blueprint('main', __name__)


@main_bp.route("/dashboard")
def dashboard():
    if "nim" not in session and "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")

    rekomendasi = []
    if "nim" in session:
        try:
            url = f"{REKOMENDASI_SERVICE_URL}/rekomendasi"
            response = requests.post(url, json={"nim": session["nim"]})
            rekomendasi = response.json()
            if isinstance(rekomendasi, dict) and "error" in rekomendasi:
                rekomendasi = []
        except Exception as e:
            print(f"Error fetching recommendations: {e}")

    return render_template(
        "dashboard.html",
        nim=session["nim"] if "nim" in session else session["admin"],
        nama=session["nama"],
        rekomendasi=rekomendasi
    )
