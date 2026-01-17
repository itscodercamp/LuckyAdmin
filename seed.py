from app import create_app
from models import db, Admin, Product, Reward, User
from werkzeug.security import generate_password_hash

app = create_app()

def seed():
    with app.app_context():
        # Create Admin
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            print("Admin created: admin / admin123")

        # Create Sample Products
        if Product.query.count() == 0:
            products = [
                Product(name="Fully Synthetic 5W-40", description="Premium engine oil for high performance", price=1200.0, category="Engine Oil"),
                Product(name="Semi Synthetic 10W-30", description="Reliable protection for daily use", price=850.0, category="Engine Oil"),
                Product(name="Diesel Engine Oil 15W-40", description="Heavy duty oil for trucks", price=2500.0, category="Lube"),
            ]
            db.session.bulk_save_objects(products)
            print("Products seeded")

        # Create Sample Rewards
        if Reward.query.count() == 0:
            rewards = [
                Reward(name="Mobile Recharge ₹100", description="Redeem points for ₹100 recharge", points_required=500, stock=100),
                Reward(name="Amazon Voucher ₹500", description="E-gift voucher for shopping", points_required=2000, stock=50),
                Reward(name="Engine Flush Kit", description="Professional engine cleaning kit", points_required=1500, stock=20),
            ]
            db.session.bulk_save_objects(rewards)
            print("Rewards seeded")

        # Create Sample User
        if not User.query.filter_by(phone='9876543210').first():
            user = User(
                name="Test User",
                phone="9876543210",
                email="test@example.com",
                city="Mumbai",
                state="Maharashtra",
                password_hash=generate_password_hash('user123'),
                points=1000
            )
            db.session.add(user)
            print("Sample user created: 9876543210 / user123")

        db.session.commit()
        print("Seeding complete")

if __name__ == '__main__':
    seed()
