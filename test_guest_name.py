import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, Ticket, Customer, TicketType, TicketStatus

# Setup DB connection
DATABASE_URL = "sqlite:///backend/data/bestar.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

def test_booking(phone, name, email):
    print(f"\n--- Testing booking for {name} ({phone}) ---")
    
    # 1. Check/Create Customer
    customer = session.query(Customer).filter(Customer.phone == phone).first()
    if not customer:
        print("Creating new customer")
        customer = Customer(name=name, phone=phone, email=email)
        session.add(customer)
        session.commit()
    else:
        print(f"Customer exists: {customer.name}")
        # Logic from tickets.py: Update email but NOT name
        if email:
            customer.email = email
        session.commit()
        
    print(f"Customer DB State -> Name: {customer.name}, Phone: {customer.phone}")

    # 2. Create Ticket with guest_name
    code = Ticket.generate_unique_code(session)
    ticket = Ticket(
        code=code,
        ticket_type=TicketType.VIP,
        price=500,
        customer_id=customer.id,
        guest_name=name,  # THIS IS THE KEY FIELD
        payment_method="Vodafone Cash",
        status=TicketStatus.PENDING
    )
    session.add(ticket)
    session.commit()
    
    # 3. Verify
    saved_ticket = session.query(Ticket).filter(Ticket.code == code).first()
    print(f"Ticket Saved -> Code: {saved_ticket.code}, Customer: {saved_ticket.customer.name}, GUEST NAME: {saved_ticket.guest_name}")
    
    if saved_ticket.guest_name == name:
        print("✅ SUCCESS: Guest name saved correctly.")
    else:
        print("❌ FAILURE: Guest name mismatch!")

try:
    # Test Case 1: First booking
    test_booking("201234567890", "Ahmed First", "ahmed@test.com")
    
    # Test Case 2: Same phone, DIFFERENT name
    test_booking("201234567890", "Mohamed Second", "mohamed@test.com")
    
finally:
    session.close()
