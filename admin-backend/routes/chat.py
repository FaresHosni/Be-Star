"""
Chat Widget API Routes - For n8n integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from models import get_session, ChatMessage

router = APIRouter()


class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    phone: Optional[str] = None


class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    is_from_customer: bool
    timestamp: str


@router.post("/send")
async def send_message(data: ChatMessageRequest):
    """
    Send a message from the chat widget
    This endpoint is connected to n8n workflow
    """
    session = get_session()
    try:
        # Generate session ID if not provided
        session_id = data.session_id or str(uuid.uuid4())
        
        # Save message
        chat_msg = ChatMessage(
            session_id=session_id,
            phone=data.phone,
            message=data.message,
            is_from_customer=True
        )
        session.add(chat_msg)
        session.commit()
        
        return {
            "success": True,
            "session_id": session_id,
            "message_id": chat_msg.id,
            "data": {
                "session_id": session_id,
                "phone": data.phone,
                "message": data.message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/reply")
async def receive_reply(session_id: str, message: str):
    """
    Receive reply from n8n workflow (AI agent response)
    """
    session = get_session()
    try:
        chat_msg = ChatMessage(
            session_id=session_id,
            message=message,
            is_from_customer=False
        )
        session.add(chat_msg)
        session.commit()
        
        return {
            "success": True,
            "message_id": chat_msg.id
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    session = get_session()
    try:
        messages = session.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": m.id,
                    "message": m.message,
                    "is_from_customer": m.is_from_customer,
                    "timestamp": m.created_at.isoformat()
                } for m in messages
            ]
        }
    finally:
        session.close()


@router.get("/webhook/n8n")
async def n8n_webhook_get():
    """
    GET endpoint for n8n webhook testing
    """
    return {"status": "ready", "message": "Chat webhook is active"}


@router.post("/webhook/n8n")
async def n8n_webhook_post(data: dict):
    """
    POST endpoint for receiving messages from n8n
    This is called by n8n to send AI responses back to the chat widget
    """
    session = get_session()
    try:
        session_id = data.get("session_id")
        message = data.get("message")
        
        if not session_id or not message:
            raise HTTPException(status_code=400, detail="session_id and message are required")
        
        chat_msg = ChatMessage(
            session_id=session_id,
            message=message,
            is_from_customer=False
        )
        session.add(chat_msg)
        session.commit()
        
        return {
            "success": True,
            "message_id": chat_msg.id,
            "session_id": session_id
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
