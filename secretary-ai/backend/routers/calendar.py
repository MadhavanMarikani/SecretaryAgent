from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from services.database import get_db
from services.calendar_service import CalendarService
from models.user import User
from models.calendar_event import CalendarEvent
from routers.auth import get_current_user

router = APIRouter()

class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    start_datetime: datetime
    end_datetime: datetime
    is_all_day: bool
    organizer_email: str
    meeting_link: str
    meeting_platform: str
    ai_summary: str
    ai_preparation_notes: str
    status: str
    
    class Config:
        from_attributes = True

class CalendarAuthResponse(BaseModel):
    authorization_url: str

@router.get("/auth/url")
def get_calendar_auth_url(
    current_user: User = Depends(get_current_user)
):
    """Get Google Calendar authorization URL"""
    calendar_service = CalendarService()
    try:
        auth_url = calendar_service.get_authorization_url(current_user.id)
        return CalendarAuthResponse(authorization_url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/callback")
def handle_calendar_auth_callback(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle Google Calendar OAuth callback"""
    calendar_service = CalendarService()
    try:
        success = calendar_service.handle_oauth_callback(code, current_user, db)
        if success:
            return {"message": "Calendar connected successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to connect calendar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events", response_model=List[CalendarEventResponse])
def get_calendar_events(
    days_ahead: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar events"""
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id
    ).order_by(CalendarEvent.start_datetime).all()
    
    return events

@router.get("/events/{event_id}", response_model=CalendarEventResponse)
def get_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific calendar event"""
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@router.post("/sync")
def sync_calendar_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually sync calendar events"""
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=400,
            detail="Calendar not connected. Please authorize first."
        )
    
    calendar_service = CalendarService()
    try:
        events = calendar_service.fetch_calendar_events(current_user, db)
        return {
            "message": f"Synced {len(events)} calendar events",
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming")
def get_upcoming_events(
    hours_ahead: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming events"""
    calendar_service = CalendarService()
    events = calendar_service.get_upcoming_events(current_user.id, hours_ahead, db)
    
    return [
        {
            "id": event.id,
            "title": event.title,
            "start_datetime": event.start_datetime,
            "location": event.location,
            "meeting_link": event.meeting_link,
            "ai_summary": event.ai_summary
        }
        for event in events
    ]

@router.get("/stats/summary")
def get_calendar_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar statistics"""
    calendar_service = CalendarService()
    
    total_events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id
    ).count()
    
    upcoming_events = calendar_service.get_upcoming_events(
        current_user.id, hours_ahead=24, db=db
    )
    
    events_with_meetings = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.meeting_link.isnot(None)
    ).count()
    
    return {
        "total_events": total_events,
        "upcoming_24h": len(upcoming_events),
        "events_with_meetings": events_with_meetings,
        "calendar_connected": bool(current_user.google_access_token)
    }