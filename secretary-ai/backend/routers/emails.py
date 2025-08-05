from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from services.database import get_db
from services.email_service import EmailService
from services.ai_service import AIService
from models.user import User
from models.email import Email, EmailStatus, EmailPriority
from routers.auth import get_current_user

router = APIRouter()

class EmailResponse(BaseModel):
    id: int
    sender_email: str
    sender_name: str
    subject: str
    body: str
    summary: str
    ai_suggested_reply: str
    sentiment: str
    status: str
    priority: str
    is_emergency: bool
    is_from_vip: bool
    received_at: datetime
    
    class Config:
        from_attributes = True

class EmailConfigUpdate(BaseModel):
    email_user: Optional[str] = None
    email_password: Optional[str] = None
    imap_server: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    vip_senders: Optional[List[str]] = None
    emergency_keywords: Optional[List[str]] = None

class ReplyDraftRequest(BaseModel):
    email_id: int
    tone: Optional[str] = "professional"

class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    body_html: Optional[str] = None

@router.get("/", response_model=List[EmailResponse])
def get_emails(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's emails with optional filtering"""
    query = db.query(Email).filter(Email.user_id == current_user.id)
    
    if status:
        try:
            email_status = EmailStatus(status)
            query = query.filter(Email.status == email_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    if priority:
        try:
            email_priority = EmailPriority(priority)
            query = query.filter(Email.priority == email_priority)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid priority")
    
    emails = query.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()
    return emails

@router.get("/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific email"""
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return email

@router.put("/{email_id}/status")
def update_email_status(
    email_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update email status"""
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    try:
        email_status = EmailStatus(status)
        email.status = email_status
        db.commit()
        return {"message": "Email status updated"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

@router.post("/sync")
def sync_emails(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually sync emails"""
    if not current_user.email_user or not current_user.email_password:
        raise HTTPException(
            status_code=400,
            detail="Email configuration not set up"
        )
    
    email_service = EmailService()
    try:
        new_emails = email_service.fetch_new_emails(current_user, db)
        return {
            "message": f"Synced {len(new_emails)} new emails",
            "count": len(new_emails)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reply-draft")
def generate_reply_draft(
    request: ReplyDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI reply draft for an email"""
    email = db.query(Email).filter(
        Email.id == request.email_id,
        Email.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    ai_service = AIService()
    try:
        reply_draft = ai_service.generate_reply_draft(
            email.subject,
            email.body,
            request.tone,
            current_user.ai_language
        )
        
        # Update the email with new draft
        email.ai_suggested_reply = reply_draft
        db.commit()
        
        return {"reply_draft": reply_draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
def send_email(
    request: SendEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send an email"""
    if not current_user.email_user or not current_user.email_password:
        raise HTTPException(
            status_code=400,
            detail="Email configuration not set up"
        )
    
    email_service = EmailService()
    try:
        success = email_service.send_email(
            current_user,
            request.to_email,
            request.subject,
            request.body,
            request.body_html
        )
        
        if success:
            return {"message": "Email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
def get_email_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email statistics summary"""
    total_emails = db.query(Email).filter(Email.user_id == current_user.id).count()
    unread_emails = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.status == EmailStatus.UNREAD
    ).count()
    urgent_emails = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.priority == EmailPriority.URGENT
    ).count()
    vip_emails = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_from_vip == True
    ).count()
    
    return {
        "total_emails": total_emails,
        "unread_emails": unread_emails,
        "urgent_emails": urgent_emails,
        "vip_emails": vip_emails
    }

@router.put("/config")
def update_email_config(
    config: EmailConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update email configuration"""
    import json
    
    if config.email_user is not None:
        current_user.email_user = config.email_user
    if config.email_password is not None:
        current_user.email_password = config.email_password
    if config.imap_server is not None:
        current_user.imap_server = config.imap_server
    if config.smtp_server is not None:
        current_user.smtp_server = config.smtp_server
    if config.smtp_port is not None:
        current_user.smtp_port = config.smtp_port
    if config.vip_senders is not None:
        current_user.vip_senders = json.dumps(config.vip_senders)
    if config.emergency_keywords is not None:
        current_user.emergency_keywords = json.dumps(config.emergency_keywords)
    
    db.commit()
    return {"message": "Email configuration updated"}