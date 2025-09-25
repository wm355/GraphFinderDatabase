from app import create_app, db
from app.models import Item

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    items = [
        Item(name="Iron", description="Fe, metal, common in steels"),
        Item(name="Wood", description="Organic material from trees"),
        Item(name="Copper", description="Cu, conductive metal"),
        Item(name="Graphite", description="Carbon allotrope, soft and conductive"),
    ]
    db.session.add_all(items)
    db.session.commit()
    print("Seeded!")
