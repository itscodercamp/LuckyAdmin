from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    phone: str
    city: str
    state: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    phone: str
    password: str

class UserResponse(UserBase):
    id: int
    points_balance: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone: Optional[str] = None

class VoucherBase(BaseModel):
    uuid: str
    points: int
    is_used: bool

class VoucherResponse(VoucherBase):
    id: int
    used_at: Optional[datetime] = None
    lot_id: str

    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: int
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    points_required: int
    image_url: str
    category: str
    is_active: bool

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class BannerResponse(BaseModel):
    id: int
    title: str
    image_url: str
    expiry_date: Optional[datetime] = None
    active_status: bool

    class Config:
        from_attributes = True

class SupportInquiry(BaseModel):
    subject: str
    message: str

class QRGenConfig(BaseModel):
    total_count: int
    lot_name: str
    min_points: int
    max_points: int
    min_points_percentage: int # e.g. 70
    max_points_percentage: int # e.g. 30
