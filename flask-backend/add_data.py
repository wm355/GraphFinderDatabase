from app import create_app, db
from app.models import Item

app = create_app()

with app.app_context():
    # Create new items
    item1 = Item(name="Iron")
    item2 = Item(name="Wood")

    # Add items to the database
    db.session.add(item1)
    db.session.add(item2)

    # Commit the changes to the database
    db.session.commit()

    print("Items added successfully!")
