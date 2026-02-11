# -*- coding: utf-8 -*-
"""Add test tickets with proper Arabic encoding"""

import sys
sys.path.insert(0, '.')

from models import get_session, Customer, Ticket, TicketType, TicketStatus
import random
import string

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def add_test_tickets():
    session = get_session()
    
    # Clear existing test tickets
    session.query(Ticket).delete()
    session.query(Customer).delete()
    session.commit()
    
    # Add test customers and tickets
    test_data = [
        {
            "name": "أحمد محمد",
            "phone": "01012345678",
            "email": "ahmed@example.com",
            "ticket_type": TicketType.VIP,
            "payment_method": "vodafone_cash",
            "status": TicketStatus.PENDING
        },
        {
            "name": "سارة علي",
            "phone": "01098765432",
            "email": "sara@example.com",
            "ticket_type": TicketType.STUDENT,
            "payment_method": "instapay",
            "status": TicketStatus.APPROVED
        },
        {
            "name": "محمود حسن",
            "phone": "01155556666",
            "email": "mahmoud@example.com",
            "ticket_type": TicketType.VIP,
            "payment_method": "vodafone_cash",
            "status": TicketStatus.REJECTED
        },
        {
            "name": "فاطمة أحمد",
            "phone": "01277778888",
            "email": "fatma@example.com",
            "ticket_type": TicketType.STUDENT,
            "payment_method": "instapay",
            "status": TicketStatus.PENDING
        }
    ]
    
    prices = {TicketType.VIP: 500, TicketType.STUDENT: 100}
    
    for data in test_data:
        # Create customer
        customer = Customer(
            name=data["name"],
            phone=data["phone"],
            email=data["email"]
        )
        session.add(customer)
        session.flush()
        
        # Create ticket
        ticket = Ticket(
            customer_id=customer.id,
            ticket_type=data["ticket_type"],
            code=generate_code(),
            status=data["status"],
            price=prices[data["ticket_type"]],
            payment_method=data["payment_method"]
        )
        session.add(ticket)
    
    session.commit()
    print("Added 4 test tickets successfully!")
    print("   - Ahmed Mohamed (VIP) - Pending")
    print("   - Sara Ali (Student) - Approved")
    print("   - Mahmoud Hassan (VIP) - Rejected")
    print("   - Fatma Ahmed (Student) - Pending")
    session.close()

if __name__ == "__main__":
    add_test_tickets()
