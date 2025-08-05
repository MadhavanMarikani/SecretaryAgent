# Secretary AI Agent

A comprehensive AI-powered secretary that helps manage emails, calendar, and daily tasks with intelligent automation and notifications.

## 🚀 Features

### Core Features
- 📧 **Email Alerts for Specific Senders**: Monitor and alert for emails from important contacts
- 🚨 **Emergency Email Alerts**: Detect and prioritize urgent emails automatically using AI
- ✍️ **Automatic Reply Draft Generator**: AI-powered email response suggestions with customizable tone
- 📅 **Meeting Reminders**: Google Calendar integration with smart notifications
- 📝 **Email Summary**: Intelligent email summarization and sentiment analysis
- 🌅 **Morning Briefing**: Daily summary of important emails and calendar events

### AI-Powered Intelligence
- **Smart Email Classification**: Automatically categorize emails by type and priority
- **Emergency Detection**: AI analyzes content to identify urgent situations
- **Sentiment Analysis**: Understand the tone of incoming emails
- **Meeting Preparation**: AI-generated preparation notes for upcoming meetings
- **Personalized Briefings**: Customized daily summaries based on your priorities

## 🏗️ Tech Stack

- **Frontend**: React with TypeScript, Material-UI
- **Backend**: Python with FastAPI
- **AI**: OpenAI GPT integration for intelligent features
- **Email**: IMAP/SMTP integration (Gmail, Outlook, etc.)
- **Calendar**: Google Calendar API integration
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT-based authentication
- **Background Tasks**: Celery with Redis

## 📁 Project Structure

```
secretary-ai/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # Database models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   ├── package.json        # Node.js dependencies
│   └── public/             # Static assets
├── .env.example            # Environment variables template
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key
- Google Cloud Project (for Calendar integration)
- Email account with app password (for Gmail)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `EMAIL_USER`: Your email address
   - `EMAIL_PASSWORD`: Your email app password
   - `GOOGLE_CLIENT_ID`: Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
   - Update other settings as needed

5. **Start the backend server**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Email Setup

1. **Gmail Configuration**:
   - Enable 2-factor authentication
   - Generate an app password
   - Use the app password in `EMAIL_PASSWORD`

2. **VIP Senders**: Configure in user settings or environment variables
3. **Emergency Keywords**: Customize keywords that trigger urgent alerts

### Google Calendar Integration

1. **Create Google Cloud Project**:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Calendar API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs

2. **Configure OAuth**:
   - Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
   - Set redirect URI to `http://localhost:8000/auth/callback`

### AI Configuration

1. **OpenAI Setup**:
   - Get API key from OpenAI
   - Configure in `OPENAI_API_KEY`
   - Choose model preferences (GPT-3.5-turbo by default)

## 📖 Usage

### Getting Started

1. **Register an Account**:
   - Navigate to `http://localhost:3000/register`
   - Create your account with email and password

2. **Configure Email**:
   - Go to Settings
   - Add your email credentials
   - Configure VIP senders and emergency keywords

3. **Connect Calendar**:
   - Go to Calendar section
   - Click "Connect Google Calendar"
   - Authorize the application

4. **Start Using**:
   - Dashboard shows overview of emails, events, and alerts
   - Background tasks automatically sync emails and calendar
   - AI processes emails for summaries and alerts

### Key Features Usage

#### Email Management
- **View Emails**: Browse all emails with filtering options
- **AI Summaries**: Get instant summaries of email content
- **Smart Replies**: Generate AI-powered reply drafts
- **Priority Detection**: Automatic prioritization of important emails

#### Calendar Integration
- **Event Sync**: Automatic synchronization with Google Calendar
- **Meeting Reminders**: Get notified before meetings
- **AI Preparation**: Receive AI-generated meeting preparation notes

#### Alerts & Notifications
- **VIP Alerts**: Instant notifications for important senders
- **Emergency Alerts**: Urgent notifications for critical emails
- **Morning Briefings**: Daily summary of important items

## 🔄 Background Tasks

The system runs several background tasks:

- **Email Sync**: Checks for new emails every 5 minutes
- **Calendar Sync**: Updates calendar events every 10 minutes
- **Meeting Reminders**: Sends reminders 15 minutes before meetings
- **Morning Briefings**: Generates daily briefings at 8:00 AM
- **Alert Processing**: Processes pending alerts every 30 seconds

## 🛡️ Security

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **Environment Variables**: Sensitive data stored in environment variables
- **CORS Protection**: Configured for specific origins
- **SQL Injection Protection**: SQLAlchemy ORM provides protection

## 🚀 Deployment

### Production Deployment

1. **Database**: Switch from SQLite to PostgreSQL
2. **Environment**: Update environment variables for production
3. **SSL**: Configure HTTPS for both frontend and backend
4. **Process Manager**: Use gunicorn for Python backend
5. **Reverse Proxy**: Use nginx for serving static files
6. **Background Tasks**: Deploy Celery workers with Redis

### Docker Deployment (Optional)

Create `docker-compose.yml` for containerized deployment:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/secretary
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=secretary
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

## 🔍 API Documentation

The API documentation is available at `http://localhost:8000/docs` when the backend is running.

### Key Endpoints

- **Authentication**: `/auth/login`, `/auth/register`
- **Emails**: `/emails/`, `/emails/sync`, `/emails/reply-draft`
- **Calendar**: `/calendar/events`, `/calendar/sync`
- **Alerts**: `/alerts/`, `/alerts/unread`
- **AI Features**: `/ai/morning-briefing`, `/ai/summarize-email`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Slack integration
- [ ] Advanced AI models
- [ ] Multi-language support
- [ ] Team collaboration features
- [ ] Advanced analytics and insights