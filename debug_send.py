import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from models import get_session, Ticket, TicketStatus, Question, Customer, QuizGroupMember

def debug_send():
    # Fix DB path for Windows execution context
    db_path = os.path.join(os.getcwd(), 'backend', 'data', 'bestar.db')
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    # Mock get_database_url if needed or rely on env being set correctly if get_session uses it
    # But get_session uses get_database_url() which defaults to sqlite:///./data/bestar.db
    # We need to override it or set env var
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    session = get_session()
    try:
        print("--- Debugging Send Question ---")
        
        # 1. Check Questions
        questions = session.query(Question).all()
        print(f"Total Questions: {len(questions)}")
        for q in questions:
            print(f"Q[{q.id}]: Target Groups = '{q.target_groups}' (Raw)")
            try:
                targets = json.loads(q.target_groups)
                print(f"       Parsed: {targets}")
            except:
                print("       Failed to parse JSON")
                targets = ["all"]
        
        # 2. Check Tickets Query (Replicating _get_target_phones logic)
        print("\n--- Checking 'all' target ---")
        tickets = session.query(Ticket).filter(
            Ticket.status.in_([TicketStatus.APPROVED, TicketStatus.ACTIVATED]),
            Ticket.is_hidden == False
        ).all()
        
        print(f"Tickets found with status IN ('{TicketStatus.APPROVED.value}', '{TicketStatus.ACTIVATED.value}'): {len(tickets)}")
        
        for t in tickets:
            phone = t.customer.phone if t.customer else "No Customer"
            print(f"Ticket[{t.id}]: Status='{t.status}' | Hidden={t.is_hidden} | Phone={phone}")
            
        # 3. Check Raw DB values for Status
        print("\n--- Raw DB Status Values ---")
        import sqlite3
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        rows = c.execute("SELECT id, status FROM tickets").fetchall()
        for r in rows:
            print(f"ID {r[0]}: '{r[1]}'")
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    debug_send()
