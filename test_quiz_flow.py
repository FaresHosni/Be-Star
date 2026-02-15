
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
# Force database path
os.environ["DATABASE_URL"] = "sqlite:///backend/data/bestar.db"

# Import models and services
from backend.models import get_session, Question, QuestionOption, Answer, QuestionType, QuestionStatus, Ticket, TicketStatus, TicketType, Customer, init_db
from backend.routes.quiz import submit_answer, AnswerSubmit

def setup_test_data():
    print("Setting up test data...")
    init_db()  # Ensure DB is migrated
    session = get_session()
    try:
        # Create Customer
        customer_phone = "201234567890"
        customer = session.query(Customer).filter(Customer.phone == customer_phone).first()
        if not customer:
            customer = Customer(name="Tester", phone=customer_phone, email="test@example.com")
            session.add(customer)
            session.commit()
            session.refresh(customer)
        
        # Create Ticket
        ticket_code = "TEST01"
        existing_ticket = session.query(Ticket).filter(Ticket.code == ticket_code).first()
        if existing_ticket:
            session.delete(existing_ticket)
            session.commit()
            
        ticket = Ticket(
            code=ticket_code,
            ticket_type=TicketType.VIP,
            status=TicketStatus.ACTIVATED,
            price=500,
            customer_id=customer.id,
            guest_name="Tester",
            guest_phone=customer_phone,
            is_hidden=False
        )
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        print(f"Ticket created: {ticket.code} for {customer.phone}")
        
        return ticket.id, customer.phone
    finally:
        session.close()

def create_question(text, q_type, correct, points=10, time_limit=60):
    session = get_session()
    try:
        q = Question(
            text=text,
            question_type=q_type,
            correct_answer=correct,
            points=points,
            time_limit_seconds=time_limit,
            status=QuestionStatus.ACTIVE,
            sent_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=time_limit),
            accept_late=False
        )
        session.add(q)
        session.commit()
        session.refresh(q)
        
        if q_type == QuestionType.MCQ:
            opt1 = QuestionOption(question_id=q.id, label="A", text="Option A", is_correct=(correct=="A"))
            opt2 = QuestionOption(question_id=q.id, label="B", text="Option B", is_correct=(correct=="B"))
            session.add_all([opt1, opt2])
            session.commit()
            
        return q.id
    finally:
        session.close()

def run_tests():
    print("Starting Quiz Flow Test...")
    
    # 1. Setup
    ticket_id, phone = setup_test_data()
    
    # 2. Test MCQ Correct
    print("\nTesting MCQ Correct Answer...")
    q1_id = create_question("Capital of Egypt?", QuestionType.MCQ, "A")
    
    response = submit_answer(AnswerSubmit(
        phone=phone,
        question_id=q1_id,
        answer_text="A"
    ))
    # Check checks
    if response["is_correct"] == True and response["points_earned"] == 10:
        print("MCQ Correct Verified")
    else:
        print(f"MCQ Failed: {response}")
    
    # 3. Test Fuzzy Correct
    print("\nTesting Fuzzy Answer...")
    q2_id = create_question("Event Name?", QuestionType.COMPLETION, "Be Star", points=20)
    
    response = submit_answer(AnswerSubmit(
        phone=phone,
        question_id=q2_id,
        answer_text="be start event" 
    ))
    
    if response["is_correct"]:
        print(f"Fuzzy Logic Verified (Score: {response['similarity_score']})")
    else:
        print(f"Fuzzy Logic Failed (Score: {response['similarity_score']})")
        
    # 4. Test Time Expiry
    print("\nTesting Time Expiry...")
    
    session = get_session()
    q3 = Question(
        text="Late Question",
        question_type=QuestionType.MCQ,
        correct_answer="A",
        points=5,
        time_limit_seconds=60,
        status=QuestionStatus.ACTIVE,
        sent_at=datetime.utcnow() - timedelta(seconds=120),
        expires_at=datetime.utcnow() - timedelta(seconds=60), # Expired 60s ago
        accept_late=False
    )
    session.add(q3)
    session.commit()
    q3_id = q3.id
    session.close()
    
    response = submit_answer(AnswerSubmit(
        phone=phone,
        question_id=q3_id,
        answer_text="A"
    ))
    
    if not response["success"] and "انتهى وقت" in response["message"]:
        print("Time Expiry Verified (Blocked)")
    elif response.get("is_late"):
        print("Time Expiry Verified (Marked Late)")
    else:
        print("Time Expiry Failed (Accepted as valid)")

    print("\nAll Verification Steps Completed!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
