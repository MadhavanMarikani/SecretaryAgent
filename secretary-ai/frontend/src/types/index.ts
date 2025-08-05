export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface Email {
  id: number;
  sender_email: string;
  sender_name: string;
  subject: string;
  body: string;
  summary: string;
  ai_suggested_reply: string;
  sentiment: string;
  status: 'unread' | 'read' | 'archived' | 'important' | 'emergency';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  is_emergency: boolean;
  is_from_vip: boolean;
  received_at: string;
}

export interface CalendarEvent {
  id: number;
  title: string;
  description: string;
  location: string;
  start_datetime: string;
  end_datetime: string;
  is_all_day: boolean;
  organizer_email: string;
  meeting_link: string;
  meeting_platform: string;
  ai_summary: string;
  ai_preparation_notes: string;
  status: string;
}

export interface Alert {
  id: number;
  title: string;
  message: string;
  alert_type: 'email_vip' | 'email_emergency' | 'meeting_reminder' | 'morning_briefing' | 'system';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: 'pending' | 'sent' | 'read' | 'dismissed';
  metadata?: string;
  created_at: string;
  sent_at?: string;
  read_at?: string;
}

export interface EmailStats {
  total_emails: number;
  unread_emails: number;
  urgent_emails: number;
  vip_emails: number;
}

export interface CalendarStats {
  total_events: number;
  upcoming_24h: number;
  events_with_meetings: number;
  calendar_connected: boolean;
}

export interface AlertStats {
  total_alerts: number;
  unread_alerts: number;
  urgent_alerts: number;
  email_alerts: number;
  meeting_alerts: number;
}

export interface MorningBriefing {
  briefing: string;
  email_count: number;
  event_count: number;
  generated_at: string;
}

export interface EmailInsights {
  period_days: number;
  total_emails: number;
  emergency_emails: number;
  vip_emails: number;
  unread_emails: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  top_senders: Array<{
    email: string;
    count: number;
  }>;
  average_per_day: number;
}