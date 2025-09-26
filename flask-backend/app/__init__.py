# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 👇 Point this to your actual folder that contains the type/element subfolders
    app.config["DATA_ROOT"] = os.getenv(
        "DATA_ROOT",
        r"C:\Users\willi\DatabaseProject\flask-backend\input"  # <-- adjust to your real root
    )

    db.init_app(app)
    # Allow GitHub Pages and localhost for development
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:8080",
        "https://wm355.github.io"
    ]
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    from .routes import main as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    print("DATA_ROOT:", app.config["DATA_ROOT"])  # helpful log
    return app
