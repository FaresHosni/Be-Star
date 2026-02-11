"""
Distributors API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from models import get_session, Distributor

router = APIRouter()


class DistributorCreate(BaseModel):
    name: str
    phone: str
    location: Optional[str] = None


class DistributorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/")
async def create_distributor(data: DistributorCreate):
    """Create a new distributor"""
    session = get_session()
    try:
        # Check if phone exists
        existing = session.query(Distributor).filter(Distributor.phone == data.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="رقم الهاتف مسجل بالفعل")
        
        distributor = Distributor(
            name=data.name,
            phone=data.phone,
            location=data.location
        )
        session.add(distributor)
        session.commit()
        session.refresh(distributor)
        
        return {
            "success": True,
            "message": "تم إضافة الموزع بنجاح",
            "distributor_id": distributor.id
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/", response_model=List[dict])
async def get_all_distributors(active_only: bool = False):
    """Get all distributors"""
    session = get_session()
    try:
        query = session.query(Distributor)
        if active_only:
            query = query.filter(Distributor.is_active == True)
        
        distributors = query.all()
        
        return [
            {
                "id": d.id,
                "name": d.name,
                "phone": d.phone,
                "location": d.location,
                "is_active": d.is_active,
                "created_at": d.created_at.isoformat()
            } for d in distributors
        ]
    finally:
        session.close()


@router.put("/{distributor_id}")
async def update_distributor(distributor_id: int, data: DistributorUpdate):
    """Update a distributor"""
    session = get_session()
    try:
        distributor = session.query(Distributor).filter(Distributor.id == distributor_id).first()
        
        if not distributor:
            raise HTTPException(status_code=404, detail="الموزع غير موجود")
        
        if data.name is not None:
            distributor.name = data.name
        if data.phone is not None:
            distributor.phone = data.phone
        if data.location is not None:
            distributor.location = data.location
        if data.is_active is not None:
            distributor.is_active = data.is_active
        
        session.commit()
        
        return {
            "success": True,
            "message": "تم تحديث بيانات الموزع"
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/{distributor_id}")
async def delete_distributor(distributor_id: int):
    """Delete a distributor"""
    session = get_session()
    try:
        distributor = session.query(Distributor).filter(Distributor.id == distributor_id).first()
        
        if not distributor:
            raise HTTPException(status_code=404, detail="الموزع غير موجود")
        
        session.delete(distributor)
        session.commit()
        
        return {
            "success": True,
            "message": "تم حذف الموزع"
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
