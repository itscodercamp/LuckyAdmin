# Lucky Lubricant - API Documentation

This document outlines all the available API endpoints for the Lucky Lubricant application, including their methods, parameters, and expected responses.

## Base URL
`http://<server-ip>:5000/api`

---

## 1. Authentication ( /auth )

### **Login**
*   **Endpoint:** `/auth/login`
*   **Method:** `POST`
*   **Payload:**
    ```json
    {
        "identifier": "phone_or_email",
        "password": "user_password"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
        "message": "Login successful",
        "user": { "id": 1, "name": "John", "phone": "123", "email": "j@g.com", "points": 100 }
    }
    ```

### **Register**
*   **Endpoint:** `/auth/register`
*   **Method:** `POST`
*   **Payload:**
    ```json
    {
        "name": "Full Name",
        "phone": "9876543210",
        "email": "user@example.com",
        "city": "City Name",
        "state": "State Name",
        "password": "secure_password"
    }
    ```
*   **Response (201 Created):**
    ```json
    { "message": "User registered successfully" }
    ```

### **Update Profile Image**
*   **Endpoint:** `/auth/profile-image`
*   **Method:** `POST` (Multipart/form-data)
*   **Parameters:**
    *   `user_id` (Form Data)
    *   `file` (Image File)
*   **Response (200 OK):**
    ```json
    { "message": "Profile image updated", "path": "uploads/user_1_image.jpg" }
    ```

### **Get Profile**
*   **Endpoint:** `/auth/profile`
*   **Method:** `GET`
*   **Query Params:** `?user_id=1`
*   **Response (200 OK):**
    ```json
    {
        "name": "John",
        "phone": "123",
        "email": "j@g.com",
        "city": "Mumbai",
        "state": "MH",
        "points": 100,
        "profile_image": "uploads/..."
    }
    ```

---

## 2. Wallet & QR ( /wallet )

### **Check Balance**
*   **Endpoint:** `/wallet/balance`
*   **Method:** `GET`
*   **Query Params:** `?user_id=1`
*   **Response (200 OK):**
    ```json
    { "points": 550 }
    ```

### **Scan QR Code**
*   **Endpoint:** `/wallet/scan`
*   **Method:** `POST`
*   **Payload:**
    ```json
    {
        "uuid": "qr-uuid-from-scan",
        "user_id": 1
    }
    ```
*   **Response (200 OK):**
    ```json
    {
        "message": "Scan successful",
        "points_earned": 50,
        "new_balance": 600
    }
    ```

### **Transaction History**
*   **Endpoint:** `/wallet/transactions`
*   **Method:** `GET`
*   **Query Params:** `?user_id=1`
*   **Response (200 OK):**
    ```json
    [
        { "id": 1, "amount": 50, "type": "earn", "description": "QR Scan", "date": "2024-01-01 12:00:00" }
    ]
    ```

---

## 3. Rewards & Guddies ( /rewards )

### **List Available Rewards**
*   **Endpoint:** `/rewards/list`
*   **Method:** `GET`
*   **Response (200 OK):**
    ```json
    [
        { "id": 1, "name": "T-Shirt", "points_required": 500, "stock": 10, "image_url": "..." }
    ]
    ```

### **Redeem Reward**
*   **Endpoint:** `/rewards/redeem`
*   **Method:** `POST`
*   **Payload:**
    ```json
    {
        "reward_id": 1,
        "user_id": 1
    }
    ```
*   **Response (200 OK):**
    ```json
    { "message": "Redemption request submitted", "new_balance": 100 }
    ```

### **Redemption History**
*   **Endpoint:** `/rewards/redemption-history`
*   **Method:** `GET`
*   **Query Params:** `?user_id=1`
*   **Response (200 OK):**
    ```json
    [
        { "id": 1, "reward_name": "T-Shirt", "status": "pending", "date": "..." }
    ]
    ```

---

## 4. Product Catalog ( /products )

### **List Products**
*   **Endpoint:** `/products/list`
*   **Method:** `GET`
*   **Response (200 OK):**
    ```json
    [
        { "id": 1, "name": "Engine Oil", "price": 450.0, "category": "Oils", "image_url": "..." }
    ]
    ```

### **Add to Cart**
*   **Endpoint:** `/products/cart/add`
*   **Method:** `POST`
*   **Payload:**
    ```json
    { "product_id": 1, "user_id": 1 }
    ```

---

## 5. App Content & Support ( /api/content )

### **Contact Support**
*   **Endpoint:** `/api/content/support/contact`
*   **Method:** `POST`
*   **Payload:**
    ```json
    { "user_id": 1, "subject": "Order Issue", "message": "My points haven't added" }
    ```

### **App Banners**
*   **Endpoint:** `/api/content/banners`
*   **Method:** `GET`
*   **Response (200 OK):**
    ```json
    [ { "image_url": "banner1.jpg", "link": "promo_url" } ]
    ```

### **User Notifications**
*   **Endpoint:** `/api/content/notifications`
*   **Method:** `GET`
*   **Query Params:** `?user_id=1`
*   **Response (200 OK):**
    ```json
    [ { "id": 1, "title": "Welcome", "message": "Hello!", "is_read": false } ]
    ```
