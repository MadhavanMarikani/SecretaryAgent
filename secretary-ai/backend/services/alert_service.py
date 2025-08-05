from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from datetime import datetime, timezone, timedelta
import json

from models.alert import Alert, AlertType, AlertPriority, AlertStatus
from models.email import Email
from models.calendar_event import CalendarEvent
from models.user import User
from services.email_service import EmailService
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.email_service = EmailService()
        self.ai_service = AIService()
    
    def create_email_vip_alert(self, email: Email, user: User, db: Session) -> Alert:
        """Create alert for VIP email"""
        try:
            alert = Alert(
                user_id=user.id,
                email_id=email.id,
                title=f"VIP Email from {email.sender_name}",
                message=f"You received an important email from {email.sender_name}: {email.subject}",
                alert_type=AlertType.EMAIL_VIP,
                priority=AlertPriority.HIGH,
                send_email=True,
                send_push=True,
                metadata=json.dumps({
                    "sender_email": email.sender_email,
                    "subject": email.subject,
                    "summary": email.summary
                })
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Send immediate notification
            self._send_alert_notification(alert, user, db)
            
            return alert
        except Exception as e:
            logger.error(f"Error creating VIP email alert: {e}")
            raise
    
    def create_emergency_email_alert(self, email: Email, user: User, db: Session) -> Alert:
        """Create alert for emergency email"""
        try:
            alert = Alert(
                user_id=user.id,
                email_id=email.id,
                title=f"URGENT: Emergency Email from {email.sender_name}",
                message=f"URGENT EMAIL DETECTED from {email.sender_name}: {email.subject}. Immediate attention required.",
                alert_type=AlertType.EMAIL_EMERGENCY,
                priority=AlertPriority.URGENT,
                send_email=True,
                send_push=True,
                send_sms=True,  # Enable SMS for emergencies
                metadata=json.dumps({
                    "sender_email": email.sender_email,
                    "subject": email.subject,
                    "summary": email.summary,
                    "emergency_detected": True
                })
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Send immediate high-priority notification
            self._send_alert_notification(alert, user, db)
            
            return alert
        except Exception as e:
            logger.error(f"Error creating emergency email alert: {e}")
            raise
    
    def create_meeting_reminder_alert(self, calendar_event: CalendarEvent, user: User, db: Session) -> Alert:
        """Create meeting reminder alert"""
        try:
            time_until = calendar_event.start_datetime - datetime.now(timezone.utc)
            minutes_until = int(time_until.total_seconds() / 60)
            
            alert = Alert(
                user_id=user.id,
                calendar_event_id=calendar_event.id,
                title=f"Meeting Reminder: {calendar_event.title}",
                message=f"Your meeting '{calendar_event.title}' starts in {minutes_until} minutes.",
                alert_type=AlertType.MEETING_REMINDER,
                priority=AlertPriority.NORMAL,
                send_email=False,
                send_push=True,
                metadata=json.dumps({
                    "meeting_title": calendar_event.title,
                    "meeting_link": calendar_event.meeting_link,
                    "location": calendar_event.location,
                    "minutes_until": minutes_until,
                    "preparation_notes": calendar_event.ai_preparation_notes
                })
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Send notification
            self._send_alert_notification(alert, user, db)
            
            return alert
        except Exception as e:
            logger.error(f"Error creating meeting reminder alert: {e}")
            raise
    
    def create_morning_briefing_alert(self, user: User, briefing_content: str, db: Session) -> Alert:
        """Create morning briefing alert"""
        try:
            alert = Alert(
                user_id=user.id,
                title="Your Daily Morning Briefing",
                message=briefing_content,
                alert_type=AlertType.MORNING_BRIEFING,
                priority=AlertPriority.NORMAL,
                send_email=True,
                send_push=True,
                metadata=json.dumps({
                    "briefing_type": "daily",
                    "generated_at": datetime.now(timezone.utc).isoformat()
                })
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Send briefing
            self._send_alert_notification(alert, user, db)
            
            return alert
        except Exception as e:
            logger.error(f"Error creating morning briefing alert: {e}")
            raise
    
    def _send_alert_notification(self, alert: Alert, user: User, db: Session):
        """Send alert notification via configured channels"""
        try:
            # Send email notification
            if alert.send_email and user.email:
                self._send_email_notification(alert, user)
            
            # Send push notification (placeholder - would integrate with push service)
            if alert.send_push:
                self._send_push_notification(alert, user)
            
            # Send SMS notification (placeholder - would integrate with SMS service)
            if alert.send_sms:
                self._send_sms_notification(alert, user)
            
            # Mark alert as sent
            alert.status = AlertStatus.SENT
            alert.sent_at = datetime.now(timezone.utc)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
    
    def _send_email_notification(self, alert: Alert, user: User):
        """Send email notification"""
        try:
            subject = f"Secretary AI: {alert.title}"
            
            # Create HTML email body
            html_body = f"""
            <html>
            <body>
                <h2>{alert.title}</h2>
                <p>{alert.message}</p>
                
                {self._format_alert_metadata(alert)}
                
                <hr>
                <p><small>This notification was sent by your Secretary AI assistant.</small></p>
            </body>
            </html>
            """
            
            # Plain text version
            text_body = f"""
            {alert.title}
            
            {alert.message}
            
            ---
            This notification was sent by your Secretary AI assistant.
            """
            
            success = self.email_service.send_email(
                user=user,
                to_email=user.email,
                subject=subject,
                body=text_body,
                body_html=html_body
            )
            
            if success:
                logger.info(f"Email notification sent for alert {alert.id}")
            else:
                logger.error(f"Failed to send email notification for alert {alert.id}")
                
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def _send_push_notification(self, alert: Alert, user: User):
        """Send push notification (placeholder)"""
        # This would integrate with a push notification service like Firebase
        logger.info(f"Push notification would be sent for alert {alert.id}: {alert.title}")
    
    def _send_sms_notification(self, alert: Alert, user: User):
        """Send SMS notification (placeholder)"""
        # This would integrate with an SMS service like Twilio
        logger.info(f"SMS notification would be sent for alert {alert.id}: {alert.title}")
    
    def _format_alert_metadata(self, alert: Alert) -> str:
        """Format alert metadata for display"""
        try:
            if not alert.metadata:
                return ""
            
            metadata = json.loads(alert.metadata)
            
            if alert.alert_type == AlertType.EMAIL_VIP or alert.alert_type == AlertType.EMAIL_EMERGENCY:
                return f"""
                <div style="background-color: #f5f5f5; padding: 10px; margin: 10px 0;">
                    <strong>Email Details:</strong><br>
                    From: {metadata.get('sender_email', 'Unknown')}<br>
                    Subject: {metadata.get('subject', 'No subject')}<br>
                    Summary: {metadata.get('summary', 'No summary available')}
                </div>
                """
            
            elif alert.alert_type == AlertType.MEETING_REMINDER:
                return f"""
                <div style="background-color: #e3f2fd; padding: 10px; margin: 10px 0;">
                    <strong>Meeting Details:</strong><br>
                    Location: {metadata.get('location', 'Not specified')}<br>
                    {f"Meeting Link: {metadata.get('meeting_link')}<br>" if metadata.get('meeting_link') else ""}
                    {f"Preparation Notes: {metadata.get('preparation_notes')}<br>" if metadata.get('preparation_notes') else ""}
                </div>
                """
            
            return ""
        except Exception as e:
            logger.error(f"Error formatting alert metadata: {e}")
            return ""
    
    def get_user_alerts(self, user_id: int, limit: int = 50, db: Session = None) -> List[Alert]:
        """Get alerts for a user"""
        return db.query(Alert).filter(
            Alert.user_id == user_id
        ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    def get_unread_alerts(self, user_id: int, db: Session) -> List[Alert]:
        """Get unread alerts for a user"""
        return db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT])
        ).order_by(Alert.created_at.desc()).all()
    
    def mark_alert_as_read(self, alert_id: int, user_id: int, db: Session) -> bool:
        """Mark alert as read"""
        try:
            alert = db.query(Alert).filter(
                Alert.id == alert_id,
                Alert.user_id == user_id
            ).first()
            
            if alert:
                alert.status = AlertStatus.READ
                alert.read_at = datetime.now(timezone.utc)
                db.commit()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error marking alert as read: {e}")
            return False
    
    def dismiss_alert(self, alert_id: int, user_id: int, db: Session) -> bool:
        """Dismiss an alert"""
        try:
            alert = db.query(Alert).filter(
                Alert.id == alert_id,
                Alert.user_id == user_id
            ).first()
            
            if alert:
                alert.status = AlertStatus.DISMISSED
                alert.dismissed_at = datetime.now(timezone.utc)
                db.commit()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error dismissing alert: {e}")
            return False
    
    def get_pending_alerts(self, db: Session) -> List[Alert]:
        """Get all pending alerts that need to be processed"""
        return db.query(Alert).filter(
            Alert.status == AlertStatus.PENDING,
            Alert.scheduled_for <= datetime.now(timezone.utc)
        ).all()