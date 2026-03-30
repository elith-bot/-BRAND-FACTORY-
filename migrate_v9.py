import os
from main import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE site_content ADD COLUMN menu_left_style TEXT"))
                conn.execute(text("ALTER TABLE site_content ADD COLUMN menu_right_style TEXT"))
                conn.commit()
                print("Successfully added style columns to site_content table.")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
