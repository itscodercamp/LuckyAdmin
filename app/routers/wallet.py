from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth
from datetime import datetime

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])

@router.get("/balance")
def get_balance(current_user: models.User = Depends(auth.get_current_user)):
    return {"points_balance": current_user.points_balance}

@router.post("/scan")
def scan_voucher(uuid: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    voucher = db.query(models.Voucher).filter(models.Voucher.uuid == uuid).first()
    
    if not voucher:
        raise HTTPException(status_code=404, detail="Invalid Voucher")
    
    if voucher.is_used:
        raise HTTPException(status_code=400, detail="Already Scanned")
    
    # Process scan
    voucher.is_used = True
    voucher.used_by = current_user.id
    voucher.used_at = datetime.utcnow()
    
    current_user.points_balance += voucher.points
    
    # Record transaction
    transaction = models.Transaction(
        user_id=current_user.id,
        type="credit",
        amount=voucher.points,
        description=f"Voucher Scan: {voucher.uuid}"
    )
    
    # Notify user
    notification = models.Notification(
        user_id=current_user.id,
        title="Points Added!",
        message=f"You have received {voucher.points} points from scanning a voucher."
    )
    
    db.add(transaction)
    db.add(notification)
    db.commit()
    
    return {"message": "Points added successfully", "points": voucher.points, "new_balance": current_user.points_balance}

@router.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).order_by(models.Transaction.timestamp.desc()).all()
