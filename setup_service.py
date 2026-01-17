import os

# Configuration (Change these if needed)
APP_NAME = "lucky_lubricant"
PROJECT_DIR = os.getcwd()
VENV_BIN = os.path.join(PROJECT_DIR, "venv", "bin") # Assumes a virtualenv named 'venv'
USER = os.getenv("USER", "root")
PORT = 5000

service_template = f"""[Unit]
Description=Gunicorn instance to serve {APP_NAME}
After=network.target

[Service]
User={USER}
Group=www-data
WorkingDirectory={PROJECT_DIR}
Environment="PATH={VENV_BIN}"
ExecStart={VENV_BIN}/gunicorn --workers 3 --bind 0.0.0.0:{PORT} wsgi:app

[Install]
WantedBy=multi-user.target
"""

def setup_service():
    print(f"--- Gunicorn Systemd Setup ---")
    service_path = f"/etc/systemd/system/{APP_NAME}.service"
    
    try:
        # Create the service file content
        with open(f"{APP_NAME}.service", "w") as f:
            f.write(service_template)
        
        print(f"\n1. Service file '{APP_NAME}.service' created locally.")
        print(f"2. To deploy, run the following commands on your server:\n")
        print(f"sudo cp {PROJECT_DIR}/{APP_NAME}.service {service_path}")
        print(f"sudo systemctl daemon-reload")
        print(f"sudo systemctl enable {APP_NAME}")
        print(f"sudo systemctl start {APP_NAME}")
        print(f"sudo systemctl status {APP_NAME}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_service()
