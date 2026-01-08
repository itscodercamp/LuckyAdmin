# Lucky Lubricant - Admin API Documentation

All endpoints in this document require an **Admin Bearer Token**.
**Base URL**: `http://localhost:8001/api/admin`
**Header**: `Authorization: Bearer <admin_jwt_token>`

## 📊 Dashboard & Stats

### 1. Get System Statistics
- **URL**: `/stats`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "total_users": 10,
    "total_vouchers": 100,
    "used_vouchers": 25,
    "total_points_distributed": 50000,
    "total_point_redeemed": 15000,
    "wallet_liability": 35000
  }
  ```

---

## 🎫 Voucher (QR) Management

### 1. Generate QR Lot (70/30 Distribution)
- **URL**: `/vouchers/generate`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "total_count": 100,
    "lot_name": "NewYear2026",
    "min_points": 50,
    "max_points": 500,
    "min_points_percentage": 70,
    "max_points_percentage": 30
  }
  ```
- **Logic**: Creates 70% min_points and 30% max_points vouchers.

### 2. List All Lots
- **URL**: `/vouchers/lots`
- **Method**: `GET`
- **Response**: `["NewYear2026", "Diwali2025"]`

### 3. Get Vouchers in a Lot
- **URL**: `/vouchers/lot/{lot_id}`
- **Method**: `GET`

---

## 👥 User Management

### 1. List All Users
- **URL**: `/users`
- **Method**: `GET`

### 2. Toggle User Status (Block/Unblock)
- **URL**: `/users/{user_id}/status`
- **Method**: `PATCH`
- **Params**: `is_active` (boolean query param)

---

## 🛍️ Rewards & Orders

### 1. List All Redemption Requests (Orders)
- **URL**: `/orders`
- **Method**: `GET`
- **Response**: Full list with linked User and Product details.

### 2. Update Order Status
- **URL**: `/orders/{order_id}`
- **Method**: `PATCH`
- **Params**: `status` (string query param: "delivered", "cancelled", etc.)

### 3. Add New Product/Reward
- **URL**: `/products/add`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "Cap",
    "description": "Premium Quality",
    "points_required": 1000,
    "image_url": "url",
    "category": "Goodies",
    "is_active": true
  }
  ```

---

## 📜 Transactions & Banners

### 1. View Global Transaction History
- **URL**: `/transactions`
- **Method**: `GET`
- **Details**: Shows every credit (scan) and debit (redemption) with user tags.

### 2. Add Promo Banner
- **URL**: `/banners/add`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "title": "Welcome Offer",
    "image_url": "url",
    "expiry_date": "2026-12-31T00:00:00",
    "active_status": true
  }
  ```

---

## 🛠️ Management Scripts (CLI)

These scripts are used directly on the server for system management.

### 1. Unified Deployment (`deploy.py`)
- **Purpose**: Automated setup, dependency installation, and database cleanup.
- **Usage**: `python deploy.py`

### 2. Admin User Management (`seed.py`)
- **Purpose**: Create or update admin credentials without using HTTP APIs.
- **Usage**:
  - Create: `python seed.py --phone 9876543210 --password pass --name "Admin" --action create`
  - Update: `python seed.py --phone 9876543210 --password newpass --action update`
