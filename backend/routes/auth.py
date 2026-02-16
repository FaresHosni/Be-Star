"""
Authentication API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

from models import get_session, Admin

router = APIRouter()
security = HTTPBearer()

# Helper functions for password hashing
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

SECRET_KEY = os.getenv("SECRET_KEY", "bestar_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200))  # 30 days


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "admin"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    admin: dict


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="توكن غير صالح")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="توكن غير صالح أو منتهي الصلاحية")


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Admin login"""
    session = get_session()
    try:
        admin = session.query(Admin).filter(Admin.email == login_data.email).first()
        
        if not admin:
            raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")
        
        if not verify_password(login_data.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")
        
        if not admin.is_active:
            raise HTTPException(status_code=401, detail="هذا الحساب غير مفعّل")
        
        access_token = create_access_token({"sub": admin.email, "role": admin.role})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin": {
                "id": admin.id,
                "email": admin.email,
                "name": admin.name,
                "role": admin.role
            }
        }
    finally:
        session.close()


@router.post("/register")
async def register_admin(admin_data: AdminCreate, token_data: dict = Depends(verify_token)):
    """Register a new admin (protected - requires existing admin)"""
    session = get_session()
    try:
        # Check if email exists
        existing = session.query(Admin).filter(Admin.email == admin_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="هذا البريد الإلكتروني مسجل بالفعل")
        
        # Hash password
        password_hash = hash_password(admin_data.password)
        
        # Create admin
        admin = Admin(
            email=admin_data.email,
            password_hash=password_hash,
            name=admin_data.name,
            role=admin_data.role
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        return {
            "success": True,
            "message": "تم إنشاء حساب الأدمن بنجاح",
            "admin_id": admin.id
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/me")
async def get_current_admin(token_data: dict = Depends(verify_token)):
    """Get current logged in admin"""
    session = get_session()
    try:
        admin = session.query(Admin).filter(Admin.email == token_data["sub"]).first()
        if not admin:
            raise HTTPException(status_code=404, detail="الأدمن غير موجود")
        
        return {
            "id": admin.id,
            "email": admin.email,
            "name": admin.name,
            "role": admin.role
        }
    finally:
        session.close()


@router.post("/init")
async def init_admin():
    """Initialize default admin account"""
    session = get_session()
    try:
        # Check if any admin exists
        existing = session.query(Admin).first()
        if existing:
            return {"message": "يوجد أدمن بالفعل"}
        
        # Create default admin
        password_hash = hash_password("admin123")
        admin = Admin(
            email=os.getenv("ADMIN_EMAIL", "hsny4756@gmail.com"),
            password_hash=password_hash,
            name="مدير النظام",
            role="super_admin"
        )
        session.add(admin)
        session.commit()
        
        return {
            "success": True,
            "message": "تم إنشاء حساب الأدمن الافتراضي",
            "email": admin.email,
            "password": "admin123"
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/admins")
async def list_admins(token_data: dict = Depends(verify_token)):
    """List all admins"""
    session = get_session()
    try:
        admins = session.query(Admin).all()
        return [
            {
                "id": a.id,
                "email": a.email,
                "name": a.name,
                "role": a.role,
                "is_active": a.is_active
            }
            for a in admins
        ]
    finally:
        session.close()


@router.put("/admins/{admin_id}")
async def update_admin(admin_id: int, admin_data: dict, token_data: dict = Depends(verify_token)):
    """Update an admin"""
    session = get_session()
    try:
        admin = session.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="الأدمن غير موجود")
        
        if "name" in admin_data:
            admin.name = admin_data["name"]
        if "email" in admin_data:
            admin.email = admin_data["email"]
        if "role" in admin_data:
            admin.role = admin_data["role"]
        if "password" in admin_data and admin_data["password"]:
            admin.password_hash = hash_password(admin_data["password"])
        
        session.commit()
        return {"success": True, "message": "تم تحديث الأدمن"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/admins/{admin_id}")
async def delete_admin(admin_id: int, token_data: dict = Depends(verify_token)):
    """Delete an admin"""
    session = get_session()
    try:
        admin = session.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="الأدمن غير موجود")
        
        session.delete(admin)
        session.commit()
        return {"success": True, "message": "تم حذف الأدمن"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

