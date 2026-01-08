import argparse
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash

def manage_admin(phone, password, name, action):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    admin = db.query(User).filter(User.phone == phone).first()
    
    if action == "create":
        if admin:
            print(f"User with phone {phone} already exists. Use 'update' to change password.")
        else:
            admin_user = User(
                name=name,
                phone=phone,
                city="HQ",
                state="System",
                email=f"admin_{phone}@luckylubricant.com",
                hashed_password=get_password_hash(password),
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Admin user '{name}' created successfully with phone {phone}.")
            
    elif action == "update":
        if not admin:
            print(f"Admin with phone {phone} not found.")
        else:
            admin.hashed_password = get_password_hash(password)
            admin.is_admin = True # Ensure it's admin
            db.commit()
            print(f"Password for admin {phone} updated successfully.")
            
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Lucky Lubricant Admin Credentials")
    parser.add_argument("--phone", required=True, help="Admin phone number")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--name", default="Super Admin", help="Admin name (for create)")
    parser.add_argument("--action", choices=["create", "update"], default="create", help="Action to perform")
    
    args = parser.parse_args()
    manage_admin(args.phone, args.password, args.name, args.action)
