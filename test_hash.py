from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
try:
    h = pwd_context.hash("admin_pass")
    print(f"Hash: {h}")
    print(f"Verify: {pwd_context.verify('admin_pass', h)}")
except Exception as e:
    print(f"Error: {e}")
