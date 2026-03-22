import sqlite3
import os

def migrate():
    db_path = 'instance/database.db'
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List of new color columns to add
    new_columns = [
        ('hero_title_color', "TEXT DEFAULT '#ffffff'"),
        ('hero_text_color', "TEXT DEFAULT '#ffffff'"),
        ('hero_btn_bg_color', "TEXT DEFAULT '#6B21C8'"),
        ('hero_btn_text_color', "TEXT DEFAULT '#FDCC04'"),
        
        ('section2_title_color', "TEXT DEFAULT '#ffffff'"),
        ('section2_text_color', "TEXT DEFAULT '#ffffff'"),
        ('section2_btn_bg_color', "TEXT DEFAULT '#6B21C8'"),
        ('section2_btn_text_color', "TEXT DEFAULT '#FDCC04'"),
        
        ('about_title_color', "TEXT DEFAULT '#ffffff'"),
        ('about_text_color', "TEXT DEFAULT '#ffffff'"),
        ('about_btn_bg_color', "TEXT DEFAULT '#6B21C8'"),
        ('about_btn_text_color', "TEXT DEFAULT '#FDCC04'"),
        
        ('learning_title_color', "TEXT DEFAULT '#ffffff'"),
        ('learning_text_color', "TEXT DEFAULT '#ffffff'"),
        ('learning_btn_bg_color', "TEXT DEFAULT '#6B21C8'"),
        ('learning_btn_text_color', "TEXT DEFAULT '#FDCC04'"),
        
        ('contact_title_color', "TEXT DEFAULT '#ffffff'"),
        ('contact_text_color', "TEXT DEFAULT '#ffffff'"),
        ('contact_btn_bg_color', "TEXT DEFAULT '#6B21C8'"),
        ('contact_btn_text_color', "TEXT DEFAULT '#FDCC04'")
    ]

    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE site_content ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration v4 completed.")

if __name__ == "__main__":
    migrate()
