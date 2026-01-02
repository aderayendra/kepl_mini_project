import requests
from flask import Blueprint, render_template, request, redirect, session, flash

PENGGUNA_SERVICE_URL = "http://127.0.0.1:5002"

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if "nim" in session or "admin" in session:
        return redirect("/dashboard")

    if request.method != "POST":
        session.clear()
        return render_template('login.html')

    nim = request.form["nim"]
    password = request.form["password"]
    jenis = request.form["jenis"]

    try:
        url = f"{PENGGUNA_SERVICE_URL}/login"
        payload = {"nim": nim, "password": password, "jenis": jenis}
        response = requests.post(url, json=payload)
        response_json = response.json()

        if response_json.get("authenticated"):
            user = response_json["user"]
            if user["jenis"] == "admin":
                session["admin"] = user["username"]
            else:
                session["nim"] = user["nim"]

            session["nama"] = user["nama"]
            return redirect("/dashboard")

        flash(response_json.get("error", "Login gagal"), "error")
    except Exception as e:
        flash(f'Error connecting to service: {e}', 'error')

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
