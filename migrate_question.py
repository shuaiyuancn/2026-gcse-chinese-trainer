from main import db
from sqlalchemy import text

def migrate():
    print("Migrating question table...")
    try:
        with db.conn.begin():
             db.conn.execute(text("ALTER TABLE question RENAME COLUMN title TO theme;"))
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
