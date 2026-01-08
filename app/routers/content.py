from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth

router = APIRouter(prefix="/api/content", tags=["Content & Notifications"])

@router.get("/banners", response_model=list[schemas.BannerResponse])
def get_banners(db: Session = Depends(database.get_db)):
    return db.query(models.Banner).filter(models.Banner.active_status == True).all()

@router.get("/notifications", response_model=list[schemas.NotificationResponse])
def get_notifications(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Notification).filter(models.Notification.user_id == current_user.id).order_by(models.Notification.created_at.desc()).all()

@router.patch("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    notification = db.query(models.Notification).filter(models.Notification.id == notif_id, models.Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.post("/support/contact")
def contact_support(inquiry: schemas.SupportInquiry, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_inquiry = models.Inquiry(
        user_id=current_user.id,
        subject=inquiry.subject,
        message=inquiry.message
    )
    db.add(new_inquiry)
    db.commit()
    return {"message": "Your inquiry has been submitted"}

@router.get("/profile", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/profile", response_model=schemas.UserResponse)
def update_profile(user_update: schemas.UserBase, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    current_user.name = user_update.name
    current_user.city = user_update.city
    current_user.state = user_update.state
    current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)
    return current_user
