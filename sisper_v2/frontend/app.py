from flask import Flask
from blueprints.auth.auth import auth_bp
from blueprints.buku.buku import buku_bp
from blueprints.peminjaman.peminjaman import peminjaman_bp
from blueprints.mahasiswa.mahasiswa import mahasiswa_bp
from blueprints.main.main import main_bp


def create_app():
    flask_app = Flask(__name__)
    flask_app.secret_key = "KZN-%d""7A[3J(90e$AF6~O#Z8grVsqqUuuf{#Qy>}URL_;ZEJnOz/-vP+*^EPE"

    # Register Blueprints
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(buku_bp)
    flask_app.register_blueprint(peminjaman_bp)
    flask_app.register_blueprint(mahasiswa_bp)
    flask_app.register_blueprint(main_bp)

    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5006)
