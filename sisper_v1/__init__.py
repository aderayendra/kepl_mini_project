from flask import Flask
from .db import close_db
from .blueprints.auth.auth import auth_bp
from .blueprints.buku.buku import buku_bp
from .blueprints.peminjaman.peminjaman import peminjaman_bp
from .blueprints.mahasiswa.mahasiswa import mahasiswa_bp
from .blueprints.main.main import main_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "KZN-%d""7A[3J(90e$AF6~O#Z8grVsqqUuuf{#Qy>}URL_;ZEJnOz/-vP+*^EPE"

    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(buku_bp)
    app.register_blueprint(peminjaman_bp)
    app.register_blueprint(mahasiswa_bp)
    app.register_blueprint(main_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
