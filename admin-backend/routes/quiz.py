"""
Quiz & Scoring Engine - API Router
Handles questions, groups, answers, and leaderboard
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
import json
import logging

from models import (
    get_session, Ticket, TicketType, TicketStatus, Customer, safe_value,
    QuizGroup, QuizGroupMember, Question, QuestionOption, Answer,
    QuestionType, QuestionStatus
)
from services.whatsapp_service import WhatsAppService
from services.scoring import evaluate_answer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quiz", tags=["quiz"])
whatsapp_service = WhatsAppService()


# ═══════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ticket_ids: List[int] = []


class OptionCreate(BaseModel):
    label: str   # A, B, C, D
    text: str
    is_correct: bool = False


class QuestionCreate(BaseModel):
    text: str
    question_type: str  # "mcq" or "completion"
    correct_answer: str
    points: int = 1
    time_limit_seconds: int = 60
    target_groups: List[str] = ["all"]  # ["all"], ["VIP"], ["Student"], ["group:5"]
    accept_late: bool = False
    options: List[OptionCreate] = []  # For MCQ only


class AnswerSubmit(BaseModel):
    phone: str
    question_id: int
    answer_text: str
    sender_name: str = ""


# ═══════════════════════════════════════════
#  Groups
# ═══════════════════════════════════════════

@router.get("/groups")
def list_groups():
    session = get_session()
    try:
        groups = session.query(QuizGroup).order_by(QuizGroup.created_at.desc()).all()
        result = []
        for g in groups:
            members = session.query(QuizGroupMember).filter(QuizGroupMember.group_id == g.id).all()
            member_data = []
            for m in members:
                ticket = session.query(Ticket).filter(Ticket.id == m.ticket_id).first()
                if ticket:
                    member_data.append({
                        "ticket_id": ticket.id,
                        "guest_name": ticket.guest_name,
                        "phone": ticket.customer.phone if ticket.customer else "—",
                        "ticket_type": safe_value(ticket.ticket_type),
                    })
            result.append({
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "member_count": len(member_data),
                "members": member_data,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            })
        return {"groups": result}
    finally:
        session.close()


@router.post("/groups")
def create_group(data: GroupCreate):
    session = get_session()
    try:
        group = QuizGroup(name=data.name, description=data.description)
        session.add(group)
        session.flush()
        
        for tid in data.ticket_ids:
            member = QuizGroupMember(group_id=group.id, ticket_id=tid)
            session.add(member)
        
        session.commit()
        return {"success": True, "message": f"تم إنشاء المجموعة '{data.name}'", "group_id": group.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.put("/groups/{group_id}")
def update_group(group_id: int, data: GroupCreate):
    session = get_session()
    try:
        group = session.query(QuizGroup).filter(QuizGroup.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="المجموعة غير موجودة")
        
        group.name = data.name
        group.description = data.description
        
        # Clear and re-add members
        session.query(QuizGroupMember).filter(QuizGroupMember.group_id == group_id).delete()
        for tid in data.ticket_ids:
            session.add(QuizGroupMember(group_id=group_id, ticket_id=tid))
        
        session.commit()
        return {"success": True, "message": f"تم تحديث المجموعة '{data.name}'"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/groups/{group_id}")
def delete_group(group_id: int):
    session = get_session()
    try:
        group = session.query(QuizGroup).filter(QuizGroup.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="المجموعة غير موجودة")
        session.delete(group)
        session.commit()
        return {"success": True, "message": "تم حذف المجموعة"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# ═══════════════════════════════════════════
#  Questions
# ═══════════════════════════════════════════

@router.get("/questions")
def list_questions():
    session = get_session()
    try:
        questions = session.query(Question).order_by(Question.created_at.desc()).all()
        result = []
        for q in questions:
            # Auto-expire if time passed
            if q.status == QuestionStatus.ACTIVE and q.expires_at and datetime.utcnow() > q.expires_at:
                q.status = QuestionStatus.EXPIRED
                session.commit()
            
            options_data = []
            for opt in q.options:
                options_data.append({
                    "label": opt.label,
                    "text": opt.text,
                    "is_correct": opt.is_correct,
                })
            
            answer_count = session.query(Answer).filter(Answer.question_id == q.id).count()
            correct_count = session.query(Answer).filter(Answer.question_id == q.id, Answer.is_correct == True).count()
            
            result.append({
                "id": q.id,
                "text": q.text,
                "question_type": safe_value(q.question_type),
                "correct_answer": q.correct_answer,
                "points": q.points,
                "time_limit_seconds": q.time_limit_seconds,
                "status": safe_value(q.status),
                "target_groups": q.get_target_groups(),
                "accept_late": q.accept_late,
                "options": options_data,
                "answer_count": answer_count,
                "correct_count": correct_count,
                "sent_at": q.sent_at.isoformat() if q.sent_at else None,
                "expires_at": q.expires_at.isoformat() if q.expires_at else None,
                "created_at": q.created_at.isoformat() if q.created_at else None,
            })
        return {"questions": result}
    finally:
        session.close()


@router.post("/questions")
def create_question(data: QuestionCreate):
    session = get_session()
    try:
        # Validate MCQ has a correct answer
        if data.question_type == "mcq" and not data.correct_answer.strip():
            raise HTTPException(status_code=400, detail="يجب تحديد الإجابة الصحيحة لسؤال الاختيار من متعدد")
        q = Question(
            text=data.text,
            question_type=QuestionType(data.question_type),
            correct_answer=data.correct_answer,
            points=data.points,
            time_limit_seconds=data.time_limit_seconds,
            accept_late=data.accept_late,
        )
        q.set_target_groups(data.target_groups)
        session.add(q)
        session.flush()
        
        # Add MCQ options
        if data.question_type == "mcq":
            for opt in data.options:
                session.add(QuestionOption(
                    question_id=q.id,
                    label=opt.label,
                    text=opt.text,
                    is_correct=opt.is_correct,
                ))
        
        session.commit()
        return {"success": True, "message": "تم إنشاء السؤال", "question_id": q.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/questions/{question_id}")
def delete_question(question_id: int):
    session = get_session()
    try:
        q = session.query(Question).filter(Question.id == question_id).first()
        if not q:
            raise HTTPException(status_code=404, detail="السؤال غير موجود")
        session.delete(q)
        session.commit()
        return {"success": True, "message": "تم حذف السؤال"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# ═══════════════════════════════════════════
#  Send Question via WhatsApp
# ═══════════════════════════════════════════

def _get_target_phones(session, target_groups: list) -> list:
    """Get phone numbers of targeted participants"""
    phones = set()
    
    for target in target_groups:
        if target == "all":
            # All approved tickets
            tickets = session.query(Ticket).filter(
                func.lower(Ticket.status).in_(['approved', 'activated']),
                Ticket.is_hidden == False
            ).all()
            for t in tickets:
                if t.customer and t.customer.phone:
                    phones.add(t.customer.phone)
        
        elif target in ("VIP", "Student"):
            # By ticket type
            ticket_type = TicketType.VIP if target == "VIP" else TicketType.STUDENT
            tickets = session.query(Ticket).filter(
                Ticket.ticket_type == ticket_type,
                func.lower(Ticket.status).in_(['approved', 'activated']),
                Ticket.is_hidden == False
            ).all()
            for t in tickets:
                if t.customer and t.customer.phone:
                    phones.add(t.customer.phone)
        
        elif target.startswith("group:"):
            # Custom group
            try:
                group_id = int(target.split(":")[1])
                members = session.query(QuizGroupMember).filter(QuizGroupMember.group_id == group_id).all()
                for m in members:
                    ticket = session.query(Ticket).filter(Ticket.id == m.ticket_id).first()
                    if ticket and ticket.customer and ticket.customer.phone:
                        phones.add(ticket.customer.phone)
            except (ValueError, IndexError):
                pass
    
    return list(phones)


@router.post("/questions/{question_id}/send")
async def send_question(question_id: int, background_tasks: BackgroundTasks):
    session = get_session()
    try:
        q = session.query(Question).filter(Question.id == question_id).first()
        if not q:
            raise HTTPException(status_code=404, detail="السؤال غير موجود")
        
        if q.status == QuestionStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="السؤال مفعل بالفعل")
        
        # Build message
        msg = f"❓ *سؤال المسابقة*\n\n{q.text}\n"
        
        if q.question_type == QuestionType.MCQ:
            msg += "\n"
            for opt in q.options:
                msg += f"  {opt.label}) {opt.text}\n"
            msg += f"\n📝 ابعت حرف الإجابة الصحيحة (مثال: A)"
        else:
            msg += f"\n📝 ابعت إجابتك في رسالة"
        
        msg += f"\n⏱️ عندك {q.time_limit_seconds} ثانية للإجابة"
        
        # Get target phones
        phones = _get_target_phones(session, q.get_target_groups())
        if not phones:
            raise HTTPException(status_code=400, detail="لا يوجد مشاركين مستهدفين")
        
        # Update question status
        q.status = QuestionStatus.ACTIVE
        q.sent_at = datetime.utcnow()
        q.expires_at = datetime.utcnow() + timedelta(seconds=q.time_limit_seconds)
        session.commit()
        
        # Send to all targeted phones with batch delays
        background_tasks.add_task(_send_quiz_bulk, phones, msg)
        
        return {
            "success": True,
            "message": f"تم بدء إرسال السؤال لـ {len(phones)} مشارك (مع تأخير لحماية الرقم)",
            "sent_count": len(phones),
            "expires_at": q.expires_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


async def _send_quiz_bulk(phones: list, msg: str):
    """Send quiz question to all phones with anti-ban delays."""
    import asyncio
    import random
    BATCH_SIZE = 25
    DELAY_MIN, DELAY_MAX = 3.0, 8.0
    BATCH_PAUSE_MIN, BATCH_PAUSE_MAX = 60.0, 90.0

    total = len(phones)
    for i, phone in enumerate(phones):
        try:
            await whatsapp_service.send_message(phone, msg)
            logger.info(f"✅ Quiz sent {i+1}/{total} to {phone}")
        except Exception as e:
            logger.error(f"❌ Quiz failed {i+1}/{total} to {phone}: {e}")

        if i < total - 1:
            if (i + 1) % BATCH_SIZE == 0:
                pause = random.uniform(BATCH_PAUSE_MIN, BATCH_PAUSE_MAX)
                logger.info(f"⏸️ Quiz batch {(i+1)//BATCH_SIZE} done. Pausing {pause:.0f}s...")
                await asyncio.sleep(pause)
            else:
                delay = random.uniform(DELAY_MIN, DELAY_MAX)
                logger.info(f"⏳ Waiting {delay:.1f}s...")
                await asyncio.sleep(delay)

    logger.info(f"📊 Quiz send finished: {total} phones processed")


@router.post("/questions/{question_id}/expire")
def expire_question(question_id: int):
    session = get_session()
    try:
        q = session.query(Question).filter(Question.id == question_id).first()
        if not q:
            raise HTTPException(status_code=404, detail="السؤال غير موجود")
        q.status = QuestionStatus.EXPIRED
        session.commit()
        return {"success": True, "message": "تم إنهاء السؤال"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# ═══════════════════════════════════════════
#  Answer Submission (from n8n)
# ═══════════════════════════════════════════

@router.post("/answer")
def submit_answer(data: AnswerSubmit):
    session = get_session()
    try:
        # Find the question
        question = session.query(Question).filter(Question.id == data.question_id).first()
        if not question:
            return {"success": False, "message": "السؤال غير موجود"}
        
        # Find participant by phone
        phone = data.phone
        if phone.startswith("0") and len(phone) == 11:
            phone = "20" + phone[1:]
        elif not phone.startswith("20") and len(phone) == 10:
            phone = "20" + phone
        
        customer = session.query(Customer).filter(Customer.phone == phone).first()
        if not customer:
            return {"success": False, "message": "المشارك غير موجود"}
        
        ticket = session.query(Ticket).filter(
            Ticket.customer_id == customer.id,
            Ticket.status.in_([TicketStatus.APPROVED, TicketStatus.ACTIVATED])
        ).first()
        if not ticket:
            return {"success": False, "message": "لا توجد تذكرة فعالة لهذا المشارك"}
        
        # Check if already answered
        existing = session.query(Answer).filter(
            Answer.question_id == question.id,
            Answer.ticket_id == ticket.id
        ).first()
        if existing:
            return {"success": False, "message": "تم الإجابة مسبقاً"}
        
        # Check if expired
        is_late = False
        if question.expires_at and datetime.utcnow() > question.expires_at:
            is_late = True
            if not question.accept_late:
                return {"success": False, "message": "انتهى وقت الإجابة ⏰"}
        
        # Evaluate answer
        q_type = safe_value(question.question_type)
        logger.info(f"[QUIZ DEBUG] question_id={question.id}, question_type='{q_type}', "
                     f"correct_answer='{question.correct_answer}' (repr={repr(question.correct_answer)}), "
                     f"answer_text='{data.answer_text}' (repr={repr(data.answer_text)})")
        
        result = evaluate_answer(
            answer_text=data.answer_text,
            correct_answer=question.correct_answer,
            question_type=q_type,
        )
        logger.info(f"[QUIZ DEBUG] evaluation result: {result}")
        
        points = question.points if result["is_correct"] and not is_late else 0
        
        # Save answer
        answer = Answer(
            question_id=question.id,
            ticket_id=ticket.id,
            phone=phone,
            answer_text=data.answer_text,
            is_correct=result["is_correct"],
            similarity_score=result["similarity_score"],
            points_earned=points,
            is_late=is_late,
        )
        session.add(answer)
        
        # Save sender name to ticket if guest_name is empty
        if data.sender_name and not ticket.guest_name:
            ticket.guest_name = data.sender_name
        
        session.commit()
        
        # Response message
        if result["is_correct"]:
            resp_msg = f"✅ إجابة صحيحة! +{points} نقطة"
        else:
            resp_msg = f"❌ إجابة خاطئة. الإجابة الصحيحة: {question.correct_answer}"
        
        if is_late:
            resp_msg += "\n⏰ (بعد الوقت - لم تحتسب)"
        
        return {
            "success": True,
            "is_correct": result["is_correct"],
            "similarity_score": result["similarity_score"],
            "points_earned": points,
            "response_message": resp_msg,
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# ═══════════════════════════════════════════
#  Active Question (for n8n to check)
# ═══════════════════════════════════════════

@router.get("/active-question")
def get_active_question():
    """Returns the currently active question (if any) - used by n8n"""
    session = get_session()
    try:
        # Auto-expire old questions
        expired = session.query(Question).filter(
            Question.status == QuestionStatus.ACTIVE,
            Question.expires_at < datetime.utcnow()
        ).all()
        for q in expired:
            q.status = QuestionStatus.EXPIRED
        if expired:
            session.commit()
        
        # Get current active question
        active = session.query(Question).filter(
            Question.status == QuestionStatus.ACTIVE
        ).order_by(Question.sent_at.desc()).first()
        
        if not active:
            return {"has_active": False}
        
        return {
            "has_active": True,
            "question_id": active.id,
            "question_type": safe_value(active.question_type),
            "expires_at": active.expires_at.isoformat() if active.expires_at else None,
        }
    finally:
        session.close()


# ═══════════════════════════════════════════
#  Leaderboard & Results
# ═══════════════════════════════════════════

@router.get("/leaderboard")
def get_leaderboard(group: Optional[str] = None):
    """
    Get leaderboard. Optional group filter:
    - None or "all" → all participants  
    - "VIP" / "Student" → by ticket type
    - "group:5" → custom group
    """
    session = get_session()
    try:
        # Base query: sum points per ticket
        query = session.query(
            Answer.ticket_id,
            func.sum(Answer.points_earned).label("total_points"),
            func.count(Answer.id).label("total_answers"),
            func.sum(func.cast(Answer.is_correct, Integer)).label("correct_answers"),
        ).group_by(Answer.ticket_id)
        
        results = query.all()
        
        leaderboard = []
        for row in results:
            ticket = session.query(Ticket).filter(Ticket.id == row.ticket_id).first()
            if not ticket:
                continue
            
            # Apply group filter
            if group and group != "all":
                if group in ("VIP", "Student"):
                    if safe_value(ticket.ticket_type) != group:
                        continue
                elif group.startswith("group:"):
                    try:
                        gid = int(group.split(":")[1])
                        is_member = session.query(QuizGroupMember).filter(
                            QuizGroupMember.group_id == gid,
                            QuizGroupMember.ticket_id == ticket.id
                        ).first()
                        if not is_member:
                            continue
                    except (ValueError, IndexError):
                        continue
            
            leaderboard.append({
                "ticket_id": ticket.id,
                "guest_name": ticket.guest_name or (ticket.customer.phone if ticket.customer else "—"),
                "phone": ticket.customer.phone if ticket.customer else "—",
                "ticket_type": safe_value(ticket.ticket_type),
                "total_points": int(row.total_points or 0),
                "total_answers": int(row.total_answers or 0),
                "correct_answers": int(row.correct_answers or 0),
            })
        
        # Sort by points descending
        leaderboard.sort(key=lambda x: x["total_points"], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        return {"leaderboard": leaderboard}
    finally:
        session.close()


@router.get("/answers/{question_id}")
def get_question_answers(question_id: int):
    """Get all answers for a specific question"""
    session = get_session()
    try:
        question = session.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="السؤال غير موجود")
        
        answers = session.query(Answer).filter(
            Answer.question_id == question_id
        ).order_by(Answer.answered_at.asc()).all()
        
        result = []
        for a in answers:
            ticket = session.query(Ticket).filter(Ticket.id == a.ticket_id).first()
            result.append({
                "id": a.id,
                "guest_name": ticket.guest_name if ticket else "—",
                "phone": a.phone,
                "answer_text": a.answer_text,
                "is_correct": a.is_correct,
                "similarity_score": a.similarity_score,
                "points_earned": a.points_earned,
                "is_late": a.is_late,
                "answered_at": a.answered_at.isoformat() if a.answered_at else None,
            })
        
        return {
            "question": {
                "id": question.id,
                "text": question.text,
                "correct_answer": question.correct_answer,
                "question_type": safe_value(question.question_type),
            },
            "answers": result,
            "total": len(result),
            "correct": sum(1 for a in result if a["is_correct"]),
        }
    finally:
        session.close()


@router.get("/participant/{ticket_id}")
def get_participant_results(ticket_id: int):
    """Get all results for a specific participant"""
    session = get_session()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="المشارك غير موجود")
        
        answers = session.query(Answer).filter(
            Answer.ticket_id == ticket_id
        ).order_by(Answer.answered_at.asc()).all()
        
        result = []
        total_points = 0
        for a in answers:
            question = session.query(Question).filter(Question.id == a.question_id).first()
            result.append({
                "question_text": question.text if question else "—",
                "question_type": safe_value(question.question_type) if question else "—",
                "answer_text": a.answer_text,
                "is_correct": a.is_correct,
                "similarity_score": a.similarity_score,
                "points_earned": a.points_earned,
                "is_late": a.is_late,
                "answered_at": a.answered_at.isoformat() if a.answered_at else None,
            })
            total_points += a.points_earned
        
        return {
            "participant": {
                "ticket_id": ticket.id,
                "guest_name": ticket.guest_name,
                "phone": ticket.customer.phone if ticket.customer else "—",
                "ticket_type": safe_value(ticket.ticket_type),
            },
            "total_points": total_points,
            "answers": result,
        }
    finally:
        session.close()
