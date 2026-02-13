"""
Be Star - Live Engagement Agent API
Manage real-time engagement with event attendees
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import base64
import logging

from models import get_session, Ticket, TicketStatus, Customer

# WhatsApp Service
from services.whatsapp_service import WhatsAppService
whatsapp_service = WhatsAppService()

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ Pydantic Models ============

class BulkSendRequest(BaseModel):
    phones: List[str]
    type: str  # "text" | "image" | "invitation" | "link"
    content: str  # message text, or base64 image data
    caption: Optional[str] = ""
    title: Optional[str] = ""
    description: Optional[str] = ""
    url: Optional[str] = ""


class BulkActionRequest(BaseModel):
    ticket_ids: List[int]


# ============ Endpoints ============

@router.get("/attendees")
async def get_attendees():
    """Get all approved/activated ticket holders (not hidden)"""
    session = get_session()
    try:
        tickets = session.query(Ticket).filter(
            Ticket.status.in_([TicketStatus.APPROVED, TicketStatus.ACTIVATED, TicketStatus.PAYMENT_SUBMITTED]),
            Ticket.is_hidden == False
        ).order_by(Ticket.created_at.desc()).all()

        result = []
        for t in tickets:
            customer = t.customer
            result.append({
                "id": t.id,
                "code": t.code,
                "guest_name": t.guest_name or (customer.name if customer else "—"),
                "phone": customer.phone if customer else (t.guest_phone or "—"),
                "email": customer.email if customer else "—",
                "ticket_type": t.ticket_type.value,
                "status": t.status.value,
                "created_at": t.created_at.isoformat() if t.created_at else None
            })
        
        return {"attendees": result, "count": len(result)}
    finally:
        session.close()


@router.get("/hidden")
async def get_hidden_attendees():
    """Get all hidden attendees"""
    session = get_session()
    try:
        tickets = session.query(Ticket).filter(
            Ticket.is_hidden == True
        ).order_by(Ticket.updated_at.desc()).all()

        result = []
        for t in tickets:
            customer = t.customer
            result.append({
                "id": t.id,
                "code": t.code,
                "guest_name": t.guest_name or (customer.name if customer else "—"),
                "phone": customer.phone if customer else (t.guest_phone or "—"),
                "email": customer.email if customer else "—",
                "ticket_type": t.ticket_type.value,
                "status": t.status.value
            })
        
        return {"hidden": result, "count": len(result)}
    finally:
        session.close()


@router.post("/send")
async def bulk_send(request: BulkSendRequest, background_tasks: BackgroundTasks):
    """Send message (text/image/invitation/link) to selected phone numbers"""
    
    if not request.phones:
        raise HTTPException(status_code=400, detail="No phones selected")

    sent_count = 0
    failed_count = 0

    for phone in request.phones:
        try:
            if request.type == "text":
                background_tasks.add_task(whatsapp_service.send_message, phone, request.content)
            
            elif request.type == "image":
                background_tasks.add_task(whatsapp_service.send_image, phone, request.content, request.caption or "")
            
            elif request.type == "invitation":
                # Format invitation message
                invite_msg = f"📨 *دعوة خاصة*\n\n"
                invite_msg += f"🎉 *{request.title}*\n" if request.title else ""
                invite_msg += f"{request.description}\n" if request.description else ""
                invite_msg += f"\n🔗 {request.url}" if request.url else ""
                background_tasks.add_task(whatsapp_service.send_message, phone, invite_msg)
            
            elif request.type == "link":
                background_tasks.add_task(whatsapp_service.send_link, phone, request.url or request.content, request.title or "", request.description or "")
            
            else:
                raise HTTPException(status_code=400, detail=f"Invalid type: {request.type}")
            
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to queue message for {phone}: {e}")
            failed_count += 1

    return {
        "success": True,
        "message": f"تم إرسال الرسالة إلى {sent_count} أشخاص",
        "sent": sent_count,
        "failed": failed_count
    }


@router.post("/hide")
async def hide_attendees(request: BulkActionRequest):
    """Hide selected attendees (soft-delete)"""
    session = get_session()
    try:
        updated = 0
        for tid in request.ticket_ids:
            ticket = session.query(Ticket).filter(Ticket.id == tid).first()
            if ticket:
                ticket.is_hidden = True
                updated += 1
        session.commit()
        return {"success": True, "message": f"تم إخفاء {updated} حضور", "count": updated}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/unhide")
async def unhide_attendees(request: BulkActionRequest):
    """Restore hidden attendees"""
    session = get_session()
    try:
        updated = 0
        for tid in request.ticket_ids:
            ticket = session.query(Ticket).filter(Ticket.id == tid).first()
            if ticket:
                ticket.is_hidden = False
                updated += 1
        session.commit()
        return {"success": True, "message": f"تم استعادة {updated} حضور", "count": updated}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/delete")
async def delete_attendees(request: BulkActionRequest):
    """Permanently delete rejected tickets"""
    session = get_session()
    try:
        deleted = 0
        for tid in request.ticket_ids:
            ticket = session.query(Ticket).filter(
                Ticket.id == tid,
                Ticket.status == TicketStatus.REJECTED
            ).first()
            if ticket:
                session.delete(ticket)
                deleted += 1
        session.commit()
        return {"success": True, "message": f"تم حذف {deleted} تذاكر مرفوضة نهائياً", "count": deleted}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image and return base64"""
    try:
        contents = await file.read()
        base64_data = base64.b64encode(contents).decode('utf-8')
        
        # Determine mime type
        mime = file.content_type or "image/jpeg"
        
        return {
            "success": True,
            "base64": base64_data,
            "mime": mime,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
