# Lucky Lubricant Reward System API

FastAPI based reward system with QR code management and user wallet.

## Features
- **User Authentication**: Register, Login, Profile Management.
- **Wallet System**: Scan vouchers (QR codes) to earn points, view transaction history.
- **Rewards**: List products and redeem them using earned points.
- **Content**: Dynamic banners and user notifications.
- **Admin Panel**: 
  - Lot-based QR generation with custom point distribution (e.g., 70% low points, 30% high points).
  - Product/Reward management.
  - System statistics.

## Tech Stack
- FastAPI
- SQLAlchemy (SQLite3)
- JWT Authentication
- Pydantic

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database & Admin User**:
   ```bash
   python seed.py
   ```
   *Default Admin Credentials:*
   - Phone: `1234567890`
   - Password: `admin123`

3. **Start the API Server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access Documentation**:
   - Interactive Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API endpoints

### Auth
- `POST /api/auth/register`: Create new account.
- `POST /api/auth/login`: Get JWT token.
- `POST /api/auth/forgot-password`: Reset password flow.

### Wallet
- `GET /api/wallet/balance`: Check current points.
- `POST /api/wallet/scan`: Scan a QR UUID to add points.
- `GET /api/wallet/transactions`: view credit/debit history.

### Admin
- `POST /api/admin/vouchers/generate`: Generate a lot of QR codes with point distribution.
- `GET /api/admin/vouchers/lots`: List all generation lots.
- `GET /api/admin/stats`: view system performance stats.
