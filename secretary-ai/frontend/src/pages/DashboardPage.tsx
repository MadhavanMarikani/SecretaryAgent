import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
} from '@mui/material';
import {
  Email as EmailIcon,
  Event as EventIcon,
  NotificationImportant as AlertIcon,
  TrendingUp,
  VpnKey,
  Warning,
  Schedule,
  SmartToy,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

import emailService from '../services/emailService';
import calendarService from '../services/calendarService';
import alertService from '../services/alertService';
import aiService from '../services/aiService';
import { EmailStats, CalendarStats, AlertStats, Email, CalendarEvent, MorningBriefing } from '../types';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [emailStats, setEmailStats] = useState<EmailStats | null>(null);
  const [calendarStats, setCalendarStats] = useState<CalendarStats | null>(null);
  const [alertStats, setAlertStats] = useState<AlertStats | null>(null);
  const [recentEmails, setRecentEmails] = useState<Email[]>([]);
  const [upcomingEvents, setUpcomingEvents] = useState<CalendarEvent[]>([]);
  const [morningBriefing, setMorningBriefing] = useState<MorningBriefing | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [
        emailStatsRes,
        calendarStatsRes,
        alertStatsRes,
        recentEmailsRes,
        upcomingEventsRes,
        briefingRes,
      ] = await Promise.allSettled([
        emailService.getEmailStats(),
        calendarService.getCalendarStats(),
        alertService.getAlertStats(),
        emailService.getEmails({ limit: 5, status: 'unread' }),
        calendarService.getUpcomingEvents(24),
        aiService.getMorningBriefing(),
      ]);

      if (emailStatsRes.status === 'fulfilled') setEmailStats(emailStatsRes.value);
      if (calendarStatsRes.status === 'fulfilled') setCalendarStats(calendarStatsRes.value);
      if (alertStatsRes.status === 'fulfilled') setAlertStats(alertStatsRes.value);
      if (recentEmailsRes.status === 'fulfilled') setRecentEmails(recentEmailsRes.value);
      if (upcomingEventsRes.status === 'fulfilled') setUpcomingEvents(upcomingEventsRes.value);
      if (briefingRes.status === 'fulfilled') setMorningBriefing(briefingRes.value);

    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
    onClick?: () => void;
  }> = ({ title, value, icon, color, onClick }) => (
    <Card sx={{ cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 48 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread Emails"
            value={emailStats?.unread_emails || 0}
            icon={<EmailIcon />}
            color="#1976d2"
            onClick={() => navigate('/emails?status=unread')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Urgent Emails"
            value={emailStats?.urgent_emails || 0}
            icon={<Warning />}
            color="#d32f2f"
            onClick={() => navigate('/emails?priority=urgent')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Upcoming Events"
            value={calendarStats?.upcoming_24h || 0}
            icon={<EventIcon />}
            color="#388e3c"
            onClick={() => navigate('/calendar')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Alerts"
            value={alertStats?.unread_alerts || 0}
            icon={<AlertIcon />}
            color="#f57c00"
            onClick={() => navigate('/alerts')}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Morning Briefing */}
        {morningBriefing && (
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SmartToy sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">
                    Morning Briefing
                  </Typography>
                </Box>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line', mb: 2 }}>
                  {morningBriefing.briefing}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip
                    label={`${morningBriefing.email_count} emails`}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={`${morningBriefing.event_count} events`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<EmailIcon />}
                  onClick={() => navigate('/emails')}
                >
                  View All Emails
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<EventIcon />}
                  onClick={() => navigate('/calendar')}
                >
                  Calendar Events
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<TrendingUp />}
                  onClick={() => navigate('/emails')}
                >
                  Email Insights
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<VpnKey />}
                  onClick={() => navigate('/settings')}
                >
                  Settings
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Unread Emails */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Unread Emails
              </Typography>
              {recentEmails.length > 0 ? (
                <List dense>
                  {recentEmails.map((email) => (
                    <React.Fragment key={email.id}>
                      <ListItem button onClick={() => navigate(`/emails`)}>
                        <ListItemIcon>
                          <EmailIcon color={email.is_emergency ? 'error' : email.is_from_vip ? 'warning' : 'primary'} />
                        </ListItemIcon>
                        <ListItemText
                          primary={email.subject}
                          secondary={`From: ${email.sender_name}`}
                        />
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography color="textSecondary" align="center" sx={{ py: 2 }}>
                  No unread emails
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Events */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upcoming Events (24h)
              </Typography>
              {upcomingEvents.length > 0 ? (
                <List dense>
                  {upcomingEvents.map((event) => (
                    <React.Fragment key={event.id}>
                      <ListItem button onClick={() => navigate('/calendar')}>
                        <ListItemIcon>
                          <Schedule color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={event.title}
                          secondary={new Date(event.start_datetime).toLocaleString()}
                        />
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography color="textSecondary" align="center" sx={{ py: 2 }}>
                  No upcoming events
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;