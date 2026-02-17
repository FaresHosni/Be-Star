"""
الشكاوى المباشرة - Complaints API Routes
تسجيل ومتابعة الشكاوى من جروب واتساب + تصعيد للمدير
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models import get_session, Complaint

router = APIRouter()


# ─── Pydantic Models ───

class ComplaintCreate(BaseModel):
    reporter_phone: Optional[str] = None
    reporter_name: Optional[str] = None
    complaint_text: str

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None         # open / resolved / escalated
    resolution_note: Optional[str] = None
    escalated_to_manager: Optional[bool] = None


# ─── Helper ───

def complaint_to_dict(c):
    return {
        "id": c.id,
        "reporter_phone": c.reporter_phone,
        "reporter_name": c.reporter_name,
        "complaint_text": c.complaint_text,
        "status": c.status,
        "resolution_note": c.resolution_note,
        "escalated_to_manager": c.escalated_to_manager,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
    }


# ─── Complaints CRUD ───

@router.get("/")
async def list_complaints(status: Optional[str] = None):
    """جلب الشكاوى مع فلتر بالحالة"""
    session = get_session()
    try:
        query = session.query(Complaint)
        if status:
            query = query.filter(Complaint.status == status)
        query = query.order_by(Complaint.created_at.desc())
        complaints = query.all()
        return [complaint_to_dict(c) for c in complaints]
    finally:
        session.close()


@router.post("/")
async def create_complaint(data: ComplaintCreate):
    """إنشاء شكوى جديدة (من n8n workflow)"""
    session = get_session()
    try:
        complaint = Complaint(
            reporter_phone=data.reporter_phone,
            reporter_name=data.reporter_name,
            complaint_text=data.complaint_text,
            status="open",
            escalated_to_manager=True,  # الشكاوى تتصعد تلقائياً
        )
        session.add(complaint)
        session.commit()
        session.refresh(complaint)
        return complaint_to_dict(complaint)
    finally:
        session.close()


@router.put("/{complaint_id}")
async def update_complaint(complaint_id: int, data: ComplaintUpdate):
    """تحديث شكوى (حل / تصعيد)"""
    session = get_session()
    try:
        complaint = session.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="الشكوى غير موجودة")

        if data.status is not None:
            complaint.status = data.status
            if data.status == "resolved":
                complaint.resolved_at = datetime.utcnow()
        if data.resolution_note is not None:
            complaint.resolution_note = data.resolution_note
        if data.escalated_to_manager is not None:
            complaint.escalated_to_manager = data.escalated_to_manager

        session.commit()
        session.refresh(complaint)
        return {"message": "تم التحديث", "complaint": complaint_to_dict(complaint)}
    finally:
        session.close()


@router.get("/summary")
async def complaints_summary():
    """ملخص الشكاوى للمدير (يستخدمها AI في المحادثة مع المدير)"""
    session = get_session()
    try:
        all_complaints = session.query(Complaint).order_by(Complaint.created_at.desc()).all()

        open_complaints = [c for c in all_complaints if c.status == "open"]
        escalated = [c for c in all_complaints if c.escalated_to_manager]
        resolved = [c for c in all_complaints if c.status == "resolved"]

        summary = {
            "total": len(all_complaints),
            "open_count": len(open_complaints),
            "escalated_count": len(escalated),
            "resolved_count": len(resolved),
            "open_complaints": [complaint_to_dict(c) for c in open_complaints[:10]],
            "recent_all": [complaint_to_dict(c) for c in all_complaints[:20]],
        }
        return summary
    finally:
        session.close()


@router.get("/stats")
async def complaints_stats():
    """إحصائيات عامة"""
    session = get_session()
    try:
        total = session.query(Complaint).count()
        open_count = session.query(Complaint).filter(Complaint.status == "open").count()
        escalated = session.query(Complaint).filter(Complaint.escalated_to_manager == True).count()
        resolved = session.query(Complaint).filter(Complaint.status == "resolved").count()

        return {
            "total": total,
            "open": open_count,
            "escalated": escalated,
            "resolved": resolved,
        }
    finally:
        session.close()
