"""
Certificates & Thank You API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import base64
import logging

from models import get_session, CertificateLog, ThankYouLog
from services.certificate_generator import generate_certificate_pdf
from services.whatsapp_service import WhatsAppService

router = APIRouter()
logger = logging.getLogger(__name__)
whatsapp = WhatsAppService()


class SendCertificatesRequest(BaseModel):
    ticket_ids: List[int]


class SendThanksRequest(BaseModel):
    ticket_ids: List[int]
    message: str


@router.get("/participants")
async def get_participants(sort_by: str = "points"):
    """Get all quiz participants with their scores and ranking"""
    session = get_session()
    try:
        from sqlalchemy import text
        
        # Get all participants with their scores from quiz_answers
        query = text("""
            SELECT 
                t.id as ticket_id,
                COALESCE(t.guest_name, c.name) as guest_name,
                COALESCE(t.guest_phone, c.phone) as phone,
                COALESCE(
                    (SELECT COUNT(*) FROM quiz_answers qa WHERE qa.ticket_id = t.id),
                    0
                ) as total_answers,
                COALESCE(
                    (SELECT COUNT(*) FROM quiz_answers qa WHERE qa.ticket_id = t.id AND qa.is_correct = 1),
                    0
                ) as correct_answers,
                COALESCE(
                    (SELECT SUM(qa.points) FROM quiz_answers qa WHERE qa.ticket_id = t.id),
                    0
                ) as total_points
            FROM tickets t
            JOIN customers c ON t.customer_id = c.id
            WHERE t.status = 'approved'
            AND t.id IN (SELECT DISTINCT ticket_id FROM quiz_answers)
        """)
        
        result = session.execute(query)
        participants = []
        for row in result:
            participants.append({
                "ticket_id": row[0],
                "guest_name": row[1],
                "phone": row[2],
                "total_answers": row[3],
                "correct_answers": row[4],
                "total_points": row[5]
            })
        
        # Sort
        if sort_by == "points":
            participants.sort(key=lambda x: x["total_points"], reverse=True)
        elif sort_by == "name":
            participants.sort(key=lambda x: x["guest_name"] or "")
        elif sort_by == "answers":
            participants.sort(key=lambda x: x["total_answers"], reverse=True)
        
        # Add ranking (by points)
        ranked = sorted(participants, key=lambda x: x["total_points"], reverse=True)
        rank_map = {}
        for i, p in enumerate(ranked):
            rank_map[p["ticket_id"]] = i + 1
        
        for p in participants:
            p["rank"] = rank_map[p["ticket_id"]]
        
        return {
            "success": True,
            "total_participants": len(participants),
            "participants": participants
        }
    except Exception as e:
        logger.error(f"Error fetching participants: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/send-certificates")
async def send_certificates(req: SendCertificatesRequest):
    """Generate and send certificate PDFs via WhatsApp for selected participants"""
    session = get_session()
    try:
        from sqlalchemy import text
        
        # Get participant data
        participants_resp = await get_participants(sort_by="points")
        all_participants = participants_resp["participants"]
        total_count = participants_resp["total_participants"]
        
        # Filter to selected ticket_ids
        selected = [p for p in all_participants if p["ticket_id"] in req.ticket_ids]
        
        if not selected:
            raise HTTPException(status_code=400, detail="لم يتم العثور على مشاركين")
        
        results = []
        for p in selected:
            try:
                # Generate PDF
                pdf_bytes = generate_certificate_pdf(
                    guest_name=p["guest_name"],
                    total_points=p["total_points"],
                    rank=p["rank"],
                    total_participants=total_count
                )
                
                # Convert to base64
                pdf_base64 = f"data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}"
                
                # Send via WhatsApp
                wa_result = await whatsapp.send_certificate(
                    phone=p["phone"],
                    pdf_base64=pdf_base64,
                    guest_name=p["guest_name"],
                    rank=p["rank"]
                )
                
                status = "sent" if wa_result else "failed"
                error_msg = None if wa_result else "فشل إرسال الواتساب"
                
                # Log to DB
                log = CertificateLog(
                    ticket_id=p["ticket_id"],
                    guest_name=p["guest_name"],
                    phone=p["phone"],
                    total_points=p["total_points"],
                    rank=p["rank"],
                    status=status,
                    error_message=error_msg
                )
                session.add(log)
                
                results.append({
                    "ticket_id": p["ticket_id"],
                    "guest_name": p["guest_name"],
                    "status": status
                })
                
            except Exception as e:
                logger.error(f"Error processing certificate for {p['guest_name']}: {e}")
                log = CertificateLog(
                    ticket_id=p["ticket_id"],
                    guest_name=p["guest_name"],
                    phone=p["phone"],
                    total_points=p["total_points"],
                    rank=p["rank"],
                    status="failed",
                    error_message=str(e)
                )
                session.add(log)
                results.append({
                    "ticket_id": p["ticket_id"],
                    "guest_name": p["guest_name"],
                    "status": "failed",
                    "error": str(e)
                })
        
        session.commit()
        
        sent_count = sum(1 for r in results if r["status"] == "sent")
        return {
            "success": True,
            "message": f"تم إرسال {sent_count} شهادة من {len(results)}",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error sending certificates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/send-thanks")
async def send_thanks(req: SendThanksRequest):
    """Send thank you messages via WhatsApp to selected participants"""
    session = get_session()
    try:
        from sqlalchemy import text
        
        # Get participant data
        participants_resp = await get_participants(sort_by="points")
        all_participants = participants_resp["participants"]
        
        selected = [p for p in all_participants if p["ticket_id"] in req.ticket_ids]
        
        if not selected:
            raise HTTPException(status_code=400, detail="لم يتم العثور على مشاركين")
        
        results = []
        for p in selected:
            try:
                # Personalize message
                personalized = req.message.replace("{name}", p["guest_name"] or "")
                personalized = personalized.replace("{points}", str(p["total_points"]))
                personalized = personalized.replace("{rank}", str(p.get("rank", "")))
                
                # Send via WhatsApp
                wa_result = await whatsapp.send_message(
                    phone=p["phone"],
                    message=personalized
                )
                
                status = "sent" if wa_result else "failed"
                error_msg = None if wa_result else "فشل إرسال الواتساب"
                
                # Log to DB
                log = ThankYouLog(
                    ticket_id=p["ticket_id"],
                    guest_name=p["guest_name"],
                    phone=p["phone"],
                    message_text=personalized,
                    status=status,
                    error_message=error_msg
                )
                session.add(log)
                
                results.append({
                    "ticket_id": p["ticket_id"],
                    "guest_name": p["guest_name"],
                    "status": status
                })
                
            except Exception as e:
                logger.error(f"Error sending thanks to {p['guest_name']}: {e}")
                log = ThankYouLog(
                    ticket_id=p["ticket_id"],
                    guest_name=p["guest_name"],
                    phone=p["phone"],
                    message_text=req.message,
                    status="failed",
                    error_message=str(e)
                )
                session.add(log)
                results.append({
                    "ticket_id": p["ticket_id"],
                    "guest_name": p["guest_name"],
                    "status": "failed"
                })
        
        session.commit()
        
        sent_count = sum(1 for r in results if r["status"] == "sent")
        return {
            "success": True,
            "message": f"تم إرسال {sent_count} رسالة من {len(results)}",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error sending thanks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/logs/certificates")
async def get_certificate_logs():
    """Get all certificate sending logs"""
    session = get_session()
    try:
        logs = session.query(CertificateLog).order_by(CertificateLog.sent_at.desc()).all()
        return [
            {
                "id": log.id,
                "ticket_id": log.ticket_id,
                "guest_name": log.guest_name,
                "phone": log.phone,
                "total_points": log.total_points,
                "rank": log.rank,
                "status": log.status,
                "error_message": log.error_message,
                "sent_at": log.sent_at.isoformat() if log.sent_at else None
            }
            for log in logs
        ]
    finally:
        session.close()


@router.get("/logs/thanks")
async def get_thanks_logs():
    """Get all thank you message logs"""
    session = get_session()
    try:
        logs = session.query(ThankYouLog).order_by(ThankYouLog.sent_at.desc()).all()
        return [
            {
                "id": log.id,
                "ticket_id": log.ticket_id,
                "guest_name": log.guest_name,
                "phone": log.phone,
                "message_text": log.message_text,
                "status": log.status,
                "error_message": log.error_message,
                "sent_at": log.sent_at.isoformat() if log.sent_at else None
            }
            for log in logs
        ]
    finally:
        session.close()
