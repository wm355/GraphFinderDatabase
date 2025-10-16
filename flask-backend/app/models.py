from . import db
from flask_sqlalchemy import SQLAlchemy

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    description = db.Column(db.Text, default="")
    # You can add more columns later (e.g., density, color, etc.)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}

db = SQLAlchemy()  # keep your existing instance if already present

class Upload(db.Model):
    __tablename__ = "uploads"
    id = db.Column(db.Integer, primary_key=True)
    dopant = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(16))              # "heating" | "cooling" | ""
    group_key = db.Column(db.String(255))
    data_type = db.Column(db.String(64))  
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
