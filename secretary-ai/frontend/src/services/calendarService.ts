import api from '../config/api';
import { CalendarEvent, CalendarStats } from '../types';

class CalendarService {
  async getCalendarEvents(daysAhead: number = 7): Promise<CalendarEvent[]> {
    const response = await api.get('/calendar/events', {
      params: { days_ahead: daysAhead }
    });
    return response.data;
  }

  async getCalendarEvent(id: number): Promise<CalendarEvent> {
    const response = await api.get(`/calendar/events/${id}`);
    return response.data;
  }

  async getUpcomingEvents(hoursAhead: number = 24): Promise<CalendarEvent[]> {
    const response = await api.get('/calendar/upcoming', {
      params: { hours_ahead: hoursAhead }
    });
    return response.data;
  }

  async syncCalendarEvents(): Promise<{ message: string; count: number }> {
    const response = await api.post('/calendar/sync');
    return response.data;
  }

  async getCalendarAuthUrl(): Promise<string> {
    const response = await api.get('/calendar/auth/url');
    return response.data.authorization_url;
  }

  async handleAuthCallback(code: string): Promise<void> {
    await api.post('/calendar/auth/callback', null, {
      params: { code }
    });
  }

  async getCalendarStats(): Promise<CalendarStats> {
    const response = await api.get('/calendar/stats/summary');
    return response.data;
  }
}

export default new CalendarService();