from . import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    description = db.Column(db.Text, default="")
    # You can add more columns later (e.g., density, color, etc.)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}
