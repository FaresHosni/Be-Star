"""
Be Star Ticketing System - Database Models
"""
from datetime import datetime
import random
import string
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
import json

Base = declarative_base()


def safe_value(v):
    """Extract string value from Enum or return string as-is."""
    return v.value if hasattr(v, 'value') else str(v)


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
    ticket_type = Column(String(20), nullable=False)
    status = Column(String(30), default="pending")
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


# ═══════════════════════════════════════════
# Quiz & Scoring Engine Models
# ═══════════════════════════════════════════

class QuestionType(str, enum.Enum):
    MCQ = "mcq"                 # اختيار من متعدد
    COMPLETION = "completion"   # إكمال (نص حر)


class QuestionStatus(str, enum.Enum):
    DRAFT = "draft"       # مسودة - لسه مترسلتش
    ACTIVE = "active"     # نشط - اترسل ومستنين إجابات
    EXPIRED = "expired"   # انتهى الوقت


class QuizGroup(Base):
    """مجموعات مخصصة للمسابقات (غير VIP/Student)"""
    __tablename__ = "quiz_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("QuizGroupMember", back_populates="group", cascade="all, delete-orphan")


class QuizGroupMember(Base):
    """ربط مشارك (ticket) بمجموعة مسابقة"""
    __tablename__ = "quiz_group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("quiz_groups.id", ondelete="CASCADE"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    
    group = relationship("QuizGroup", back_populates="members")
    ticket = relationship("Ticket")


class Question(Base):
    """سؤال مسابقة"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)                     # نص السؤال
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    correct_answer = Column(Text, nullable=False)            # الإجابة الصحيحة (للإكمال أو حرف MCQ)
    points = Column(Integer, default=1)                      # عدد الدرجات
    time_limit_seconds = Column(Integer, default=60)         # المدة بالثواني
    status = Column(SQLEnum(QuestionStatus), default=QuestionStatus.DRAFT)
    
    # استهداف: JSON array من أنواع المجموعات
    # مثال: ["VIP", "Student"] أو ["group:5"] أو ["all"]
    target_groups = Column(Text, default='["all"]')
    
    # هل الإجابات بعد الوقت تتحسب؟
    accept_late = Column(Boolean, default=False)
    
    sent_at = Column(DateTime, nullable=True)                # وقت الإرسال
    expires_at = Column(DateTime, nullable=True)             # وقت الانتهاء
    created_at = Column(DateTime, default=datetime.utcnow)
    
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    def get_target_groups(self):
        try:
            return json.loads(self.target_groups or '["all"]')
        except:
            return ["all"]
    
    def set_target_groups(self, groups_list):
        self.target_groups = json.dumps(groups_list, ensure_ascii=False)


class QuestionOption(Base):
    """خيارات السؤال (MCQ فقط)"""
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(1), nullable=False)     # A, B, C, D
    text = Column(Text, nullable=False)            # نص الخيار
    is_correct = Column(Boolean, default=False)    # هل ده الإجابة الصح؟
    
    question = relationship("Question", back_populates="options")


class Answer(Base):
    """إجابة مشارك على سؤال"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    phone = Column(String(20), nullable=False)      # رقم المشارك
    
    answer_text = Column(Text, nullable=False)       # الإجابة اللي بعتها
    is_correct = Column(Boolean, default=False)      # صح ولا غلط
    similarity_score = Column(Float, default=0.0)    # نسبة التشابه (للإكمال)
    points_earned = Column(Integer, default=0)       # الدرجات المكتسبة
    is_late = Column(Boolean, default=False)         # هل جاوب بعد الوقت؟
    
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    question = relationship("Question", back_populates="answers")
    ticket = relationship("Ticket")


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


class CertificateLog(Base):
    """Log of sent certificates"""
    __tablename__ = "certificate_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, nullable=True)
    guest_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    total_points = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    status = Column(String(20), default="sent")  # sent / failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)


class ThankYouLog(Base):
    """Log of sent thank you messages"""
    __tablename__ = "thankyou_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, nullable=True)
    guest_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    message_text = Column(Text, nullable=True)
    status = Column(String(20), default="sent")  # sent / failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════
# Logistics Coordinator Models (موظف لوجستيات التشغيل)
# ═══════════════════════════════════════════

class ChecklistItem(Base):
    """مهمة يومية - يديرها الأدمن ويتابعها الـ AI في جروب واتساب"""
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_by_phone = Column(String(20), nullable=True)   # رقم اللي خلّص المهمة
    completed_by_name = Column(String(100), nullable=True)   # اسم اللي خلّص المهمة
    completed_at = Column(DateTime, nullable=True)
    date = Column(String(10), nullable=False, index=True)     # YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.utcnow)


class AgendaEvent(Base):
    """حدث في الأجندة - مع تذكير قبل 10 دقائق"""
    __tablename__ = "agenda_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_time = Column(DateTime, nullable=False)             # وقت الحدث بالضبط
    location = Column(String(200), nullable=True)
    reminder_sent = Column(Boolean, default=False)            # هل اتبعت التذكير؟
    date = Column(String(10), nullable=False, index=True)     # YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.utcnow)


class Complaint(Base):
    """شكوى من عميل على جروب واتساب"""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    reporter_phone = Column(String(20), nullable=True)
    reporter_name = Column(String(100), nullable=True)
    complaint_text = Column(Text, nullable=False)
    status = Column(String(20), default="open")               # open / resolved / escalated
    resolution_note = Column(Text, nullable=True)
    escalated_to_manager = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class LogisticsSettings(Base):
    """إعدادات اللوجستيات - رقم المدير + Group ID (key-value)"""
    __tablename__ = "logistics_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False)     # manager_phone / whatsapp_group_id / manager_name
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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

    # Check if 'is_active' column exists in 'admins' table
    if 'admins' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('admins')]
        if 'is_active' not in columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE admins ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                conn.commit()

    # Check for guest_name and guest_phone in tickets
    if 'tickets' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('tickets')]
        with engine.connect() as conn:
            if 'guest_name' not in columns:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN guest_name TEXT"))
            if 'guest_phone' not in columns:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN guest_phone TEXT"))
            conn.commit()

    return engine


def get_session():
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
