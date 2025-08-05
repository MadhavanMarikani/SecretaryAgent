from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from services.database import Base

class AlertType(enum.Enum):
    EMAIL_VIP = "email_vip"
    EMAIL_EMERGENCY = "email_emergency"
    MEETING_REMINDER = "meeting_reminder"
    MORNING_BRIEFING = "morning_briefing"
    SYSTEM = "system"

class AlertPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AlertStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    DISMISSED = "dismissed"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Alert details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    priority = Column(Enum(AlertPriority), default=AlertPriority.NORMAL)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    
    # Related entities
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    calendar_event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)
    
    # Delivery settings
    send_email = Column(Boolean, default=False)
    send_push = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(Text)  # JSON for additional data
    
    # Timestamps
    scheduled_for = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    dismissed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    email = relationship("Email", back_populates="alerts")
    calendar_event = relationship("CalendarEvent", back_populates="alerts")