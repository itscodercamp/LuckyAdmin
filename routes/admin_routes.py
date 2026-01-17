from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Admin, User, Product, Reward, QRBatch, QRCode, RedemptionRequest, Transaction, Notification, SupportMessage
import qrcode
import os
import uuid
import random
import zipfile
from io import BytesIO
from datetime import datetime

admin_bp = Blueprint('admin_routes', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_routes.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_routes.admin_login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    from models import Order, SupportMessage
    user_count = User.query.count()
    product_count = Product.query.count()
    reward_count = Reward.query.count()
    batch_count = QRBatch.query.count()
    pending_redemptions = RedemptionRequest.query.filter_by(status='pending').count()
    pending_orders = Order.query.filter_by(status='pending').count()
    unread_messages = SupportMessage.query.filter_by(is_read=False).count()
    
    # New: Admin Notifications
    notifications = Notification.query.filter_by(is_admin_alert=True, is_read=False).order_by(Notification.created_at.desc()).all()
    
    # Recent Transactions for dashboard (Scans and Redemptions)
    recent_scans = QRCode.query.filter_by(is_redeemed=True).order_by(QRCode.redeemed_at.desc()).limit(5).all()
    recent_redemptions = RedemptionRequest.query.order_by(RedemptionRequest.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           user_count=user_count, 
                           product_count=product_count, 
                           reward_count=reward_count, 
                           batch_count=batch_count,
                           pending_redemptions=pending_redemptions,
                           pending_orders=pending_orders,
                           unread_messages=unread_messages,
                           notifications=notifications,
                           recent_scans=recent_scans,
                           recent_redemptions=recent_redemptions)

@admin_bp.route('/notification/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.is_read = True
    db.session.commit()
    return jsonify({"success": True})

@admin_bp.route('/goodies', methods=['GET', 'POST'])
@login_required
def goodies_admin():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        points = int(request.form.get('points_required'))
        stock = int(request.form.get('stock'))
        
        # Handle Reward Image
        image_url = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename != '':
                from werkzeug.utils import secure_filename
                filename = secure_filename(f"reward_{int(datetime.now().timestamp())}_{file.filename}")
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
                image_url = f"/uploads/{filename}"
        
        new_reward = Reward(
            name=name,
            description=description,
            points_required=points,
            stock=stock,
            image_url=image_url
        )
        db.session.add(new_reward)
        db.session.commit()
        flash('New Goodie added successfully!')
        return redirect(url_for('admin_routes.goodies_admin'))
        
    rewards = Reward.query.all()
    return render_template('goodies_admin.html', rewards=rewards)

@admin_bp.route('/goodies/<int:reward_id>/delete', methods=['POST'])
@login_required
def delete_goodie(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    db.session.delete(reward)
    db.session.commit()
    flash(f"Goodie '{reward.name}' removed.")
    return redirect(url_for('admin_routes.goodies_admin'))

@admin_bp.route('/goodies/<int:reward_id>/edit', methods=['POST'])
@login_required
def edit_goodie(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    
    reward.name = request.form.get('name')
    reward.description = request.form.get('description')
    reward.points_required = int(request.form.get('points_required'))
    reward.stock = int(request.form.get('stock'))
    
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename != '':
            from werkzeug.utils import secure_filename
            filename = secure_filename(f"reward_{int(datetime.now().timestamp())}_{file.filename}")
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            reward.image_url = f"/uploads/{filename}"
            
    db.session.commit()
    flash('Goodie updated successfully!')
    return redirect(url_for('admin_routes.goodies_admin'))

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products_admin():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        
        # Category Logic: Prefer new_category if provided
        category = request.form.get('new_category')
        if not category or category.strip() == '':
            category = request.form.get('category')
        
        # Handle file upload
        image_url = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename != '':
                from werkzeug.utils import secure_filename
                filename = secure_filename(f"prod_{int(datetime.now().timestamp())}_{file.filename}")
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
                image_url = f"/uploads/{filename}"
        
        # Fallback to text URL if no file uploaded
        if not image_url:
            image_url = request.form.get('image_url')
        
        new_product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            image_url=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('admin_routes.products_admin'))
        
    products = Product.query.all()
    return render_template('products_admin.html', products=products)

@admin_bp.route('/product/<int:product_id>')
@login_required
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_view.html', product=product)

@admin_bp.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f"Product '{product.name}' deleted successfully.")
    return redirect(url_for('admin_routes.products_admin'))

@admin_bp.route('/users')
@login_required
def users_list():
    query = User.query
    
    # Filtering
    name = request.args.get('name')
    phone = request.args.get('phone')
    city = request.args.get('city')
    state = request.args.get('state')
    
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if phone:
        query = query.filter(User.phone.ilike(f"%{phone}%"))
    if city:
        query = query.filter(User.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(User.state.ilike(f"%{state}%"))
        
    users = query.all()
    return render_template('users.html', users=users)

@admin_bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    # Fetch related data
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    redemptions = RedemptionRequest.query.filter_by(user_id=user_id).order_by(RedemptionRequest.created_at.desc()).all()
    
    # Notifications/Messages (using Notification model if exists)
    messages = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    return render_template('user_profile.html', 
                           user=user, 
                           transactions=transactions, 
                           redemptions=redemptions,
                           messages=messages)

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Delete related records (cleanup)
    Transaction.query.filter_by(user_id=user_id).delete()
    RedemptionRequest.query.filter_by(user_id=user_id).delete()
    Notification.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User '{user.name}' and all associated data deleted successfully.")
    return redirect(url_for('admin_routes.users_list'))

@admin_bp.route('/qr-management', methods=['GET', 'POST'])
@login_required
def qr_management():
    if request.method == 'POST':
        batch_name = request.form.get('batch_name')
        qr_size = int(request.form.get('qr_size')) # e.g. 100
        
        # Batch generation logic
        new_batch = QRBatch(batch_name=batch_name, total_qrs=qr_size, total_points=0)
        db.session.add(new_batch)
        db.session.flush() # Get batch ID

        total_batch_points = 0
        
        # 50% (10-30 points)
        count_50 = int(qr_size * 0.5)
        # 40% (31-50 points)
        count_40 = int(qr_size * 0.4)
        # 10% (51-80 points)
        count_10 = qr_size - count_50 - count_40
        
        distributions = [
            (count_50, 10, 30),
            (count_40, 31, 50),
            (count_10, 51, 80)
        ]

        for count, min_p, max_p in distributions:
            for _ in range(count):
                pts = random.randint(min_p, max_p)
                qr = QRCode(batch_id=new_batch.id, points=pts, uuid=str(uuid.uuid4()))
                db.session.add(qr)
                total_batch_points += pts
        
        new_batch.total_points = total_batch_points
        db.session.commit()
        flash('QR Batch generated successfully')
        return redirect(url_for('admin_routes.qr_management'))

    batches = QRBatch.query.order_by(QRBatch.created_at.desc()).all()
    # Add stats to each batch object for display
    for b in batches:
        b.redeemed_count = QRCode.query.filter_by(batch_id=b.id, is_redeemed=True).count()
        b.available_count = b.total_qrs - b.redeemed_count
    return render_template('qr_management.html', batches=batches)

@admin_bp.route('/qr-batch/<int:batch_id>/download')
@login_required
def download_qr_zip(batch_id):
    batch = QRBatch.query.get_or_404(batch_id)
    qrs = QRCode.query.filter_by(batch_id=batch_id).all()
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for qr in qrs:
            # Generate QR Image
            img = qrcode.make(qr.uuid)
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            zf.writestr(f"qr_{qr.id}_{qr.points}pts.png", img_io.getvalue())
            
    memory_file.seek(0)
    return send_file(memory_file, download_name=f"batch_{batch.batch_name}.zip", as_attachment=True)

@admin_bp.route('/qr-batch/<int:batch_id>')
@login_required
def batch_details(batch_id):
    batch = QRBatch.query.get_or_404(batch_id)
    # Get stats
    total_qrs = len(batch.qrs)
    redeemed_qrs = QRCode.query.filter_by(batch_id=batch_id, is_redeemed=True).count()
    pending_qrs = total_qrs - redeemed_qrs
    
    # Get recent scans in this batch
    recent_scans = QRCode.query.filter_by(batch_id=batch_id, is_redeemed=True).order_by(QRCode.redeemed_at.desc()).limit(10).all()
    
    return render_template('batch_details.html', 
                           batch=batch, 
                           redeemed=redeemed_qrs, 
                           pending=pending_qrs,
                           recent_scans=recent_scans)

@admin_bp.route('/qr-batch/<int:batch_id>/delete', methods=['POST'])
@login_required
def delete_batch(batch_id):
    batch = QRBatch.query.get_or_404(batch_id)
    
    # Check if any QR is redeemed, if so, maybe we shouldn't delete or handle with care.
    # For now, following user request to allow delete.
    
    # Delete all QRs in batch first
    QRCode.query.filter_by(batch_id=batch_id).delete()
    db.session.delete(batch)
    db.session.commit()
    
    flash(f"Batch '{batch.batch_name}' deleted successfully.")
    return redirect(url_for('admin_routes.qr_management'))

@admin_bp.route('/redemptions')
@login_required
def redemptions_list():
    requests = RedemptionRequest.query.order_by(RedemptionRequest.created_at.desc()).all()
    return render_template('redemptions.html', requests=requests)

@admin_bp.route('/redemption/<int:req_id>/approve', methods=['POST'])
@login_required
def approve_redemption(req_id):
    req = RedemptionRequest.query.get_or_404(req_id)
    req.status = 'approved'
    db.session.commit()
    flash('Redemption approved')
    return redirect(url_for('admin_routes.redemptions_list'))

@admin_bp.route('/redemption/<int:req_id>/reject', methods=['POST'])
@login_required
def reject_redemption(req_id):
    req = RedemptionRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    # Refund points
    user = User.query.get(req.user_id)
    reward = Reward.query.get(req.reward_id)
    user.points += reward.points_required
    reward.stock += 1
    
    db.session.commit()
    flash('Redemption rejected and points refunded')
    return redirect(url_for('admin_routes.redemptions_list'))

@admin_bp.route('/support-messages')
@login_required
def messages_admin():
    messages = SupportMessage.query.order_by(SupportMessage.created_at.desc()).all()
    unread_count = sum(1 for m in messages if not m.is_read)
    return render_template('messages_admin.html', messages=messages, unread_count=unread_count)

@admin_bp.route('/support-message/<int:msg_id>')
@login_required
def view_message(msg_id):
    msg = SupportMessage.query.get_or_404(msg_id)
    if not msg.is_read:
        msg.is_read = True
        db.session.commit()
    return render_template('message_view.html', message=msg)

@admin_bp.route('/support-message/<int:msg_id>/delete', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = SupportMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.')
    return redirect(url_for('admin_routes.messages_admin'))
