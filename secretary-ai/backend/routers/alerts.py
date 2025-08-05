from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from services.database import get_db
from services.alert_service import AlertService
from models.user import User
from models.alert import Alert, AlertType, AlertPriority, AlertStatus
from routers.auth import get_current_user

router = APIRouter()

class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    alert_type: str
    priority: str
    status: str
    metadata: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    alert_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's alerts with optional filtering"""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if alert_type:
        try:
            alert_type_enum = AlertType(alert_type)
            query = query.filter(Alert.alert_type == alert_type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid alert type")
    
    if status:
        try:
            alert_status = AlertStatus(status)
            query = query.filter(Alert.status == alert_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
    return alerts

@router.get("/unread", response_model=List[AlertResponse])
def get_unread_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread alerts"""
    alert_service = AlertService()
    alerts = alert_service.get_unread_alerts(current_user.id, db)
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert

@router.put("/{alert_id}/read")
def mark_alert_as_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark alert as read"""
    alert_service = AlertService()
    success = alert_service.mark_alert_as_read(alert_id, current_user.id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert marked as read"}

@router.put("/{alert_id}/dismiss")
def dismiss_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss an alert"""
    alert_service = AlertService()
    success = alert_service.dismiss_alert(alert_id, current_user.id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert dismissed"}

@router.put("/mark-all-read")
def mark_all_alerts_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all alerts as read"""
    updated_count = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT])
    ).update({
        Alert.status: AlertStatus.READ,
        Alert.read_at: datetime.utcnow()
    })
    
    db.commit()
    return {"message": f"Marked {updated_count} alerts as read"}

@router.get("/stats/summary")
def get_alert_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert statistics"""
    total_alerts = db.query(Alert).filter(Alert.user_id == current_user.id).count()
    
    unread_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT])
    ).count()
    
    urgent_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.priority == AlertPriority.URGENT,
        Alert.status.in_([AlertStatus.PENDING, AlertStatus.SENT])
    ).count()
    
    email_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.alert_type.in_([AlertType.EMAIL_VIP, AlertType.EMAIL_EMERGENCY])
    ).count()
    
    meeting_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.alert_type == AlertType.MEETING_REMINDER
    ).count()
    
    return {
        "total_alerts": total_alerts,
        "unread_alerts": unread_alerts,
        "urgent_alerts": urgent_alerts,
        "email_alerts": email_alerts,
        "meeting_alerts": meeting_alerts
    }