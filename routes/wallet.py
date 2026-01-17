from flask import Blueprint, request, jsonify
from models import db, User, QRCode, Transaction
from datetime import datetime

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/balance', methods=['GET'])
def balance():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"points": user.points}), 200

@wallet_bp.route('/scan', methods=['POST'])
def scan():
    data = request.json
    print(f"DEBUG SCAN: Received data: {data}") # Debugging
    
    uuid_code = data.get('uuid')
    user_id = data.get('user_id')

    if not uuid_code or not user_id:
        print("DEBUG SCAN: Missing uuid or user_id")
        return jsonify({"message": "Missing uuid or user_id"}), 400

    user = User.query.get(user_id)
    if not user:
        print(f"DEBUG SCAN: User {user_id} not found")
        return jsonify({"message": "User not found"}), 404

    qr_code = QRCode.query.filter_by(uuid=uuid_code).first()

    if not qr_code:
        print(f"DEBUG SCAN: Invalid QR Code {uuid_code}")
        return jsonify({"message": "Invalid QR Code"}), 400

    if qr_code.is_redeemed:
        print(f"DEBUG SCAN: QR {uuid_code} already redeemed")
        return jsonify({"message": "QR Code already redeemed"}), 400

    # Redeem and add points
    qr_code.is_redeemed = True
    qr_code.redeemed_by = user.id
    qr_code.redeemed_at = datetime.utcnow()
    
    user.points += qr_code.points

    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        amount=qr_code.points,
        type='earn',
        description=f"Points earned from QR scan (Batch: {qr_code.batch.batch_name})"
    )
    
    db.session.add(transaction)
    
    # Create Admin Notification
    from models import Notification
    admin_alert = Notification(
        title="QR Scanned",
        message=f"Customer {user.name} scanned a QR for {qr_code.points} points (Batch: {qr_code.batch.batch_name}).",
        is_admin_alert=True
    )
    db.session.add(admin_alert)
    
    db.session.commit()

    return jsonify({
        "message": "Scan successful",
        "points_earned": qr_code.points,
        "new_balance": user.points
    }), 200

@wallet_bp.route('/transactions', methods=['GET'])
def transactions():
    user_id = request.args.get('user_id')
    txs = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    
    return jsonify([{
        "id": tx.id,
        "amount": tx.amount,
        "type": tx.type,
        "description": tx.description,
        "date": tx.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for tx in txs]), 200
