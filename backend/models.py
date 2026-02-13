"""
Be Star Ticketing System - Database Models
"""
from datetime import datetime
import random
import string
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

Base = declarative_base()


class TicketType(str, enum.Enum):
    VIP = "VIP"
    STUDENT = "Student"


class TicketStatus(str, enum.Enum):
    PENDING = "pending"
    PAYMENT_SUBMITTED = "payment_submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVATED = "activated"


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tickets = relationship("Ticket", back_populates="customer")


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False, index=True)
    ticket_type = Column(SQLEnum(TicketType), nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.PENDING)
    price = Column(Integer, nullable=False)
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", back_populates="tickets")
    
    payment_method = Column(String(50), nullable=True)
    payment_proof = Column(Text, nullable=True)
    

    # Guest name for this specific ticket (defaults to customer name if empty)
    guest_name = Column(String(100), nullable=True)
    guest_phone = Column(String(20), nullable=True)
    
    approved_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(255), nullable=True)
    
    distributor_id = Column(Integer, ForeignKey("distributors.id"), nullable=True)
    
    # Live Engagement: hide attendee from engagement list
    is_hidden = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def generate_unique_code(session):
        """Generate a unique 6-digit ticket code"""
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            existing = session.query(Ticket).filter(Ticket.code == code).first()
            if not existing:
                return code


class TicketDraft(Base):
    __tablename__ = "ticket_drafts"

    id = Column(Integer, primary_key=True, index=True)
    user_phone = Column(String(20), nullable=False, index=True)
    ticket_index = Column(Integer, nullable=False)
    
    guest_name = Column(String(100), nullable=True)
    guest_phone = Column(String(20), nullable=True)
    ticket_type = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    payment_proof = Column(Text, nullable=True)
    
    is_completed = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Distributor(Base):
    __tablename__ = "distributors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    message = Column(Text, nullable=False)
    is_from_customer = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
def get_database_url():
    import os
    return os.getenv("DATABASE_URL", "sqlite:///./data/bestar.db")


def create_db_engine():
    engine = create_engine(
        get_database_url(),
        connect_args={"check_same_thread": False}
    )
    return engine


def init_db():
    engine = create_db_engine()
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration: Add missing columns to existing tables
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    
    # Check if 'is_hidden' column exists in 'tickets' table
    if 'tickets' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('tickets')]
        if 'is_hidden' not in columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN is_hidden BOOLEAN DEFAULT 0"))
                conn.commit()
    
    return engine


def get_session():
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
