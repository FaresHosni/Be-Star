"""
Be Star Ticketing System - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routes
from routes.tickets import router as tickets_router
from routes.auth import router as auth_router
from routes.distributors import router as distributors_router
from routes.chat import router as chat_router
from routes.stats import router as stats_router

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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tickets_router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(distributors_router, prefix="/api/distributors", tags=["Distributors"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat Widget"])
app.include_router(stats_router, prefix="/api/stats", tags=["Statistics"])


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
