import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const CalendarPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Calendar
      </Typography>
      <Card>
        <CardContent>
          <Typography>
            Calendar integration with Google Calendar events, meeting reminders, and AI-powered preparation notes.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CalendarPage;