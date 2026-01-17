from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth

router = APIRouter(prefix="/api/rewards", tags=["Rewards"])

@router.get("/list", response_model=list[schemas.ProductResponse])
def list_rewards(db: Session = Depends(database.get_db)):
    return db.query(models.Product).filter(models.Product.is_active == True).all()

@router.post("/redeem")
def redeem_reward(reward_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == reward_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    if current_user.points_balance < product.points_required:
        raise HTTPException(status_code=400, detail="Insufficient points balance")
    
    # Process redemption
    current_user.points_balance -= product.points_required
    
    order = models.Order(
        user_id=current_user.id,
        product_id=product.id,
        status="pending"
    )
    
    transaction = models.Transaction(
        user_id=current_user.id,
        type="debit",
        amount=product.points_required,
        description=f"Redeemed Reward: {product.name}"
    )
    
    notification = models.Notification(
        user_id=current_user.id,
        title="Reward Redeemed!",
        message=f"You have redeemed {product.name}. Your order is being processed."
    )
    
    db.add(order)
    db.add(transaction)
    db.add(notification)
    db.commit()
    
    return {"message": "Reward redeemed successfully", "order_id": order.id, "new_balance": current_user.points_balance}
