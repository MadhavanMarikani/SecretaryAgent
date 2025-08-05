import api from '../config/api';
import { Alert, AlertStats } from '../types';

export interface AlertFilters {
  alert_type?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

class AlertService {
  async getAlerts(filters: AlertFilters = {}): Promise<Alert[]> {
    const response = await api.get('/alerts/', { params: filters });
    return response.data;
  }

  async getUnreadAlerts(): Promise<Alert[]> {
    const response = await api.get('/alerts/unread');
    return response.data;
  }

  async getAlert(id: number): Promise<Alert> {
    const response = await api.get(`/alerts/${id}`);
    return response.data;
  }

  async markAlertAsRead(id: number): Promise<void> {
    await api.put(`/alerts/${id}/read`);
  }

  async dismissAlert(id: number): Promise<void> {
    await api.put(`/alerts/${id}/dismiss`);
  }

  async markAllAlertsAsRead(): Promise<{ message: string }> {
    const response = await api.put('/alerts/mark-all-read');
    return response.data;
  }

  async getAlertStats(): Promise<AlertStats> {
    const response = await api.get('/alerts/stats/summary');
    return response.data;
  }
}

export default new AlertService();