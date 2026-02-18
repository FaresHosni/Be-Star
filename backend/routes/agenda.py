"""
الأجندة - Agenda API Routes
إدارة الأحداث والمواعيد + التذكيرات
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, timedelta

from models import get_session, AgendaEvent

router = APIRouter()


# ─── Pydantic Models ───

class AgendaCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_time: str           # ISO format: "2026-02-17T14:00:00"
    location: Optional[str] = None
    date: Optional[str] = None  # YYYY-MM-DD, يُستخرج من event_time لو مش موجود

class AgendaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_time: Optional[str] = None
    location: Optional[str] = None


# ─── Helper ───

def event_to_dict(event):
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "event_time": event.event_time.isoformat() if event.event_time else None,
        "location": event.location,
        "reminder_sent": event.reminder_sent,
        "date": event.date,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


# ─── Agenda CRUD (list + create) ───

@router.get("/")
async def list_agenda(date_filter: Optional[str] = None):
    """جلب أحداث الأجندة - مع فلتر بالتاريخ"""
    session = get_session()
    try:
        query = session.query(AgendaEvent)
        if date_filter:
            query = query.filter(AgendaEvent.date == date_filter)
        query = query.order_by(AgendaEvent.event_time.asc())
        events = query.all()
        return [event_to_dict(e) for e in events]
    finally:
        session.close()


@router.post("/")
async def create_agenda(data: AgendaCreate):
    """إنشاء حدث جديد"""
    session = get_session()
    try:
        event_time = datetime.fromisoformat(data.event_time)
        event_date = data.date or event_time.strftime("%Y-%m-%d")

        event = AgendaEvent(
            title=data.title,
            description=data.description,
            event_time=event_time,
            location=data.location,
            date=event_date,
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return event_to_dict(event)
    except ValueError:
        raise HTTPException(status_code=400, detail="صيغة الوقت غير صحيحة، استخدم ISO format")
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# ⚠️ IMPORTANT: Static routes MUST come BEFORE /{event_id} routes
#    FastAPI matches routes top-to-bottom.
# ═══════════════════════════════════════════════════════════════

@router.get("/week")
async def get_week_events(start_date: Optional[str] = None):
    """أحداث الأسبوع (سبت ← جمعة)"""
    session = get_session()
    try:
        if start_date:
            week_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            today = date.today()
            days_since_saturday = (today.weekday() - 5) % 7
            week_start = today - timedelta(days=days_since_saturday)

        week_end = week_start + timedelta(days=6)
        start_str = week_start.strftime("%Y-%m-%d")
        end_str = week_end.strftime("%Y-%m-%d")

        events = session.query(AgendaEvent).filter(
            AgendaEvent.date >= start_str,
            AgendaEvent.date <= end_str
        ).order_by(AgendaEvent.event_time.asc()).all()

        return {
            "week_start": start_str,
            "week_end": end_str,
            "events": [event_to_dict(e) for e in events],
        }
    finally:
        session.close()


# ─── API للـ Workflow (n8n) - التذكيرات ───

@router.get("/upcoming")
async def get_upcoming_events(minutes: int = 10):
    """أحداث قادمة خلال X دقيقة (يستخدمها n8n للتذكيرات)"""
    session = get_session()
    try:
        # نستخدم توقيت القاهرة
        import pytz
        cairo_tz = pytz.timezone("Africa/Cairo")
        now_cairo = datetime.now(cairo_tz)
        target_time = now_cairo + timedelta(minutes=minutes)

        # نبحث عن أحداث وقتها بين الآن و X دقيقة قدام ومش اتبعتلها تذكير
        today_str = now_cairo.strftime("%Y-%m-%d")
        events = session.query(AgendaEvent).filter(
            AgendaEvent.date == today_str,
            AgendaEvent.reminder_sent == False,
        ).all()

        upcoming = []
        for event in events:
            # نقارن الوقت (بتاع المنصة بتوقيت القاهرة)
            event_dt = cairo_tz.localize(event.event_time) if event.event_time.tzinfo is None else event.event_time
            if now_cairo <= event_dt <= target_time:
                upcoming.append(event_to_dict(event))

        return {"upcoming": upcoming, "count": len(upcoming)}
    finally:
        session.close()


# ─── Dynamic Routes (/{event_id}) — MUST come after static routes ───

@router.put("/{event_id}")
async def update_agenda(event_id: int, data: AgendaUpdate):
    """تعديل حدث"""
    session = get_session()
    try:
        event = session.query(AgendaEvent).filter(AgendaEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="الحدث غير موجود")

        if data.title is not None:
            event.title = data.title
        if data.description is not None:
            event.description = data.description
        if data.event_time is not None:
            event.event_time = datetime.fromisoformat(data.event_time)
            event.date = event.event_time.strftime("%Y-%m-%d")
        if data.location is not None:
            event.location = data.location

        session.commit()
        session.refresh(event)
        return {"message": "تم التعديل", "event": event_to_dict(event)}
    finally:
        session.close()


@router.put("/{event_id}/reminder-sent")
async def mark_reminder_sent(event_id: int):
    """تعليم إن التذكير اتبعت (يستخدمها n8n بعد إرسال التذكير)"""
    session = get_session()
    try:
        event = session.query(AgendaEvent).filter(AgendaEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="الحدث غير موجود")

        event.reminder_sent = True
        session.commit()
        return {"message": "تم التعليم", "id": event.id}
    finally:
        session.close()


@router.delete("/{event_id}")
async def delete_agenda(event_id: int):
    """حذف حدث"""
    session = get_session()
    try:
        event = session.query(AgendaEvent).filter(AgendaEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="الحدث غير موجود")

        session.delete(event)
        session.commit()
        return {"message": "تم الحذف"}
    finally:
        session.close()
