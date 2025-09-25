from app import create_app, db  # import your app and db from the Flask app

app = create_app()

# Create the tables based on models
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
