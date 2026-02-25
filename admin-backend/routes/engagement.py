"""
Be Star - Live Engagement Agent API
Manage real-time engagement with event attendees
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict
import base64
import logging
import asyncio
import random

from models import get_session, Ticket, TicketStatus, Customer, safe_value
from sqlalchemy import func

# WhatsApp Service
from services.whatsapp_service import WhatsAppService
whatsapp_service = WhatsAppService()

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ Pydantic Models ============

class BulkSendRequest(BaseModel):
    phones: List[str]
    attendee_ids: Optional[List[int]] = []  # ticket IDs for personalization
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
            func.lower(Ticket.status) == 'approved',
            Ticket.is_hidden == False
        ).order_by(Ticket.created_at.desc()).all()

        results = []
        for t in tickets:
            try:
                customer = t.customer
                ticket_type = safe_value(t.ticket_type)
                status = safe_value(t.status)
                
                results.append({
                    "id": t.id,
                    "code": t.code,
                    "guest_name": t.guest_name or (customer.name if customer else "—"),
                    "phone": customer.phone if customer else (t.guest_phone or "—"),
                    "email": customer.email if customer else "—",
                    "ticket_type": ticket_type,
                    "status": status,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                })
            except Exception:
                continue
        
        return {"attendees": results, "count": len(results)}
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

        results = []
        for t in tickets:
            try:
                customer = t.customer
                ticket_type = safe_value(t.ticket_type)
                status = safe_value(t.status)
                
                results.append({
                    "id": t.id,
                    "code": t.code,
                    "guest_name": t.guest_name or (customer.name if customer else "—"),
                    "phone": customer.phone if customer else (t.guest_phone or "—"),
                    "email": customer.email if customer else "—",
                    "ticket_type": ticket_type,
                    "status": status
                })
            except Exception:
                continue
        
        return {"hidden": results, "count": len(results)}
    finally:
        session.close()


# ── Batch sending configuration ──
BATCH_SIZE = 25           # messages per batch
DELAY_MIN = 3.0           # min seconds between messages
DELAY_MAX = 8.0           # max seconds between messages
BATCH_PAUSE_MIN = 60.0    # min seconds between batches
BATCH_PAUSE_MAX = 90.0    # max seconds between batches


def _get_attendee_info(attendee_ids: List[int]) -> Dict[str, dict]:
    """Look up guest_name and code for each attendee ticket, keyed by phone."""
    if not attendee_ids:
        return {}
    session = get_session()
    try:
        tickets = session.query(Ticket).filter(Ticket.id.in_(attendee_ids)).all()
        info = {}
        for t in tickets:
            customer = t.customer
            phone = customer.phone if customer else (t.guest_phone or "")
            if phone:
                info[phone] = {
                    "guest_name": t.guest_name or (customer.name if customer else ""),
                    "code": t.code or "",
                }
        return info
    finally:
        session.close()


def _build_message(request: BulkSendRequest, phone: str, attendee_info: Dict[str, dict]) -> str:
    """Build the message text, adding personalization footer if info is available."""
    # Base message
    if request.type == "text":
        msg = request.content
    elif request.type == "invitation":
        msg = f"📨 *دعوة خاصة*\n\n"
        msg += f"🎉 *{request.title}*\n" if request.title else ""
        msg += f"{request.description}\n" if request.description else ""
        msg += f"\n🔗 {request.url}" if request.url else ""
    else:
        msg = request.content

    # Add personalization footer
    info = attendee_info.get(phone)
    if info:
        name = info.get("guest_name", "")
        code = info.get("code", "")
        if name or code:
            footer = "\n\n"
            if name:
                footer += f"👤 {name}"
            if code:
                footer += f" | 🎫 {code}"
            msg += footer

    return msg


async def _send_bulk_messages(request: BulkSendRequest, attendee_info: Dict[str, dict]):
    """
    Send messages one-by-one with random delay.
    Every BATCH_SIZE messages, pause for a longer break.
    """
    total = len(request.phones)
    sent = 0
    failed = 0

    for i, phone in enumerate(request.phones):
        try:
            if request.type == "text":
                msg = _build_message(request, phone, attendee_info)
                await whatsapp_service.send_message(phone, msg)

            elif request.type == "image":
                caption = request.caption or ""
                info = attendee_info.get(phone)
                if info:
                    name = info.get("guest_name", "")
                    code = info.get("code", "")
                    if name or code:
                        extra = f"\n👤 {name}" if name else ""
                        extra += f" | 🎫 {code}" if code else ""
                        caption = (caption + extra) if caption else extra.strip()
                await whatsapp_service.send_image(phone, request.content, caption)

            elif request.type == "invitation":
                msg = _build_message(request, phone, attendee_info)
                await whatsapp_service.send_message(phone, msg)

            elif request.type == "link":
                await whatsapp_service.send_link(
                    phone,
                    request.url or request.content,
                    request.title or "",
                    request.description or ""
                )

            sent += 1
            logger.info(f"✅ Sent {i+1}/{total} to {phone}")
        except Exception as e:
            failed += 1
            logger.error(f"❌ Failed {i+1}/{total} to {phone}: {e}")

        # Delay logic (skip after last message)
        if i < total - 1:
            # Check if we just finished a batch
            if (i + 1) % BATCH_SIZE == 0:
                pause = random.uniform(BATCH_PAUSE_MIN, BATCH_PAUSE_MAX)
                logger.info(f"⏸️ Batch {(i+1)//BATCH_SIZE} complete. Pausing {pause:.0f}s...")
                await asyncio.sleep(pause)
            else:
                delay = random.uniform(DELAY_MIN, DELAY_MAX)
                logger.info(f"⏳ Waiting {delay:.1f}s...")
                await asyncio.sleep(delay)

    logger.info(f"📊 Bulk send finished: {sent} sent, {failed} failed out of {total}")


@router.post("/send")
async def bulk_send(request: BulkSendRequest, background_tasks: BackgroundTasks):
    """Send message to selected phone numbers with anti-ban batch delays"""

    if not request.phones:
        raise HTTPException(status_code=400, detail="No phones selected")

    # Look up attendee info for personalization
    attendee_info = _get_attendee_info(request.attendee_ids or [])

    # Queue the entire batch as ONE background task
    background_tasks.add_task(_send_bulk_messages, request, attendee_info)

    return {
        "success": True,
        "message": f"تم بدء إرسال الرسائل إلى {len(request.phones)} شخص (مع تأخير لحماية الرقم)",
        "queued": len(request.phones),
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
