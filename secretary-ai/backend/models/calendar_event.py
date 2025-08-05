from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from services.database import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Google Calendar data
    google_event_id = Column(String(255), unique=True, index=True)
    calendar_id = Column(String(255), nullable=False)
    
    # Event details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    location = Column(String(500))
    
    # Timing
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    is_all_day = Column(Boolean, default=False)
    timezone = Column(String(50), default="UTC")
    
    # Attendees
    organizer_email = Column(String(255))
    attendees = Column(Text)  # JSON array of attendee objects
    
    # Meeting details
    meeting_link = Column(String(500))
    meeting_platform = Column(String(50))  # zoom, teams, meet, etc.
    
    # AI features
    ai_summary = Column(Text)
    ai_preparation_notes = Column(Text)
    
    # Reminder settings
    reminder_sent = Column(Boolean, default=False)
    reminder_minutes_before = Column(Integer, default=15)
    
    # Status
    status = Column(String(20), default="confirmed")  # confirmed, tentative, cancelled
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="calendar_events")