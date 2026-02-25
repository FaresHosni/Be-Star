"""
Statistics API Routes
"""
from fastapi import APIRouter
from sqlalchemy import func

from models import get_session, Ticket, Customer, TicketType, TicketStatus, safe_value

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    session = get_session()
    try:
        # Total tickets
        total_tickets = session.query(func.count(Ticket.id)).scalar() or 0
        
        # By status
        pending = session.query(func.count(Ticket.id)).filter(
            func.lower(Ticket.status) == 'pending'
        ).scalar() or 0
        
        payment_submitted = session.query(func.count(Ticket.id)).filter(
            func.lower(Ticket.status) == 'payment_submitted'
        ).scalar() or 0
        
        approved = session.query(func.count(Ticket.id)).filter(
            func.lower(Ticket.status) == 'approved'
        ).scalar() or 0
        
        rejected = session.query(func.count(Ticket.id)).filter(
            func.lower(Ticket.status) == 'rejected'
        ).scalar() or 0
        
        activated = session.query(func.count(Ticket.id)).filter(
            func.lower(Ticket.status) == 'activated'
        ).scalar() or 0
        
        # By type
        vip_count = session.query(func.count(Ticket.id)).filter(
            func.upper(Ticket.ticket_type) == 'VIP'
        ).scalar() or 0
        
        student_count = session.query(func.count(Ticket.id)).filter(
            func.upper(Ticket.ticket_type) == 'STUDENT'
        ).scalar() or 0
        
        # Revenue
        total_revenue = session.query(func.sum(Ticket.price)).filter(
            func.lower(Ticket.status).in_(['approved', 'activated'])
        ).scalar() or 0
        
        # Customers count
        total_customers = session.query(func.count(Customer.id)).scalar() or 0
        
        return {
            "total_tickets": total_tickets,
            "by_status": {
                "pending": pending,
                "payment_submitted": payment_submitted,
                "approved": approved,
                "rejected": rejected,
                "activated": activated
            },
            "by_type": {
                "vip": vip_count,
                "student": student_count
            },
            "total_revenue": total_revenue,
            "total_customers": total_customers
        }
    finally:
        session.close()


@router.get("/recent-tickets")
async def get_recent_tickets(limit: int = 10):
    """Get recent tickets"""
    session = get_session()
    try:
        tickets = session.query(Ticket).join(Customer).order_by(
            Ticket.created_at.desc()
        ).limit(limit).all()
        
        results = []
        for t in tickets:
            try:
                ticket_type = safe_value(t.ticket_type)
                status = safe_value(t.status)
                
                results.append({
                    "id": t.id,
                    "code": t.code,
                    "customer_name": t.customer.name,
                    "ticket_type": ticket_type,
                    "status": status,
                    "price": t.price,
                    "created_at": t.created_at.isoformat()
                })
            except Exception:
                continue
        return results
    finally:
        session.close()
