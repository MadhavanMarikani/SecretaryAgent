from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from services.database import Base

class EmailStatus(enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    IMPORTANT = "important"
    EMERGENCY = "emergency"

class EmailPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Email metadata
    message_id = Column(String(255), unique=True, index=True)
    sender_email = Column(String(255), nullable=False, index=True)
    sender_name = Column(String(255))
    recipient_email = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    body = Column(Text)
    body_html = Column(Text)
    
    # Status and priority
    status = Column(Enum(EmailStatus), default=EmailStatus.UNREAD)
    priority = Column(Enum(EmailPriority), default=EmailPriority.NORMAL)
    is_emergency = Column(Boolean, default=False)
    is_from_vip = Column(Boolean, default=False)
    
    # AI-generated content
    summary = Column(Text)
    ai_suggested_reply = Column(Text)
    sentiment = Column(String(50))
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="emails")
    alerts = relationship("Alert", back_populates="email")

class EmailRule(Base):
    __tablename__ = "email_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Rule conditions
    sender_pattern = Column(String(255))  # Email pattern to match
    subject_pattern = Column(String(255))  # Subject pattern to match
    body_pattern = Column(String(255))     # Body pattern to match
    
    # Rule actions
    set_priority = Column(Enum(EmailPriority))
    mark_as_emergency = Column(Boolean, default=False)
    send_alert = Column(Boolean, default=False)
    auto_reply = Column(Boolean, default=False)
    auto_reply_template = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="email_rules")