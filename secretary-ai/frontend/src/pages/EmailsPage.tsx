import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Paper,
  Alert,
  CircularProgress,
  Fab,
  Divider,
} from '@mui/material';
import {
  Email as EmailIcon,
  Refresh,
  Reply,
  Settings,
  Add,
  Warning,
  Star,
  Schedule,
} from '@mui/icons-material';

import emailService from '../services/emailService';
import { Email, EmailStats } from '../types';

const EmailsPage: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [stats, setStats] = useState<EmailStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [replyDialogOpen, setReplyDialogOpen] = useState(false);
  const [replyDraft, setReplyDraft] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadEmails();
    loadStats();
  }, [statusFilter, priorityFilter]);

  const loadEmails = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (statusFilter) filters.status = statusFilter;
      if (priorityFilter) filters.priority = priorityFilter;
      
      const emailData = await emailService.getEmails(filters);
      setEmails(emailData);
    } catch (err) {
      setError('Failed to load emails');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await emailService.getEmailStats();
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load stats');
    }
  };

  const handleSync = async () => {
    try {
      await emailService.syncEmails();
      loadEmails();
      loadStats();
    } catch (err) {
      setError('Failed to sync emails');
    }
  };

  const handleEmailClick = (email: Email) => {
    setSelectedEmail(email);
  };

  const handleGenerateReply = async () => {
    if (!selectedEmail) return;
    
    try {
      const draft = await emailService.generateReplyDraft(selectedEmail.id);
      setReplyDraft(draft);
      setReplyDialogOpen(true);
    } catch (err) {
      setError('Failed to generate reply');
    }
  };

  const handleStatusChange = async (email: Email, newStatus: string) => {
    try {
      await emailService.updateEmailStatus(email.id, newStatus);
      loadEmails();
      loadStats();
    } catch (err) {
      setError('Failed to update email status');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'emergency': return 'error';
      case 'important': return 'warning';
      case 'unread': return 'primary';
      default: return 'default';
    }
  };

  const getPriorityIcon = (priority: string, isFromVip: boolean, isEmergency: boolean) => {
    if (isEmergency) return <Warning color="error" />;
    if (isFromVip) return <Star color="warning" />;
    if (priority === 'urgent') return <Warning color="error" />;
    return <EmailIcon color="primary" />;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Emails
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, ml: 'auto' }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleSync}
          >
            Sync
          </Button>
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={() => {/* Navigate to email settings */}}
          >
            Settings
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Stats */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6">{stats.total_emails}</Typography>
              <Typography variant="body2">Total</Typography>
            </Paper>
          </Grid>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6">{stats.unread_emails}</Typography>
              <Typography variant="body2">Unread</Typography>
            </Paper>
          </Grid>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6">{stats.urgent_emails}</Typography>
              <Typography variant="body2">Urgent</Typography>
            </Paper>
          </Grid>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6">{stats.vip_emails}</Typography>
              <Typography variant="body2">VIP</Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            label="Status"
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="unread">Unread</MenuItem>
            <MenuItem value="read">Read</MenuItem>
            <MenuItem value="important">Important</MenuItem>
            <MenuItem value="emergency">Emergency</MenuItem>
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Priority</InputLabel>
          <Select
            value={priorityFilter}
            label="Priority"
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="urgent">Urgent</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="normal">Normal</MenuItem>
            <MenuItem value="low">Low</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {/* Email List */}
        <Grid item xs={12} md={selectedEmail ? 8 : 12}>
          <Card>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : emails.length > 0 ? (
              <List>
                {emails.map((email) => (
                  <React.Fragment key={email.id}>
                    <ListItem 
                      button 
                      onClick={() => handleEmailClick(email)}
                      selected={selectedEmail?.id === email.id}
                    >
                      <ListItemIcon>
                        {getPriorityIcon(email.priority, email.is_from_vip, email.is_emergency)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1">
                              {email.subject}
                            </Typography>
                            <Chip
                              label={email.status}
                              size="small"
                              color={getStatusColor(email.status) as any}
                            />
                            {email.is_from_vip && (
                              <Chip label="VIP" size="small" color="warning" />
                            )}
                            {email.is_emergency && (
                              <Chip label="URGENT" size="small" color="error" />
                            )}
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2">
                              From: {email.sender_name} ({email.sender_email})
                            </Typography>
                            {email.summary && (
                              <Typography variant="body2" color="text.secondary">
                                {email.summary}
                              </Typography>
                            )}
                            <Typography variant="caption">
                              {new Date(email.received_at).toLocaleString()}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box p={4} textAlign="center">
                <Typography color="textSecondary">
                  No emails found
                </Typography>
              </Box>
            )}
          </Card>
        </Grid>

        {/* Email Details */}
        {selectedEmail && (
          <Grid item xs={12} md={4}>
            <Card>
              <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Email Details
                </Typography>
                
                <Typography variant="subtitle1" gutterBottom>
                  {selectedEmail.subject}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  From: {selectedEmail.sender_name}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {selectedEmail.sender_email}
                </Typography>
                
                <Box sx={{ my: 2 }}>
                  <Typography variant="body1">
                    {selectedEmail.body}
                  </Typography>
                </Box>
                
                {selectedEmail.summary && (
                  <Box sx={{ my: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      AI Summary:
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedEmail.summary}
                    </Typography>
                  </Box>
                )}
                
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', my: 2 }}>
                  <Chip label={selectedEmail.sentiment} size="small" />
                  <Chip label={selectedEmail.priority} size="small" />
                </Box>
                
                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<Reply />}
                    onClick={handleGenerateReply}
                    fullWidth
                  >
                    AI Reply
                  </Button>
                </Box>
                
                <Box sx={{ mt: 2 }}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={selectedEmail.status}
                      label="Status"
                      onChange={(e) => handleStatusChange(selectedEmail, e.target.value)}
                    >
                      <MenuItem value="unread">Unread</MenuItem>
                      <MenuItem value="read">Read</MenuItem>
                      <MenuItem value="important">Important</MenuItem>
                      <MenuItem value="archived">Archived</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              </Box>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Reply Dialog */}
      <Dialog
        open={replyDialogOpen}
        onClose={() => setReplyDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>AI Generated Reply</DialogTitle>
        <DialogContent>
          <TextField
            multiline
            rows={10}
            fullWidth
            value={replyDraft}
            onChange={(e) => setReplyDraft(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReplyDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained">
            Use Reply
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmailsPage;