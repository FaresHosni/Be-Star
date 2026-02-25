"""
Be Star Ticketing System - Main FastAPI Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routes
from routes.tickets import router as tickets_router
from routes.auth import router as auth_router, verify_token
from routes.distributors import router as distributors_router
from routes.chat import router as chat_router
from routes.stats import router as stats_router
from routes.engagement import router as engagement_router
from routes.quiz import router as quiz_router
from routes.certificates import router as certificates_router
from routes.checklist import router as checklist_router
from routes.agenda import router as agenda_router
from routes.complaints import router as complaints_router
from routes.vip import router as vip_router

# Import models to create tables
from models import init_db

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Be Star Ticketing System",
    description="نظام حجز تذاكر إيفنت كن نجماً",
    version="1.0.0"
)

# CORS configuration — restricted to actual domains only
ALLOWED_ORIGINS = [
    "https://admin-bestar.mrailabs.com",
    "https://platform-bestar.mrailabs.com",
    "http://localhost:3000",
    "http://localhost:3005",
    "http://localhost:3006",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Public routes (no token required) ───
# Auth: login/init are public by design, register/admins are already protected inside
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
# Tickets: public booking from the official platform + WhatsApp
app.include_router(tickets_router, prefix="/api/tickets", tags=["Tickets"])
# Chat: public chat widget from the official platform
app.include_router(chat_router, prefix="/api/chat", tags=["Chat Widget"])

# ─── Protected routes (require admin JWT token) ───
app.include_router(stats_router, prefix="/api/stats", tags=["Statistics"], dependencies=[Depends(verify_token)])
app.include_router(distributors_router, prefix="/api/distributors", tags=["Distributors"], dependencies=[Depends(verify_token)])
app.include_router(engagement_router, prefix="/api/engagement", tags=["Live Engagement"], dependencies=[Depends(verify_token)])
app.include_router(quiz_router, dependencies=[Depends(verify_token)])  # Quiz router has its own /api/quiz prefix
app.include_router(certificates_router, prefix="/api/certificates", tags=["Certificates"], dependencies=[Depends(verify_token)])
app.include_router(checklist_router, prefix="/api/checklist", tags=["قائمة المهام"], dependencies=[Depends(verify_token)])
app.include_router(agenda_router, prefix="/api/agenda", tags=["الأجندة"], dependencies=[Depends(verify_token)])
app.include_router(complaints_router, prefix="/api/complaints", tags=["الشكاوى المباشرة"], dependencies=[Depends(verify_token)])
app.include_router(vip_router, prefix="/api/vip", tags=["كبار الزوار"], dependencies=[Depends(verify_token)])


@app.get("/")
async def root():
    return {
        "message": "مرحباً بك في نظام حجز تذاكر كن نجماً",
        "event": os.getenv("EVENT_NAME", "Be Star"),
        "date": os.getenv("EVENT_DATE", "2026-02-11"),
        "location": os.getenv("EVENT_LOCATION", "سوهاج")
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
