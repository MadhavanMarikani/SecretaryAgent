import openai
import os
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def summarize_email(self, subject: str, body: str) -> str:
        """Generate a concise summary of an email"""
        try:
            prompt = f"""
            Please provide a concise summary of this email in 1-2 sentences:
            
            Subject: {subject}
            Body: {body[:1000]}...
            
            Focus on the key points and any required actions.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that summarizes emails concisely and professionally."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error summarizing email: {e}")
            return f"Email from {subject}: {body[:100]}..."
    
    def generate_reply_draft(self, subject: str, body: str, tone: str = "professional", language: str = "en") -> str:
        """Generate a suggested reply draft"""
        try:
            tone_instructions = {
                "professional": "formal and professional",
                "friendly": "warm and friendly but professional",
                "casual": "casual and approachable",
                "formal": "very formal and respectful"
            }
            
            prompt = f"""
            Generate a {tone_instructions.get(tone, 'professional')} reply to this email:
            
            Subject: {subject}
            Original Message: {body[:800]}...
            
            The reply should:
            - Acknowledge the sender's message
            - Address key points raised
            - Be appropriate in tone
            - Include a clear call to action if needed
            - Be concise (2-3 paragraphs maximum)
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an AI assistant that drafts email replies in {language}. Be helpful and {tone}."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating reply draft: {e}")
            return "Thank you for your email. I will review it and get back to you soon."
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze the sentiment of email content"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the following text. Respond with only one word: positive, negative, or neutral."},
                    {"role": "user", "content": text[:500]}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            return sentiment if sentiment in ["positive", "negative", "neutral"] else "neutral"
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return "neutral"
    
    def detect_emergency_content(self, subject: str, body: str) -> bool:
        """Use AI to detect if email content indicates an emergency"""
        try:
            prompt = f"""
            Analyze this email to determine if it indicates an emergency, urgent situation, or critical issue:
            
            Subject: {subject}
            Body: {body[:500]}...
            
            Respond with only "true" or "false".
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI that detects emergency situations in emails. Look for urgent language, time-sensitive issues, critical problems, or emergency requests."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().lower()
            return result == "true"
        except Exception as e:
            logger.error(f"Error detecting emergency content: {e}")
            return False
    
    def generate_morning_briefing(self, emails: List[Dict], calendar_events: List[Dict]) -> str:
        """Generate a morning briefing summary"""
        try:
            email_summaries = []
            for email in emails[:10]:  # Limit to 10 most recent
                email_summaries.append(f"- From {email['sender_name']}: {email['summary']}")
            
            event_summaries = []
            for event in calendar_events[:5]:  # Limit to 5 upcoming events
                event_summaries.append(f"- {event['title']} at {event['start_time']}")
            
            prompt = f"""
            Create a concise morning briefing based on this information:
            
            Recent Important Emails:
            {chr(10).join(email_summaries) if email_summaries else "No important emails"}
            
            Upcoming Calendar Events:
            {chr(10).join(event_summaries) if event_summaries else "No upcoming events"}
            
            Format as a professional daily briefing with:
            1. Good morning greeting
            2. Email summary section
            3. Calendar highlights section
            4. Any recommended actions
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant creating daily briefings. Be concise, professional, and helpful."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating morning briefing: {e}")
            return "Good morning! Your briefing is being prepared. Please check back shortly."
    
    def extract_meeting_info(self, email_body: str) -> Dict:
        """Extract meeting information from email content"""
        try:
            prompt = f"""
            Extract meeting information from this email and return as JSON:
            
            {email_body[:800]}
            
            Return JSON with these fields (use null if not found):
            - date: meeting date (YYYY-MM-DD format)
            - time: meeting time
            - duration: estimated duration
            - location: meeting location or platform
            - attendees: list of attendees
            - topic: main topic/subject
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract meeting information and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error extracting meeting info: {e}")
            return {}
    
    def categorize_email(self, subject: str, body: str) -> str:
        """Categorize email content"""
        try:
            prompt = f"""
            Categorize this email into one of these categories:
            - meeting
            - project
            - urgent
            - information
            - request
            - social
            - newsletter
            - other
            
            Subject: {subject}
            Body: {body[:300]}...
            
            Respond with only the category name.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Categorize emails based on their content and purpose."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            category = response.choices[0].message.content.strip().lower()
            valid_categories = ["meeting", "project", "urgent", "information", "request", "social", "newsletter", "other"]
            return category if category in valid_categories else "other"
        except Exception as e:
            logger.error(f"Error categorizing email: {e}")
            return "other"