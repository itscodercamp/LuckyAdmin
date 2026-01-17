from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth
import uuid
import random

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])

@router.post("/vouchers/generate", response_model=list[schemas.VoucherResponse])
def generate_vouchers(config: schemas.QRGenConfig, db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    vouchers = []
    
    # Calculate counts
    count_low = int(config.total_count * config.min_points_percentage / 100)
    count_high = config.total_count - count_low
    
    # Generate low value vouchers
    for _ in range(count_low):
        new_voucher = models.Voucher(
            uuid=str(uuid.uuid4()),
            points=config.min_points,
            lot_id=config.lot_name
        )
        db.add(new_voucher)
        vouchers.append(new_voucher)
        
    # Generate high value vouchers
    for _ in range(count_high):
        new_voucher = models.Voucher(
            uuid=str(uuid.uuid4()),
            points=config.max_points,
            lot_id=config.lot_name
        )
        db.add(new_voucher)
        vouchers.append(new_voucher)
        
    db.commit()
    for v in vouchers:
        db.refresh(v)
        
    return vouchers

@router.get("/vouchers/lots")
def list_lots(db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    lots = db.query(models.Voucher.lot_id).distinct().all()
    return [lot[0] for lot in lots]

@router.get("/vouchers/lot/{lot_id}", response_model=list[schemas.VoucherResponse])
def get_vouchers_by_lot(lot_id: str, db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    return db.query(models.Voucher).filter(models.Voucher.lot_id == lot_id).all()

@router.post("/products/add", response_model=schemas.ProductResponse)
def add_product(product: schemas.ProductResponse, db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    # This schema might need to be different for creation (id is auto)
    new_product = models.Product(
        name=product.name,
        description=product.description,
        points_required=product.points_required,
        image_url=product.image_url,
        category=product.category,
        is_active=product.is_active
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/stats")
def get_stats(db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    total_users = db.query(models.User).count()
    total_vouchers = db.query(models.Voucher).count()
    used_vouchers = db.query(models.Voucher).filter(models.Voucher.is_used == True).count()
    total_points_distributed = db.query(models.Transaction).filter(models.Transaction.type == "credit").with_entities(models.func.sum(models.Transaction.amount)).scalar() or 0
    total_point_redeemed = db.query(models.Transaction).filter(models.Transaction.type == "debit").with_entities(models.func.sum(models.Transaction.amount)).scalar() or 0
    
    return {
        "total_users": total_users,
        "total_vouchers": total_vouchers,
        "used_vouchers": used_vouchers,
        "total_points_distributed": total_points_distributed,
        "total_point_redeemed": total_point_redeemed,
        "wallet_liability": total_points_distributed - total_point_redeemed
    }

@router.get("/users", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    return db.query(models.User).all()

@router.patch("/users/{user_id}/status")
def toggle_user_status(user_id: int, is_active: bool, db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    return {"message": f"User status updated to {'active' if is_active else 'inactive'}"}

@router.get("/orders")
def list_orders(db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    orders = db.query(models.Order).all()
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "status": order.status,
            "created_at": order.created_at,
            "user": {
                "id": order.user.id,
                "name": order.user.name,
                "phone": order.user.phone
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "points_required": order.product.points_required
            }
        })
    return result

@router.patch("/orders/{order_id}")
def update_order_status(order_id: int, status: str, db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return {"message": "Order status updated"}

@router.get("/transactions")
def list_all_transactions(db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    transactions = db.query(models.Transaction).all()
    result = []
    for tx in transactions:
        result.append({
            "id": tx.id,
            "type": tx.type,
            "amount": tx.amount,
            "description": tx.description,
            "timestamp": tx.timestamp,
            "user": {
                "id": tx.user.id,
                "name": tx.user.name,
                "phone": tx.user.phone
            }
        })
    return result

@router.post("/banners/add", response_model=schemas.BannerResponse)
def add_banner(banner: schemas.BannerResponse, db: Session = Depends(database.get_db), current_admin: models.User = Depends(auth.get_current_admin_user)):
    new_banner = models.Banner(
        title=banner.title,
        image_url=banner.image_url,
        expiry_date=banner.expiry_date,
        active_status=banner.active_status
    )
    db.add(new_banner)
    db.commit()
    db.refresh(new_banner)
    return new_banner
