"""
قائمة المهام - Checklist API Routes
إدارة المهام اليومية + إعدادات اللوجستيات (رقم المدير + Group ID)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

from models import get_session, ChecklistItem, LogisticsSettings

router = APIRouter()


# ─── Pydantic Models ───

class ChecklistCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[str] = None  # YYYY-MM-DD, default = today

class ChecklistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ChecklistToggle(BaseModel):
    is_completed: bool
    completed_by_phone: Optional[str] = None
    completed_by_name: Optional[str] = None

class SettingsUpdate(BaseModel):
    manager_phone: Optional[str] = None
    manager_name: Optional[str] = None
    whatsapp_group_id: Optional[str] = None


# ─── Checklist CRUD ───

@router.get("/")
async def list_checklist(date_filter: Optional[str] = None):
    """جلب المهام - مع فلتر بالتاريخ (YYYY-MM-DD)"""
    session = get_session()
    try:
        query = session.query(ChecklistItem)
        if date_filter:
            query = query.filter(ChecklistItem.date == date_filter)
        query = query.order_by(ChecklistItem.created_at.desc())
        items = query.all()

        result = []
        for item in items:
            result.append({
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "is_completed": item.is_completed,
                "completed_by_phone": item.completed_by_phone,
                "completed_by_name": item.completed_by_name,
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                "date": item.date,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            })
        return result
    finally:
        session.close()


@router.post("/")
async def create_checklist(data: ChecklistCreate):
    """إنشاء مهمة جديدة"""
    session = get_session()
    try:
        item_date = data.date or date.today().strftime("%Y-%m-%d")
        item = ChecklistItem(
            title=data.title,
            description=data.description,
            date=item_date,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "is_completed": item.is_completed,
            "date": item.date,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
    finally:
        session.close()


@router.put("/{item_id}")
async def update_checklist(item_id: int, data: ChecklistUpdate):
    """تعديل مهمة"""
    session = get_session()
    try:
        item = session.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="المهمة غير موجودة")

        if data.title is not None:
            item.title = data.title
        if data.description is not None:
            item.description = data.description

        session.commit()
        session.refresh(item)
        return {"message": "تم التعديل", "id": item.id, "title": item.title}
    finally:
        session.close()


@router.put("/{item_id}/toggle")
async def toggle_checklist(item_id: int, data: ChecklistToggle):
    """تبديل حالة الإكمال (من واتساب أو من المنصة)"""
    session = get_session()
    try:
        item = session.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="المهمة غير موجودة")

        item.is_completed = data.is_completed
        if data.is_completed:
            item.completed_at = datetime.utcnow()
            item.completed_by_phone = data.completed_by_phone
            item.completed_by_name = data.completed_by_name
        else:
            item.completed_at = None
            item.completed_by_phone = None
            item.completed_by_name = None

        session.commit()
        return {
            "message": "تم التحديث",
            "id": item.id,
            "is_completed": item.is_completed,
        }
    finally:
        session.close()


@router.delete("/{item_id}")
async def delete_checklist(item_id: int):
    """حذف مهمة"""
    session = get_session()
    try:
        item = session.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="المهمة غير موجودة")

        session.delete(item)
        session.commit()
        return {"message": "تم الحذف"}
    finally:
        session.close()


@router.get("/progress")
async def get_progress(date_filter: Optional[str] = None):
    """نسبة الإنجاز اليومية"""
    session = get_session()
    try:
        target_date = date_filter or date.today().strftime("%Y-%m-%d")
        items = session.query(ChecklistItem).filter(ChecklistItem.date == target_date).all()
        total = len(items)
        completed = sum(1 for i in items if i.is_completed)
        percentage = round((completed / total * 100), 1) if total > 0 else 0
        return {
            "date": target_date,
            "total": total,
            "completed": completed,
            "percentage": percentage,
        }
    finally:
        session.close()


@router.get("/week")
async def get_week_progress(start_date: Optional[str] = None):
    """نسبة إنجاز الأسبوع (سبت ← جمعة)"""
    from datetime import timedelta

    session = get_session()
    try:
        if start_date:
            week_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            today = date.today()
            # الأسبوع يبدأ السبت (weekday 5)
            days_since_saturday = (today.weekday() - 5) % 7
            week_start = today - timedelta(days=days_since_saturday)

        week_data = []
        day_names_ar = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]

        for i in range(7):
            d = week_start + timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            items = session.query(ChecklistItem).filter(ChecklistItem.date == d_str).all()
            total = len(items)
            completed = sum(1 for item in items if item.is_completed)
            percentage = round((completed / total * 100), 1) if total > 0 else 0

            week_data.append({
                "date": d_str,
                "day_name": day_names_ar[d.weekday()],
                "total": total,
                "completed": completed,
                "percentage": percentage,
            })

        return week_data
    finally:
        session.close()


# ─── Logistics Settings (رقم المدير + Group ID) ───

@router.get("/settings")
async def get_settings():
    """جلب إعدادات اللوجستيات"""
    session = get_session()
    try:
        settings = session.query(LogisticsSettings).all()
        result = {}
        for s in settings:
            result[s.key] = s.value
        return result
    finally:
        session.close()


@router.put("/settings")
async def update_settings(data: SettingsUpdate):
    """تحديث إعدادات اللوجستيات"""
    session = get_session()
    try:
        updates = {}
        if data.manager_phone is not None:
            updates["manager_phone"] = data.manager_phone
        if data.manager_name is not None:
            updates["manager_name"] = data.manager_name
        if data.whatsapp_group_id is not None:
            updates["whatsapp_group_id"] = data.whatsapp_group_id

        for key, value in updates.items():
            setting = session.query(LogisticsSettings).filter(LogisticsSettings.key == key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = LogisticsSettings(key=key, value=value)
                session.add(setting)

        session.commit()
        return {"message": "تم تحديث الإعدادات", "updated": list(updates.keys())}
    finally:
        session.close()


# ─── API للـ Workflow (n8n) ───

@router.get("/search")
async def search_task(task_name: str, date_filter: Optional[str] = None):
    """بحث عن مهمة بالاسم (يستخدمها الـ n8n workflow)"""
    session = get_session()
    try:
        target_date = date_filter or date.today().strftime("%Y-%m-%d")
        items = session.query(ChecklistItem).filter(
            ChecklistItem.date == target_date,
            ChecklistItem.title.ilike(f"%{task_name}%")
        ).all()

        results = []
        for item in items:
            results.append({
                "id": item.id,
                "title": item.title,
                "is_completed": item.is_completed,
                "date": item.date,
            })
        return {"found": len(results) > 0, "tasks": results}
    finally:
        session.close()
