from flask import Blueprint, request, jsonify
from models import db, Notification, Banner

content_bp = Blueprint('content', __name__)

@content_bp.route('/support/contact', methods=['POST'])
def contact_support():
    data = request.json
    subject = data.get('subject')
    message = data.get('message')
    user_id = data.get('user_id')
    
    # Store support request logic here
    return jsonify({"message": "Support message sent"}), 200

@content_bp.route('/notifications', methods=['GET'])
def notifications():
    user_id = request.args.get('user_id')
    notes = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "date": n.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for n in notes]), 200

@content_bp.route('/notifications/<int:id>/read', methods=['PATCH'])
def mark_read(id):
    note = Notification.query.get(id)
    if note:
        note.is_read = True
        db.session.commit()
    return jsonify({"message": "Notification marked as read"}), 200

@content_bp.route('/banners', methods=['GET'])
def get_banners():
    banners = Banner.query.filter_by(active=True).all()
    return jsonify([{
        "image_url": b.image_url,
        "link": b.link
    } for b in banners]), 200
