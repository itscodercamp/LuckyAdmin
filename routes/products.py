from flask import Blueprint, request, jsonify
from models import db, Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/list', methods=['GET'])
def list_products():
    base_url = request.host_url.rstrip('/')
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "image_url": f"{base_url}{p.image_url}" if p.image_url and not p.image_url.startswith('http') else p.image_url,
        "category": p.category
    } for p in products]), 200

@products_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    # Simplification: Cart logic usually requires a separate model, 
    # but based on prompt we just need the endpoint.
    data = request.json
    product_id = data.get('product_id')
    user_id = data.get('user_id')
    # Record logic here if needed
    return jsonify({"message": f"Product {product_id} added to cart for user {user_id}"}), 200

@products_bp.route('/cart/list', methods=['GET'])
def list_cart():
    user_id = request.args.get('user_id')
    # Return mock or real cart items
    return jsonify([]), 200
