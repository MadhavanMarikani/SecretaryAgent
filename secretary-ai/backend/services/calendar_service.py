from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from models.calendar_event import CalendarEvent
from models.user import User
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self):
        self.ai_service = AIService()
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events'
        ]
    
    def get_authorization_url(self, user_id: int) -> str:
        """Get Google OAuth authorization URL"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=str(user_id)
            )
            
            return authorization_url
        except Exception as e:
            logger.error(f"Error getting authorization URL: {e}")
            raise
    
    def handle_oauth_callback(self, code: str, user: User, db: Session) -> bool:
        """Handle OAuth callback and store tokens"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Store tokens in user record
            user.google_access_token = credentials.token
            user.google_refresh_token = credentials.refresh_token
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            return False
    
    def get_credentials(self, user: User) -> Optional[Credentials]:
        """Get valid Google credentials for user"""
        try:
            if not user.google_access_token:
                return None
            
            creds = Credentials(
                token=user.google_access_token,
                refresh_token=user.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                scopes=self.scopes
            )
            
            # Refresh if needed
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update stored tokens
                user.google_access_token = creds.token
                # Note: refresh_token might be None on refresh
            
            return creds
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return None
    
    def fetch_calendar_events(self, user: User, db: Session, days_ahead: int = 7) -> List[CalendarEvent]:
        """Fetch calendar events from Google Calendar"""
        try:
            creds = self.get_credentials(user)
            if not creds:
                logger.warning("No valid credentials for calendar access")
                return []
            
            service = build('calendar', 'v3', credentials=creds)
            
            # Get events from now to days_ahead
            now = datetime.now(timezone.utc).isoformat()
            future = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=future,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            calendar_events = []
            
            for event in events:
                calendar_event = self._process_calendar_event(event, user, db)
                if calendar_event:
                    calendar_events.append(calendar_event)
            
            return calendar_events
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []
    
    def _process_calendar_event(self, event: Dict, user: User, db: Session) -> Optional[CalendarEvent]:
        """Process a single calendar event"""
        try:
            event_id = event['id']
            
            # Check if event already exists
            existing_event = db.query(CalendarEvent).filter(
                CalendarEvent.google_event_id == event_id
            ).first()
            
            if existing_event:
                return existing_event
            
            # Extract event data
            title = event.get('summary', 'Untitled Event')
            description = event.get('description', '')
            location = event.get('location', '')
            
            # Parse start and end times
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Handle all-day events
            is_all_day = 'date' in event['start']
            
            if is_all_day:
                start_datetime = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
                end_datetime = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
            else:
                start_datetime = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_datetime = datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            # Extract attendees
            attendees = []
            if 'attendees' in event:
                for attendee in event['attendees']:
                    attendees.append({
                        'email': attendee.get('email', ''),
                        'name': attendee.get('displayName', ''),
                        'status': attendee.get('responseStatus', 'needsAction')
                    })
            
            # Extract organizer
            organizer_email = event.get('organizer', {}).get('email', '')
            
            # Extract meeting link
            meeting_link = ''
            meeting_platform = ''
            if 'conferenceData' in event:
                for entry_point in event['conferenceData'].get('entryPoints', []):
                    if entry_point.get('entryPointType') == 'video':
                        meeting_link = entry_point.get('uri', '')
                        meeting_platform = 'google_meet'
                        break
            
            # Create calendar event
            calendar_event = CalendarEvent(
                user_id=user.id,
                google_event_id=event_id,
                calendar_id='primary',
                title=title,
                description=description,
                location=location,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                is_all_day=is_all_day,
                organizer_email=organizer_email,
                attendees=json.dumps(attendees),
                meeting_link=meeting_link,
                meeting_platform=meeting_platform
            )
            
            # AI processing
            self._process_with_ai(calendar_event)
            
            db.add(calendar_event)
            db.commit()
            db.refresh(calendar_event)
            
            return calendar_event
        except Exception as e:
            logger.error(f"Error processing calendar event: {e}")
            return None
    
    def _process_with_ai(self, calendar_event: CalendarEvent):
        """Process calendar event with AI"""
        try:
            # Generate AI summary
            event_text = f"{calendar_event.title} {calendar_event.description}"
            calendar_event.ai_summary = self.ai_service.summarize_email(
                calendar_event.title,
                calendar_event.description or "Meeting scheduled"
            )
            
            # Generate preparation notes
            if calendar_event.description:
                calendar_event.ai_preparation_notes = self._generate_preparation_notes(calendar_event)
        except Exception as e:
            logger.error(f"Error in AI processing for calendar event: {e}")
    
    def _generate_preparation_notes(self, calendar_event: CalendarEvent) -> str:
        """Generate AI preparation notes for meeting"""
        try:
            prompt = f"""
            Based on this meeting information, provide brief preparation notes:
            
            Title: {calendar_event.title}
            Description: {calendar_event.description}
            Duration: {(calendar_event.end_datetime - calendar_event.start_datetime).total_seconds() / 3600:.1f} hours
            Location: {calendar_event.location}
            
            Provide 2-3 bullet points for meeting preparation.
            """
            
            response = self.ai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate concise meeting preparation notes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating preparation notes: {e}")
            return "Review meeting agenda and prepare relevant materials."
    
    def get_upcoming_events(self, user_id: int, hours_ahead: int = 24, db: Session = None) -> List[CalendarEvent]:
        """Get upcoming events within specified hours"""
        now = datetime.now(timezone.utc)
        future = now + timedelta(hours=hours_ahead)
        
        return db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_datetime >= now,
            CalendarEvent.start_datetime <= future
        ).order_by(CalendarEvent.start_datetime).all()
    
    def get_events_needing_reminders(self, db: Session) -> List[CalendarEvent]:
        """Get events that need reminders to be sent"""
        now = datetime.now(timezone.utc)
        
        return db.query(CalendarEvent).filter(
            CalendarEvent.reminder_sent == False,
            CalendarEvent.start_datetime > now,
            CalendarEvent.start_datetime <= now + timedelta(minutes=CalendarEvent.reminder_minutes_before)
        ).all()
    
    def mark_reminder_sent(self, calendar_event: CalendarEvent, db: Session):
        """Mark reminder as sent"""
        calendar_event.reminder_sent = True
        db.commit()