import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const AlertsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Alerts & Notifications
      </Typography>
      <Card>
        <CardContent>
          <Typography>
            View and manage all your alerts including VIP email notifications, emergency alerts, meeting reminders, and morning briefings.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AlertsPage;