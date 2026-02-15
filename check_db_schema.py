
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Force database path to correct location
os.environ["DATABASE_URL"] = "sqlite:///backend/data/bestar.db"

from sqlalchemy import create_engine, inspect, text
from backend.models import Admin, get_database_url

def check_schema():
    print("Checking database schema...")
    db_url = get_database_url()
    
    # Override because get_database_url might ignore env var if not set properly or if default takes precedence
    # Actually models.py uses os.getenv("DATABASE_URL", ...) so it should work.
    # But just in case, verify the path exists.
    
    db_path = os.path.join("backend", "data", "bestar.db")
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    print(f"Database URL: {db_url}")
    
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    if 'admins' not in inspector.get_table_names():
        print("Error: 'admins' table not found!")
        return
    
    columns = [col['name'] for col in inspector.get_columns('admins')]
    print(f"Columns in 'admins' table: {columns}")
    
    if 'is_active' in columns:
        print("Success: 'is_active' column exists.")
    else:
        print("Error: 'is_active' column is MISSING!")
        
        # Try to migrate
        print("Attempting to add 'is_active' column...")
        with engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE admins ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                conn.commit()
                print("Migration successful: 'is_active' column added.")
            except Exception as e:
                print(f"Migration failed: {e}")

    # Check if we can query admins
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM admins")).fetchall()
            print(f"Number of admins found: {len(result)}")
            for row in result:
                print(row)
    except Exception as e:
        print(f"Error querying admins: {e}")

if __name__ == "__main__":
    check_schema()
