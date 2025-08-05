from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

from services.database import get_db
from services.ai_service import AIService
from services.email_service import EmailService
from services.calendar_service import CalendarService
from models.user import User
from models.email import Email, EmailStatus
from models.calendar_event import CalendarEvent
from routers.auth import get_current_user

router = APIRouter()

class SummarizeRequest(BaseModel):
    subject: str
    body: str

class GenerateReplyRequest(BaseModel):
    subject: str
    body: str
    tone: Optional[str] = "professional"
    language: Optional[str] = "en"

class MorningBriefingResponse(BaseModel):
    briefing: str
    email_count: int
    event_count: int
    generated_at: datetime

class EmailSummaryResponse(BaseModel):
    summary: str
    sentiment: str
    category: str

@router.post("/summarize-email", response_model=EmailSummaryResponse)
def summarize_email(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user)
):
    """Summarize an email using AI"""
    ai_service = AIService()
    
    try:
        summary = ai_service.summarize_email(request.subject, request.body)
        sentiment = ai_service.analyze_sentiment(request.body)
        category = ai_service.categorize_email(request.subject, request.body)
        
        return EmailSummaryResponse(
            summary=summary,
            sentiment=sentiment,
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-reply")
def generate_reply(
    request: GenerateReplyRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate AI reply draft"""
    ai_service = AIService()
    
    try:
        reply_draft = ai_service.generate_reply_draft(
            request.subject,
            request.body,
            request.tone,
            request.language
        )
        
        return {"reply_draft": reply_draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/morning-briefing", response_model=MorningBriefingResponse)
def get_morning_briefing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated morning briefing"""
    ai_service = AIService()
    calendar_service = CalendarService()
    
    try:
        # Get recent important emails
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_emails = db.query(Email).filter(
            Email.user_id == current_user.id,
            Email.received_at >= yesterday,
            Email.status.in_([EmailStatus.UNREAD, EmailStatus.IMPORTANT, EmailStatus.EMERGENCY])
        ).order_by(Email.received_at.desc()).limit(10).all()
        
        # Get upcoming calendar events
        upcoming_events = calendar_service.get_upcoming_events(
            current_user.id, hours_ahead=24, db=db
        )
        
        # Format data for AI
        email_data = []
        for email in recent_emails:
            email_data.append({
                'sender_name': email.sender_name,
                'subject': email.subject,
                'summary': email.summary or email.subject,
                'priority': email.priority.value,
                'is_emergency': email.is_emergency,
                'is_from_vip': email.is_from_vip
            })
        
        event_data = []
        for event in upcoming_events:
            event_data.append({
                'title': event.title,
                'start_time': event.start_datetime.strftime("%H:%M"),
                'location': event.location or 'Not specified',
                'summary': event.ai_summary
            })
        
        # Generate briefing
        briefing_content = ai_service.generate_morning_briefing(email_data, event_data)
        
        return MorningBriefingResponse(
            briefing=briefing_content,
            email_count=len(recent_emails),
            event_count=len(upcoming_events),
            generated_at=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-meeting-info")
def extract_meeting_info(
    email_body: str,
    current_user: User = Depends(get_current_user)
):
    """Extract meeting information from email content"""
    ai_service = AIService()
    
    try:
        meeting_info = ai_service.extract_meeting_info(email_body)
        return {"meeting_info": meeting_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-sentiment")
def analyze_sentiment(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """Analyze sentiment of text"""
    ai_service = AIService()
    
    try:
        sentiment = ai_service.analyze_sentiment(text)
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/categorize-email")
def categorize_email(
    subject: str,
    body: str,
    current_user: User = Depends(get_current_user)
):
    """Categorize email content"""
    ai_service = AIService()
    
    try:
        category = ai_service.categorize_email(subject, body)
        return {"category": category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-emergency")
def detect_emergency(
    subject: str,
    body: str,
    current_user: User = Depends(get_current_user)
):
    """Detect if email content indicates an emergency"""
    ai_service = AIService()
    
    try:
        is_emergency = ai_service.detect_emergency_content(subject, body)
        return {"is_emergency": is_emergency}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/email-trends")
def get_email_insights(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email insights and trends"""
    try:
        # Get emails from the last N days
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        emails = db.query(Email).filter(
            Email.user_id == current_user.id,
            Email.received_at >= start_date
        ).all()
        
        # Calculate insights
        total_emails = len(emails)
        emergency_count = sum(1 for email in emails if email.is_emergency)
        vip_count = sum(1 for email in emails if email.is_from_vip)
        unread_count = sum(1 for email in emails if email.status == EmailStatus.UNREAD)
        
        # Sentiment analysis
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for email in emails:
            if email.sentiment:
                sentiment_counts[email.sentiment] = sentiment_counts.get(email.sentiment, 0) + 1
        
        # Top senders
        sender_counts = {}
        for email in emails:
            sender_counts[email.sender_email] = sender_counts.get(email.sender_email, 0) + 1
        
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period_days": days,
            "total_emails": total_emails,
            "emergency_emails": emergency_count,
            "vip_emails": vip_count,
            "unread_emails": unread_count,
            "sentiment_distribution": sentiment_counts,
            "top_senders": [{"email": email, "count": count} for email, count in top_senders],
            "average_per_day": round(total_emails / days, 1) if days > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))