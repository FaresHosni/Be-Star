import sqlite3
import os

# Database path
DB_PATH = 'backend/data/bestar.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Migrating database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(tickets)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'guest_name' not in columns:
            print("Adding guest_name column to tickets table...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN guest_name VARCHAR(100)")
            conn.commit()
            print("Migration successful: guest_name column added.")
        else:
            print("Column guest_name already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
