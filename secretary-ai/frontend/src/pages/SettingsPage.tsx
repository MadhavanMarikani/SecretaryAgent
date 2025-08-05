import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Card>
        <CardContent>
          <Typography>
            Configure your email accounts, calendar integration, VIP senders, emergency keywords, AI preferences, and notification settings.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SettingsPage;