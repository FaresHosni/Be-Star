"""
كبار الزوار (VIP) — API Routes
إدارة الشخصيات المهمة + تتبع الردود + إعدادات الرسائل
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import httpx
import os
import uuid
import shutil

from models import get_session, VipGuest, VipSettings

router = APIRouter()


# ─── Pydantic Models ───

class VipGuestCreate(BaseModel):
    name: str
    phone: str
    added_by: Optional[str] = None

class VipStatusUpdate(BaseModel):
    status: str                       # will_attend / not_attending / inquiring / reacted / no_response
    source: Optional[str] = "n8n"     # n8n / manual

class VipSettingsUpdate(BaseModel):
    invitation_text: Optional[str] = None
    invitation_image: Optional[str] = None
    invitation_link: Optional[str] = None
    reaction_reply: Optional[str] = None
    inquiry_reply: Optional[str] = None


# ─── Helpers ───

def vip_to_dict(v):
    return {
        "id": v.id,
        "name": v.name,
        "phone": v.phone,
        "status": v.status,
        "previous_status": v.previous_status,
        "changed_mind": v.changed_mind,
        "last_interaction": v.last_interaction.isoformat() if v.last_interaction else None,
        "added_by": v.added_by,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


def get_vip_setting(session, key: str) -> Optional[str]:
    s = session.query(VipSettings).filter(VipSettings.key == key).first()
    return s.value if s else None


def set_vip_setting(session, key: str, value: str):
    s = session.query(VipSettings).filter(VipSettings.key == key).first()
    if s:
        s.value = value
    else:
        session.add(VipSettings(key=key, value=value))


async def send_whatsapp_message(phone: str, text: str, image_filename: str = None):
    """إرسال رسالة واتساب عبر Evolution API"""
    evo_url = os.getenv("EVOLUTION_API_URL", "http://38.242.139.159:8080")
    evo_key = os.getenv("EVOLUTION_API_KEY", "")
    instance = os.getenv("EVOLUTION_INSTANCE", "Mahmoud Magdy")

    # تنسيق الرقم
    jid = phone.lstrip("0+")
    if not jid.startswith("20"):
        jid = "20" + jid
    jid = jid + "@s.whatsapp.net"

    async with httpx.AsyncClient(timeout=15) as client:
        if image_filename:
            # قراءة الصورة المرفوعة كـ base64
            import base64
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vip_uploads")
            filepath = os.path.join(upload_dir, image_filename)
            if os.path.exists(filepath):
                with open(filepath, "rb") as img_file:
                    b64 = base64.b64encode(img_file.read()).decode("utf-8")
                ext = image_filename.rsplit(".", 1)[-1].lower()
                mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
                await client.post(
                    f"{evo_url}/message/sendMedia/{instance}",
                    headers={"apikey": evo_key, "Content-Type": "application/json"},
                    json={
                        "number": jid,
                        "mediatype": "image",
                        "media": f"data:{mime};base64,{b64}",
                        "caption": text,
                    }
                )
            else:
                # لو الصورة مش موجودة، ابعت نص فقط
                await client.post(
                    f"{evo_url}/message/sendText/{instance}",
                    headers={"apikey": evo_key, "Content-Type": "application/json"},
                    json={"number": jid, "text": text}
                )
        else:
            # إرسال نص فقط
            await client.post(
                f"{evo_url}/message/sendText/{instance}",
                headers={"apikey": evo_key, "Content-Type": "application/json"},
                json={
                    "number": jid,
                    "text": text,
                }
            )



# ─── VIP CRUD ───

@router.get("/")
async def list_vip_guests(status: Optional[str] = None):
    """جلب كل الشخصيات المهمة"""
    session = get_session()
    try:
        query = session.query(VipGuest)
        if status:
            query = query.filter(VipGuest.status == status)
        query = query.order_by(VipGuest.created_at.desc())
        guests = query.all()
        return [vip_to_dict(g) for g in guests]
    finally:
        session.close()


@router.post("/")
async def add_vip_guest(data: VipGuestCreate):
    """إضافة شخصية مهمة + إرسال الدعوة تلقائياً"""
    session = get_session()
    try:
        # تحقق من عدم التكرار
        existing = session.query(VipGuest).filter(VipGuest.phone == data.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="هذا الرقم مضاف بالفعل")

        guest = VipGuest(
            name=data.name,
            phone=data.phone,
            status="invited",
            added_by=data.added_by,
        )
        session.add(guest)
        session.commit()
        session.refresh(guest)

        # إرسال الدعوة تلقائياً
        invitation_text = get_vip_setting(session, "invitation_text") or ""
        invitation_link = get_vip_setting(session, "invitation_link") or ""
        invitation_image = get_vip_setting(session, "invitation_image") or ""

        if invitation_text:
            full_text = invitation_text
            if invitation_link:
                full_text += f"\n\n🔗 {invitation_link}"
            try:
                await send_whatsapp_message(
                    data.phone,
                    full_text,
                    image_filename=invitation_image if invitation_image else None
                )
            except Exception as e:
                print(f"⚠️ VIP invitation send failed: {e}")

        return {"message": "تمت الإضافة بنجاح", "guest": vip_to_dict(guest)}
    finally:
        session.close()


@router.delete("/{guest_id}")
async def delete_vip_guest(guest_id: int):
    """حذف شخصية مهمة"""
    session = get_session()
    try:
        guest = session.query(VipGuest).filter(VipGuest.id == guest_id).first()
        if not guest:
            raise HTTPException(status_code=404, detail="غير موجود")
        session.delete(guest)
        session.commit()
        return {"message": "تم الحذف"}
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# ⚠️ Static routes MUST come BEFORE /{id} routes
# ═══════════════════════════════════════════════════════════════

@router.get("/stats")
async def vip_stats():
    """إحصائيات كبار الزوار"""
    session = get_session()
    try:
        all_guests = session.query(VipGuest).all()
        total = len(all_guests)

        counts = {
            "will_attend": 0,
            "not_attending": 0,
            "inquiring": 0,
            "reacted": 0,
            "no_response": 0,
            "invited": 0,
            "changed_mind": 0,
        }
        for g in all_guests:
            if g.status in counts:
                counts[g.status] += 1
            if g.changed_mind:
                counts["changed_mind"] += 1

        counts["total"] = total
        return counts
    finally:
        session.close()


@router.get("/settings")
async def get_settings():
    """جلب إعدادات رسائل VIP"""
    session = get_session()
    try:
        settings = session.query(VipSettings).all()
        result = {}
        for s in settings:
            result[s.key] = s.value
        return result
    finally:
        session.close()


@router.put("/settings")
async def update_settings(data: VipSettingsUpdate):
    """تحديث إعدادات رسائل VIP"""
    session = get_session()
    try:
        fields = {
            "invitation_text": data.invitation_text,
            "invitation_image": data.invitation_image,
            "invitation_link": data.invitation_link,
            "reaction_reply": data.reaction_reply,
            "inquiry_reply": data.inquiry_reply,
        }
        for key, value in fields.items():
            if value is not None:
                set_vip_setting(session, key, value)

        session.commit()
        return {"message": "تم حفظ الإعدادات"}
    finally:
        session.close()


@router.post("/upload-image")
async def upload_invitation_image(file: UploadFile = File(...)):
    """رفع صورة الدعوة"""
    # تأكد إن الملف صورة
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="الملف لازم يكون صورة")

    # إنشاء مجلد الرفع
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vip_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # اسم فريد للملف
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"vip_invite_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    # حفظ الملف
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # حفظ في الإعدادات
    session = get_session()
    try:
        set_vip_setting(session, "invitation_image", filename)
        session.commit()
    finally:
        session.close()

    return {"message": "تم رفع الصورة بنجاح", "filename": filename}


@router.get("/image/{filename}")
async def serve_vip_image(filename: str):
    """تقديم صورة الدعوة"""
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vip_uploads")
    filepath = os.path.join(upload_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="الصورة غير موجودة")
    return FileResponse(filepath)


@router.get("/check/{phone}")
async def check_is_vip(phone: str):
    """فحص هل الرقم VIP — يستخدمها n8n"""
    session = get_session()
    try:
        guest = session.query(VipGuest).filter(VipGuest.phone == phone).first()
        if guest:
            return {
                "is_vip": True,
                "guest": vip_to_dict(guest),
            }
        return {"is_vip": False}
    finally:
        session.close()


@router.post("/webhook/status")
async def webhook_update_status(data: VipStatusUpdate, phone: Optional[str] = None):
    """تحديث حالة VIP — يستخدمها n8n"""
    if not phone:
        raise HTTPException(status_code=400, detail="phone query param required")

    session = get_session()
    try:
        guest = session.query(VipGuest).filter(VipGuest.phone == phone).first()
        if not guest:
            raise HTTPException(status_code=404, detail="VIP غير موجود")

        old_status = guest.status
        new_status = data.status

        # تتبع تغيير الرأي
        decision_statuses = {"will_attend", "not_attending"}
        if old_status in decision_statuses and new_status in decision_statuses and old_status != new_status:
            guest.changed_mind = True

        guest.previous_status = old_status
        guest.status = new_status
        guest.last_interaction = datetime.utcnow()

        session.commit()
        session.refresh(guest)
        return {"message": "تم التحديث", "guest": vip_to_dict(guest)}
    finally:
        session.close()
