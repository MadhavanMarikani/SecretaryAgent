from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from dotenv import load_dotenv

from routers import auth, emails, calendar, ai_assistant, alerts
from services.database import engine, Base
from services.background_tasks import start_background_tasks

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secretary AI",
    description="AI-powered secretary for email and calendar management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(emails.router, prefix="/emails", tags=["Emails"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
app.include_router(ai_assistant.router, prefix="/ai", tags=["AI Assistant"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    start_background_tasks()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Secretary AI is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "email": "configured",
            "ai": "ready"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )