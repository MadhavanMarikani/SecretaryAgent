import asyncio
import schedule
import time
import threading
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from typing import List

from services.database import SessionLocal
from services.email_service import EmailService
from services.calendar_service import CalendarService
from services.alert_service import AlertService
from services.ai_service import AIService
from models.user import User
from models.email import Email, EmailStatus
from models.calendar_event import CalendarEvent
from models.alert import Alert, AlertType

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    def __init__(self):
        self.email_service = EmailService()
        self.calendar_service = CalendarService()
        self.alert_service = AlertService()
        self.ai_service = AIService()
        self.running = False
    
    def start(self):
        """Start background tasks"""
        self.running = True
        
        # Schedule tasks
        schedule.every(5).minutes.do(self.check_new_emails)
        schedule.every(10).minutes.do(self.sync_calendar_events)
        schedule.every(1).minutes.do(self.send_meeting_reminders)
        schedule.every().day.at("08:00").do(self.send_morning_briefings)
        schedule.every(30).seconds.do(self.process_pending_alerts)
        
        # Start scheduler in separate thread
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("Background tasks started")
    
    def stop(self):
        """Stop background tasks"""
        self.running = False
        logger.info("Background tasks stopped")
    
    def _run_scheduler(self):
        """Run the task scheduler"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(5)
    
    def check_new_emails(self):
        """Check for new emails for all users"""
        try:
            db = SessionLocal()
            users = db.query(User).filter(
                User.is_active == True,
                User.email_user.isnot(None)
            ).all()
            
            for user in users:
                try:
                    new_emails = self.email_service.fetch_new_emails(user, db)
                    
                    for email in new_emails:
                        self._process_new_email(email, user, db)
                        
                    if new_emails:
                        logger.info(f"Processed {len(new_emails)} new emails for user {user.id}")
                        
                except Exception as e:
                    logger.error(f"Error checking emails for user {user.id}: {e}")
                    continue
            
            db.close()
        except Exception as e:
            logger.error(f"Error in check_new_emails: {e}")
    
    def _process_new_email(self, email: Email, user: User, db: Session):
        """Process a new email and create alerts if necessary"""
        try:
            # Create VIP alert
            if email.is_from_vip:
                self.alert_service.create_email_vip_alert(email, user, db)
            
            # Create emergency alert
            if email.is_emergency:
                self.alert_service.create_emergency_email_alert(email, user, db)
            
        except Exception as e:
            logger.error(f"Error processing new email {email.id}: {e}")
    
    def sync_calendar_events(self):
        """Sync calendar events for all users"""
        try:
            db = SessionLocal()
            users = db.query(User).filter(
                User.is_active == True,
                User.google_access_token.isnot(None)
            ).all()
            
            for user in users:
                try:
                    events = self.calendar_service.fetch_calendar_events(user, db)
                    if events:
                        logger.info(f"Synced {len(events)} calendar events for user {user.id}")
                        
                except Exception as e:
                    logger.error(f"Error syncing calendar for user {user.id}: {e}")
                    continue
            
            db.close()
        except Exception as e:
            logger.error(f"Error in sync_calendar_events: {e}")
    
    def send_meeting_reminders(self):
        """Send meeting reminders"""
        try:
            db = SessionLocal()
            
            # Get events that need reminders
            events_needing_reminders = self.calendar_service.get_events_needing_reminders(db)
            
            for event in events_needing_reminders:
                try:
                    user = db.query(User).filter(User.id == event.user_id).first()
                    if user:
                        self.alert_service.create_meeting_reminder_alert(event, user, db)
                        self.calendar_service.mark_reminder_sent(event, db)
                        
                except Exception as e:
                    logger.error(f"Error sending reminder for event {event.id}: {e}")
                    continue
            
            if events_needing_reminders:
                logger.info(f"Sent {len(events_needing_reminders)} meeting reminders")
            
            db.close()
        except Exception as e:
            logger.error(f"Error in send_meeting_reminders: {e}")
    
    def send_morning_briefings(self):
        """Send morning briefings to all users"""
        try:
            db = SessionLocal()
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # Check if user wants morning briefings at this time
                    current_time = datetime.now().strftime("%H:%M")
                    if current_time != user.morning_briefing_time:
                        continue
                    
                    # Check if briefing already sent today
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    existing_briefing = db.query(Alert).filter(
                        Alert.user_id == user.id,
                        Alert.alert_type == AlertType.MORNING_BRIEFING,
                        Alert.created_at >= today_start
                    ).first()
                    
                    if existing_briefing:
                        continue
                    
                    # Generate briefing
                    briefing_content = self._generate_daily_briefing(user, db)
                    
                    # Create briefing alert
                    self.alert_service.create_morning_briefing_alert(user, briefing_content, db)
                    
                    logger.info(f"Sent morning briefing to user {user.id}")
                    
                except Exception as e:
                    logger.error(f"Error sending morning briefing to user {user.id}: {e}")
                    continue
            
            db.close()
        except Exception as e:
            logger.error(f"Error in send_morning_briefings: {e}")
    
    def _generate_daily_briefing(self, user: User, db: Session) -> str:
        """Generate daily briefing for user"""
        try:
            # Get recent important emails
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            recent_emails = db.query(Email).filter(
                Email.user_id == user.id,
                Email.received_at >= yesterday,
                Email.status.in_([EmailStatus.UNREAD, EmailStatus.IMPORTANT, EmailStatus.EMERGENCY])
            ).order_by(Email.received_at.desc()).limit(10).all()
            
            # Get upcoming calendar events
            upcoming_events = self.calendar_service.get_upcoming_events(
                user.id, hours_ahead=24, db=db
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
            
            # Generate briefing with AI
            briefing = self.ai_service.generate_morning_briefing(email_data, event_data)
            
            return briefing
            
        except Exception as e:
            logger.error(f"Error generating daily briefing: {e}")
            return "Good morning! Your briefing is being prepared. Please check back shortly."
    
    def process_pending_alerts(self):
        """Process pending alerts"""
        try:
            db = SessionLocal()
            pending_alerts = self.alert_service.get_pending_alerts(db)
            
            for alert in pending_alerts:
                try:
                    user = db.query(User).filter(User.id == alert.user_id).first()
                    if user:
                        self.alert_service._send_alert_notification(alert, user, db)
                        
                except Exception as e:
                    logger.error(f"Error processing alert {alert.id}: {e}")
                    continue
            
            db.close()
        except Exception as e:
            logger.error(f"Error in process_pending_alerts: {e}")

# Global instance
background_manager = BackgroundTaskManager()

def start_background_tasks():
    """Start background tasks"""
    background_manager.start()

def stop_background_tasks():
    """Stop background tasks"""
    background_manager.stop()