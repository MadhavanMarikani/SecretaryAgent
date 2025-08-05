import api from '../config/api';
import { Email, EmailStats } from '../types';

export interface EmailFilters {
  status?: string;
  priority?: string;
  limit?: number;
  offset?: number;
}

export interface SendEmailData {
  to_email: string;
  subject: string;
  body: string;
  body_html?: string;
}

export interface EmailConfigData {
  email_user?: string;
  email_password?: string;
  imap_server?: string;
  smtp_server?: string;
  smtp_port?: number;
  vip_senders?: string[];
  emergency_keywords?: string[];
}

class EmailService {
  async getEmails(filters: EmailFilters = {}): Promise<Email[]> {
    const response = await api.get('/emails/', { params: filters });
    return response.data;
  }

  async getEmail(id: number): Promise<Email> {
    const response = await api.get(`/emails/${id}`);
    return response.data;
  }

  async updateEmailStatus(id: number, status: string): Promise<void> {
    await api.put(`/emails/${id}/status`, null, { params: { status } });
  }

  async syncEmails(): Promise<{ message: string; count: number }> {
    const response = await api.post('/emails/sync');
    return response.data;
  }

  async generateReplyDraft(emailId: number, tone: string = 'professional'): Promise<string> {
    const response = await api.post('/emails/reply-draft', {
      email_id: emailId,
      tone
    });
    return response.data.reply_draft;
  }

  async sendEmail(data: SendEmailData): Promise<void> {
    await api.post('/emails/send', data);
  }

  async getEmailStats(): Promise<EmailStats> {
    const response = await api.get('/emails/stats/summary');
    return response.data;
  }

  async updateEmailConfig(config: EmailConfigData): Promise<void> {
    await api.put('/emails/config', config);
  }
}

export default new EmailService();