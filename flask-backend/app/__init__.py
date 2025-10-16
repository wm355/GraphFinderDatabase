# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def _normalize_db_url(url: str) -> str:
    # Optional nicety: Heroku-style DATABASE_URL uses postgres://
    # SQLAlchemy expects postgresql://
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

def create_app():
    app = Flask(__name__)

    # --- Database config ---
    raw_db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = _normalize_db_url(raw_db_url)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- File storage roots ---
    # We keep a single base (input/) and use it for BOTH reading (DATA_ROOT)
    # and writing uploads (UPLOAD_ROOT). That way new uploads immediately
    # appear to any code that scans input/.
    here = os.path.dirname(__file__)
    default_root = os.path.abspath(os.path.join(here, "..", "input"))

    # Allow override via env if you deploy somewhere else
    data_root = os.getenv("DATA_ROOT", default_root)
    app.config["DATA_ROOT"] = data_root
    app.config["UPLOAD_ROOT"] = data_root  # keep them identical

    # Ensure the folder structure exists
    os.makedirs(app.config["DATA_ROOT"], exist_ok=True)
    for sub in ("resistance_temp", "transmittance_temp"):
        os.makedirs(os.path.join(app.config["DATA_ROOT"], sub), exist_ok=True)

    # --- Extensions ---
    db.init_app(app)

    # CORS (adjust as needed)
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:8080",
        "https://wm355.github.io",
    ]
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # --- Routes/Blueprints ---
    # Make sure your blueprint in routes.py matches this import and has url_prefix="/api"
    # e.g., in routes.py: bp = Blueprint("api", __name__)
    from .routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # --- DB create ---
    with app.app_context():
        db.create_all()

    # Helpful logs
    print("SQLALCHEMY_DATABASE_URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    print("DATA_ROOT:", app.config["DATA_ROOT"])
    print("UPLOAD_ROOT:", app.config["UPLOAD_ROOT"])
    return app
