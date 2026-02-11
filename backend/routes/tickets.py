"""
Tickets API Routes
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import base64
import os

from models import get_session, Customer, Ticket, TicketType, TicketStatus

router = APIRouter()


class TicketCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    ticket_type: TicketType
    payment_method: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    code: str
    ticket_type: str
    status: str
    price: int
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    payment_method: Optional[str]
    payment_proof: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TicketApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None


class TicketActivation(BaseModel):
    code: str
    phone: str
    name: str
    email: Optional[str] = None


@router.post("/", response_model=dict)
async def create_ticket(ticket_data: TicketCreate):
    """Create a new ticket reservation"""
    session = get_session()
    try:
        # Check if customer exists
        customer = session.query(Customer).filter(Customer.phone == ticket_data.phone).first()
        
        if not customer:
            customer = Customer(
                name=ticket_data.name,
                phone=ticket_data.phone,
                email=ticket_data.email
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)
        
        # Get price based on ticket type
        vip_price = int(os.getenv("VIP_PRICE", 500))
        student_price = int(os.getenv("STUDENT_PRICE", 100))
        price = vip_price if ticket_data.ticket_type == TicketType.VIP else student_price
        
        # Generate unique code
        code = Ticket.generate_unique_code(session)
        
        # Create ticket
        ticket = Ticket(
            code=code,
            ticket_type=ticket_data.ticket_type,
            price=price,
            customer_id=customer.id,
            payment_method=ticket_data.payment_method,
            status=TicketStatus.PENDING
        )
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        
        return {
            "success": True,
            "ticket_id": ticket.id,
            "code": ticket.code,
            "price": ticket.price,
            "message": f"تم إنشاء حجز تذكرة {ticket_data.ticket_type.value} بنجاح"
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/check/{phone}")
async def check_customer_tickets(phone: str):
    """Check if a phone number has existing tickets"""
    session = get_session()
    try:
        customer = session.query(Customer).filter(Customer.phone == phone).first()
        
        if not customer:
            return {
                "has_tickets": False,
                "tickets": [],
                "message": "لم يتم العثور على حجوزات سابقة لهذا الرقم"
            }
        
        tickets = session.query(Ticket).filter(Ticket.customer_id == customer.id).all()
        
        return {
            "has_tickets": len(tickets) > 0,
            "customer_name": customer.name,
            "tickets": [
                {
                    "id": t.id,
                    "code": t.code,
                    "type": t.ticket_type.value,
                    "status": t.status.value,
                    "price": t.price
                } for t in tickets
            ],
            "message": f"تم العثور على {len(tickets)} تذكرة لهذا الرقم"
        }
    finally:
        session.close()


@router.get("/", response_model=List[dict])
async def get_all_tickets(status: Optional[str] = None):
    """Get all tickets with optional status filter"""
    session = get_session()
    try:
        query = session.query(Ticket).join(Customer)
        
        if status:
            query = query.filter(Ticket.status == status)
        
        tickets = query.order_by(Ticket.created_at.desc()).all()
        
        return [
            {
                "id": t.id,
                "code": t.code,
                "ticket_type": t.ticket_type.value,
                "status": t.status.value,
                "price": t.price,
                "customer_name": t.customer.name,
                "customer_phone": t.customer.phone,
                "customer_email": t.customer.email,
                "payment_method": t.payment_method,
                "payment_proof": t.payment_proof,
                "created_at": t.created_at.isoformat()
            } for t in tickets
        ]
    finally:
        session.close()


@router.post("/{ticket_id}/payment-proof")
async def upload_payment_proof(ticket_id: int, file: UploadFile = File(...)):
    """Upload payment proof image"""
    session = get_session()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="التذكرة غير موجودة")
        
        # Read and encode image
        content = await file.read()
        encoded = base64.b64encode(content).decode('utf-8')
        
        ticket.payment_proof = f"data:{file.content_type};base64,{encoded}"
        ticket.status = TicketStatus.PAYMENT_SUBMITTED
        session.commit()
        
        return {
            "success": True,
            "message": "تم رفع إثبات الدفع بنجاح، في انتظار المراجعة"
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


from fastapi import BackgroundTasks

@router.post("/{ticket_id}/approve")
async def approve_ticket(ticket_id: int, approval: TicketApproval, background_tasks: BackgroundTasks, admin_id: int = 1):
    """Approve or reject a ticket"""
    session = get_session()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="التذكرة غير موجودة")
        
        if approval.approved:
            ticket.status = TicketStatus.APPROVED
            ticket.approved_by = admin_id
            ticket.approved_at = datetime.utcnow()
            message = "تم اعتماد التذكرة بنجاح"
            
            # Prepare data for n8n
            ticket_data = {
                "ticket_id": ticket.id,
                "phone": ticket.customer.phone,
                "name": ticket.customer.name,
                "code": ticket.code,
                "ticket_type": ticket.ticket_type.value,
                "price": ticket.price,
                "event_date": os.getenv("EVENT_DATE", "2026-02-11"),
                "location": os.getenv("EVENT_LOCATION", "سوهاج"),
                "pdf_url": f"http://localhost:8000/api/tickets/{ticket.id}/pdf" # Adjust domain in n8n if needed
            }
            
            # Trigger n8n workflow in background
            from services.n8n_client import trigger_ticket_approved_workflow
            background_tasks.add_task(trigger_ticket_approved_workflow, ticket_data)
            
        else:
            ticket.status = TicketStatus.REJECTED
            ticket.rejection_reason = approval.rejection_reason
            message = "تم رفض التذكرة"
        
        session.commit()
        
        return {
            "success": True,
            "status": ticket.status.value,
            "message": message
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/activate")
async def activate_ticket(activation: TicketActivation):
    """Activate an offline ticket by code"""
    session = get_session()
    try:
        ticket = session.query(Ticket).filter(Ticket.code == activation.code).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="كود التذكرة غير صحيح")
        
        if ticket.status == TicketStatus.ACTIVATED:
            return {
                "success": False,
                "message": "هذه التذكرة مفعّلة بالفعل",
                "activated_phone": ticket.customer.phone
            }
        
        # Check if already linked to another phone
        if ticket.customer.phone and ticket.customer.phone != activation.phone:
            return {
                "success": False,
                "message": "هذه التذكرة مرتبطة برقم هاتف آخر"
            }
        
        # Update customer info and activate
        ticket.customer.name = activation.name
        ticket.customer.phone = activation.phone
        ticket.customer.email = activation.email
        ticket.status = TicketStatus.ACTIVATED
        
        session.commit()
        
        return {
            "success": True,
            "ticket_type": ticket.ticket_type.value,
            "message": "تم تفعيل التذكرة بنجاح! نراك في الإيفنت 🎉"
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: int):
    """Get ticket details by ID"""
    session = get_session()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="التذكرة غير موجودة")
        
        return {
            "id": ticket.id,
            "code": ticket.code,
            "ticket_type": ticket.ticket_type.value,
            "status": ticket.status.value,
            "price": ticket.price,
            "customer": {
                "name": ticket.customer.name,
                "phone": ticket.customer.phone,
                "email": ticket.customer.email
            },
            "payment_method": ticket.payment_method,
            "created_at": ticket.created_at.isoformat()
        }
    finally:
        session.close()


@router.get("/{ticket_id}/pdf")
async def download_ticket_pdf(ticket_id: int):
    """Download ticket as PDF"""
    from fastapi.responses import Response
    from services.pdf_generator import generate_ticket_pdf
    
    session = get_session()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="التذكرة غير موجودة")
        
        # Only allow download for approved or activated tickets
        if ticket.status not in [TicketStatus.APPROVED, TicketStatus.ACTIVATED]:
            raise HTTPException(status_code=400, detail="التذكرة غير معتمدة بعد")
        
        pdf_bytes = generate_ticket_pdf(
            ticket_code=ticket.code,
            ticket_type=ticket.ticket_type.value,
            customer_name=ticket.customer.name,
            price=ticket.price
        )
        
        filename = f"ticket_{ticket.code}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    finally:
        session.close()

