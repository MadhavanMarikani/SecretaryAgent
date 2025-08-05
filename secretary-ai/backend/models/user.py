from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from services.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Email settings
    email_provider = Column(String(50), default="gmail")
    email_user = Column(String(255))
    email_password = Column(Text)  # Encrypted
    imap_server = Column(String(255))
    smtp_server = Column(String(255))
    smtp_port = Column(Integer, default=587)
    
    # Google Calendar settings
    google_refresh_token = Column(Text)
    google_access_token = Column(Text)
    
    # AI preferences
    ai_tone = Column(String(50), default="professional")
    ai_language = Column(String(10), default="en")
    
    # Alert settings
    vip_senders = Column(Text)  # JSON array of email addresses
    emergency_keywords = Column(Text)  # JSON array of keywords
    morning_briefing_time = Column(String(10), default="08:00")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    emails = relationship("Email", back_populates="user")
    email_rules = relationship("EmailRule", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    alerts = relationship("Alert", back_populates="user")