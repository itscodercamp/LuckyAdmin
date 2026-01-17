from flask import Blueprint, request, jsonify
from models import db, Reward, RedemptionRequest, User, Transaction

rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/list', methods=['GET'])
def list_rewards():
    rewards = Reward.query.all()
    base_url = request.host_url.rstrip('/')
    return jsonify([{
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "points_required": r.points_required,
        "points": r.points_required, # Alias for frontend compatibility
        "image_url": f"{base_url}{r.image_url}" if r.image_url and not r.image_url.startswith('http') else r.image_url,
        "stock": r.stock
    } for r in rewards]), 200

@rewards_bp.route('/redeem', methods=['POST'])
def redeem():
    data = request.json
    reward_id = data.get('reward_id')
    user_id = data.get('user_id')

    user = User.query.get(user_id)
    reward = Reward.query.get(reward_id)

    if not user or not reward:
        return jsonify({"message": "User or Reward not found"}), 404

    if user.points < reward.points_required:
        return jsonify({"message": "Insufficient points"}), 400

    if reward.stock <= 0:
        return jsonify({"message": "Reward out of stock"}), 400

    # Deduct points and stock
    user.points -= reward.points_required
    reward.stock -= 1

    # Record Redemption Request
    request_obj = RedemptionRequest(
        user_id=user.id,
        reward_id=reward.id,
        status='pending'
    )

    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        amount=-reward.points_required,
        type='spend',
        description=f"Redeemed reward: {reward.name}"
    )

    db.session.add(request_obj)
    db.session.add(transaction)
    
    # Create Admin Notification
    from models import Notification
    admin_alert = Notification(
        title="New Redemption Request",
        message=f"Customer {user.name} has requested: {reward.name} ({reward.points_required} pts).",
        is_admin_alert=True
    )
    db.session.add(admin_alert)
    
    db.session.commit()

    return jsonify({"message": "Redemption request submitted", "new_balance": user.points}), 200

@rewards_bp.route('/redemption-history', methods=['GET'])
@rewards_bp.route('/history', methods=['GET'])
def redemption_history():
    user_id = request.args.get('user_id')
    redemptions = RedemptionRequest.query.filter_by(user_id=user_id).order_by(RedemptionRequest.created_at.desc()).all()
    
    return jsonify([{
        "id": r.id,
        "reward_name": r.reward.name,
        "status": r.status,
        "date": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for r in redemptions]), 200
