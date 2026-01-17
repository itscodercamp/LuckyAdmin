from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier') # email or phone
    password = data.get('password')

    user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

    if user and check_password_hash(user.password_hash, password):
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "phone": user.phone,
                "email": user.email,
                "points": user.points
            }
        }), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    city = data.get('city')
    state = data.get('state')
    password = data.get('password')

    if User.query.filter((User.phone == phone) | (User.email == email)).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(
        name=name,
        phone=phone,
        email=email,
        city=city,
        state=state,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    
    # Create Admin Notification
    from models import Notification
    admin_alert = Notification(
        title="New User Registered",
        message=f"New customer {name} ({phone}) has joined from {city}, {state}.",
        is_admin_alert=True
    )
    db.session.add(admin_alert)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/profile-image', methods=['POST'])
@auth_bp.route('/profile/upload', methods=['POST'])
def profile_image():
    # user_id should be sent or inferred from token (here we simplify)
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    filename = secure_filename(f"user_{user_id}_{file.filename}")
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

    user.profile_image = file_path
    db.session.commit()
    
    base_url = request.host_url.rstrip('/')
    full_url = f"{base_url}/{file_path}".replace("//", "/")

    return jsonify({"message": "Profile image updated", "path": full_url}), 200

@auth_bp.route('/profile', methods=['GET'])
def profile():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    base_url = request.host_url.rstrip('/')
    # Fix profile image URL
    img_url = user.profile_image
    if img_url and not img_url.startswith('http'):
        img_url = f"{base_url}/{img_url}".replace("//", "/")

    return jsonify({
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "city": user.city,
        "state": user.state,
        "points": user.points,
        "profile_image": img_url
    }), 200
