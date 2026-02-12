from sqlalchemy import text
from models import create_db_engine, Base

def update_schema():
    engine = create_db_engine()
    connection = engine.connect()
    
    print("Checking database schema...")
    
    # 1. Create new User Drafts table
    # This works if table doesn't exist
    Base.metadata.create_all(bind=engine)
    print("Created missing tables (e.g. ticket_drafts).")
    
    # 2. Add column 'guest_phone' to 'tickets' table manually if not exists
    # Check if column exists
    try:
        # Simple check by selecting it
        connection.execute(text("SELECT guest_phone FROM tickets LIMIT 1"))
        print("Column 'guest_phone' already exists in 'tickets'.")
    except Exception:
        print("Column 'guest_phone' missing. Adding it...")
        try:
            # SQLite and Postgres syntax for ADD COLUMN is similar
            connection.execute(text("ALTER TABLE tickets ADD COLUMN guest_phone VARCHAR(20)"))
            connection.commit() # Important for some drivers
            print("Successfully added 'guest_phone' to 'tickets'.")
        except Exception as e:
            print(f"Error adding column: {e}")
            
    connection.close()

if __name__ == "__main__":
    update_schema()
