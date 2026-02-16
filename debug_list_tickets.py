import sys
import os
import datetime

# Fix DB path
db_path = os.path.join(os.getcwd(), 'backend', 'data', 'bestar.db')
if os.path.exists(db_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from models import get_session, Ticket, Customer, TicketType, TicketStatus
from sqlalchemy import func

def debug_list():
    session = get_session()
    try:
        print("--- Debugging List Tickets ---")
        
        # 1. Query count before join
        count_all = session.query(Ticket).count()
        print(f"Total Tickets in DB: {count_all}")
        
        # 2. Query with join
        query = session.query(Ticket).join(Customer)
        joined_count = query.count()
        print(f"Tickets after JOIN Customer: {joined_count}")
        
        if count_all > joined_count:
            print("WARNING: Some tickets are lost due to JOIN (Orphaned tickets).")
            # Find orphans
            orphans = session.query(Ticket).outerjoin(Customer).filter(Customer.id == None).all()
            print(f"Orphaned Ticket IDs: {[t.id for t in orphans]}")
        
        # 3. Fetch and Serialize
        tickets = query.order_by(Ticket.created_at.desc()).all()
        print(f"Fetched {len(tickets)} tickets for serialization.")
        
        success_count = 0
        for i, t in enumerate(tickets):
            try:
                # Replicating the logic from tickets.py
                data = {
                    "id": t.id,
                    "code": t.code,
                    "ticket_type": t.ticket_type.value if hasattr(t.ticket_type, 'value') else str(t.ticket_type),
                    "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                    "price": t.price,
                    "customer_name": t.guest_name if t.guest_name else t.customer.name,
                    "customer_phone": t.customer.phone,
                    "customer_email": t.customer.email,
                    "payment_method": t.payment_method,
                    "payment_proof": t.payment_proof[:20] + "..." if t.payment_proof else None,
                    "created_at": t.created_at.isoformat()
                }
                if i < 3: # Print first 3
                    print(f"Serialized Ticket {t.id}: {data}")
                success_count += 1
            except Exception as e:
                print(f"FAILED to serialize Ticket {t.id}: {e}")
                # Debug the problematic fields
                print(f"   t.status type: {type(t.status)}, value: {t.status}")
                print(f"   t.ticket_type type: {type(t.ticket_type)}, value: {t.ticket_type}")

        print(f"Successfully serialized {success_count}/{len(tickets)} tickets.")

    except Exception as e:
        print(f"Global Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    debug_list()
