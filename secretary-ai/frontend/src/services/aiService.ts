import api from '../config/api';
import { MorningBriefing, EmailInsights } from '../types';

export interface SummarizeEmailData {
  subject: string;
  body: string;
}

export interface GenerateReplyData {
  subject: string;
  body: string;
  tone?: string;
  language?: string;
}

export interface EmailSummaryResponse {
  summary: string;
  sentiment: string;
  category: string;
}

class AIService {
  async summarizeEmail(data: SummarizeEmailData): Promise<EmailSummaryResponse> {
    const response = await api.post('/ai/summarize-email', data);
    return response.data;
  }

  async generateReply(data: GenerateReplyData): Promise<string> {
    const response = await api.post('/ai/generate-reply', data);
    return response.data.reply_draft;
  }

  async getMorningBriefing(): Promise<MorningBriefing> {
    const response = await api.get('/ai/morning-briefing');
    return response.data;
  }

  async extractMeetingInfo(emailBody: string): Promise<any> {
    const response = await api.post('/ai/extract-meeting-info', null, {
      params: { email_body: emailBody }
    });
    return response.data.meeting_info;
  }

  async analyzeSentiment(text: string): Promise<string> {
    const response = await api.post('/ai/analyze-sentiment', null, {
      params: { text }
    });
    return response.data.sentiment;
  }

  async categorizeEmail(subject: string, body: string): Promise<string> {
    const response = await api.post('/ai/categorize-email', null, {
      params: { subject, body }
    });
    return response.data.category;
  }

  async detectEmergency(subject: string, body: string): Promise<boolean> {
    const response = await api.post('/ai/detect-emergency', null, {
      params: { subject, body }
    });
    return response.data.is_emergency;
  }

  async getEmailInsights(days: number = 7): Promise<EmailInsights> {
    const response = await api.get('/ai/insights/email-trends', {
      params: { days }
    });
    return response.data;
  }
}

export default new AIService();