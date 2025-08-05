import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
import asyncio
import logging
from sqlalchemy.orm import Session

from models.email import Email, EmailStatus, EmailPriority
from models.user import User
from services.ai_service import AIService
from services.database import get_db

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.ai_service = AIService()
    
    def connect_imap(self, user: User) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server"""
        try:
            mail = imaplib.IMAP4_SSL(user.imap_server or "imap.gmail.com")
            mail.login(user.email_user, user.email_password)
            return mail
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            raise
    
    def connect_smtp(self, user: User) -> smtplib.SMTP:
        """Connect to SMTP server"""
        try:
            smtp = smtplib.SMTP(user.smtp_server or "smtp.gmail.com", user.smtp_port or 587)
            smtp.starttls()
            smtp.login(user.email_user, user.email_password)
            return smtp
        except Exception as e:
            logger.error(f"SMTP connection failed: {e}")
            raise
    
    def fetch_new_emails(self, user: User, db: Session) -> List[Email]:
        """Fetch new emails from IMAP server"""
        try:
            mail = self.connect_imap(user)
            mail.select("INBOX")
            
            # Search for unread emails
            status, message_ids = mail.search(None, "UNSEEN")
            
            emails = []
            if message_ids[0]:
                for msg_id in message_ids[0].split():
                    try:
                        email_obj = self._process_email_message(mail, msg_id, user, db)
                        if email_obj:
                            emails.append(email_obj)
                    except Exception as e:
                        logger.error(f"Error processing email {msg_id}: {e}")
                        continue
            
            mail.close()
            mail.logout()
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def _process_email_message(self, mail: imaplib.IMAP4_SSL, msg_id: bytes, user: User, db: Session) -> Optional[Email]:
        """Process individual email message"""
        try:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract email data
            message_id = email_message.get("Message-ID", "")
            sender = email_message.get("From", "")
            recipient = email_message.get("To", "")
            subject = self._decode_header(email_message.get("Subject", ""))
            date_str = email_message.get("Date", "")
            
            # Parse sender email
            sender_email = re.findall(r'[\w\.-]+@[\w\.-]+', sender)
            sender_email = sender_email[0] if sender_email else sender
            
            # Parse sender name
            sender_name = sender.split("<")[0].strip().strip('"') if "<" in sender else sender_email
            
            # Extract body
            body, body_html = self._extract_email_body(email_message)
            
            # Parse date
            received_at = self._parse_email_date(date_str)
            
            # Check if email already exists
            existing_email = db.query(Email).filter(Email.message_id == message_id).first()
            if existing_email:
                return existing_email
            
            # Create email object
            email_obj = Email(
                user_id=user.id,
                message_id=message_id,
                sender_email=sender_email,
                sender_name=sender_name,
                recipient_email=recipient,
                subject=subject,
                body=body,
                body_html=body_html,
                received_at=received_at
            )
            
            # AI processing
            self._process_with_ai(email_obj, user)
            
            # Check VIP status
            email_obj.is_from_vip = self._check_vip_sender(sender_email, user)
            
            # Check emergency status
            email_obj.is_emergency = self._check_emergency_keywords(subject + " " + body, user)
            
            # Set priority
            if email_obj.is_emergency:
                email_obj.priority = EmailPriority.URGENT
                email_obj.status = EmailStatus.EMERGENCY
            elif email_obj.is_from_vip:
                email_obj.priority = EmailPriority.HIGH
                email_obj.status = EmailStatus.IMPORTANT
            
            db.add(email_obj)
            db.commit()
            db.refresh(email_obj)
            
            return email_obj
            
        except Exception as e:
            logger.error(f"Error processing email message: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        try:
            decoded = decode_header(header)
            if decoded[0][1]:
                return decoded[0][0].decode(decoded[0][1])
            return str(decoded[0][0])
        except:
            return header
    
    def _extract_email_body(self, email_message) -> tuple:
        """Extract plain text and HTML body from email"""
        body = ""
        body_html = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                elif part.get_content_type() == "text/html":
                    body_html = part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            if email_message.get_content_type() == "text/plain":
                body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
            elif email_message.get_content_type() == "text/html":
                body_html = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
        
        # If no plain text, extract from HTML
        if not body and body_html:
            import re
            body = re.sub('<[^<]+?>', '', body_html)
        
        return body, body_html
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now(timezone.utc)
    
    def _process_with_ai(self, email_obj: Email, user: User):
        """Process email with AI for summary and reply suggestions"""
        try:
            # Generate summary
            email_obj.summary = self.ai_service.summarize_email(
                email_obj.subject, 
                email_obj.body
            )
            
            # Generate suggested reply
            email_obj.ai_suggested_reply = self.ai_service.generate_reply_draft(
                email_obj.subject,
                email_obj.body,
                user.ai_tone,
                user.ai_language
            )
            
            # Analyze sentiment
            email_obj.sentiment = self.ai_service.analyze_sentiment(email_obj.body)
            
        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
    
    def _check_vip_sender(self, sender_email: str, user: User) -> bool:
        """Check if sender is in VIP list"""
        try:
            if user.vip_senders:
                vip_list = json.loads(user.vip_senders)
                return sender_email.lower() in [vip.lower() for vip in vip_list]
        except:
            pass
        return False
    
    def _check_emergency_keywords(self, text: str, user: User) -> bool:
        """Check if email contains emergency keywords"""
        try:
            if user.emergency_keywords:
                keywords = json.loads(user.emergency_keywords)
                text_lower = text.lower()
                return any(keyword.lower() in text_lower for keyword in keywords)
        except:
            pass
        return False
    
    def send_email(self, user: User, to_email: str, subject: str, body: str, body_html: str = None) -> bool:
        """Send email via SMTP"""
        try:
            smtp = self.connect_smtp(user)
            
            msg = MIMEMultipart("alternative")
            msg["From"] = user.email_user
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Add plain text part
            msg.attach(MIMEText(body, "plain"))
            
            # Add HTML part if provided
            if body_html:
                msg.attach(MIMEText(body_html, "html"))
            
            smtp.send_message(msg)
            smtp.quit()
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def mark_as_read(self, email_obj: Email, db: Session):
        """Mark email as read"""
        email_obj.status = EmailStatus.READ
        db.commit()
    
    def get_emails_by_priority(self, user_id: int, priority: EmailPriority, db: Session) -> List[Email]:
        """Get emails by priority"""
        return db.query(Email).filter(
            Email.user_id == user_id,
            Email.priority == priority
        ).order_by(Email.received_at.desc()).all()
    
    def get_unread_emails(self, user_id: int, db: Session) -> List[Email]:
        """Get unread emails"""
        return db.query(Email).filter(
            Email.user_id == user_id,
            Email.status == EmailStatus.UNREAD
        ).order_by(Email.received_at.desc()).all()