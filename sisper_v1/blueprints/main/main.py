from flask import Blueprint, render_template, session, flash, redirect

main_bp = Blueprint('main', __name__)


@main_bp.route("/dashboard")
def dashboard():
    if "nim" not in session and "admin" not in session:
        flash('Anda harus login terlebih dahulu', 'error')
        return redirect("/")
    return render_template(
        "dashboard.html",
        nim=session["nim"] if "nim" in session else session["admin"],
        nama=session["nama"]
    )
