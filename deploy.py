import os
import subprocess
import sys
import secrets
import shutil

def run_command(command):
    print(f"Executing: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr.decode()}")
    else:
        print(stdout.decode())

def setup():
    print("🚀 Starting Lucky Lubricant Production Setup...")

    # 1. Install requirements
    print("\n📦 Installing/Updating requirements...")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")

    # 2. Cleanup unwanted DB files
    print("\n🧹 Cleaning up old database files...")
    db_files = ["sql_app.db", "sql_app_v2.db"]
    for db in db_files:
        if os.path.exists(db):
            try:
                os.remove(db)
                print(f"Removed {db}")
            except Exception as e:
                print(f"Could not remove {db}: {e}")

    # 3. Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("\n📝 Creating .env file...")
        secret = secrets.token_hex(32)
        env_content = f"""# Production Security
SECRET_KEY={secret}
CORS_ORIGINS=*

# Database
# DB_URL=sqlite:///./sql_app_prod.db
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print(".env file created with a fresh SECRET_KEY.")

    # 4. Initialize Production Database & Admin
    print("\n🔑 Creating Production Admin User...")
    phone = input("Enter Admin Phone: ")
    password = input("Enter Admin Password: ")
    run_command(f"{sys.executable} seed.py --phone {phone} --password {password} --name 'Super Admin' --action create")

    print("\n✅ Setup Complete!")
    print("\nTo start the production server, run:")
    print("gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000")

if __name__ == "__main__":
    setup()
