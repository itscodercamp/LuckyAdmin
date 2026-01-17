import requests
import json
import uuid
import sys
import os

# Configuration
BASE_URL = "http://127.0.0.1:5000/api"

def print_header(text):
    print("\n" + "="*50)
    print(f" {text.upper()} ")
    print("="*50)

def test_registration():
    print_header("Testing Registration")
    # Generate random user data
    test_id = str(uuid.uuid4())[:4]
    payload = {
        "name": f"Test User {test_id}",
        "phone": f"900000{test_id}", # Simulated phone number
        "email": f"test_{test_id}@luckylubricant.com",
        "city": "Mumbai",
        "state": "Maharashtra",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            return payload
        else:
            print("Registration failed. Using existing user if available...")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login(credentials):
    print_header("Testing Login")
    payload = {
        "identifier": credentials['phone'],
        "password": credentials['password']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            return data.get('user')
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_profile(user_id):
    print_header("Testing Profile Fetch")
    try:
        response = requests.get(f"{BASE_URL}/auth/profile", params={"user_id": user_id})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_products():
    print_header("Testing Products List")
    try:
        response = requests.get(f"{BASE_URL}/products/list")
        products = response.json()
        print(f"Status: {response.status_code}")
        print(f"Found {len(products)} products")
        if products:
            print(f"First product: {products[0]['name']} - ₹{products[0]['price']}")
        return products
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_rewards():
    print_header("Testing Rewards List")
    try:
        response = requests.get(f"{BASE_URL}/rewards/list")
        rewards = response.json()
        print(f"Status: {response.status_code}")
        print(f"Found {len(rewards)} rewards")
        if rewards:
            print(f"First reward: {rewards[0]['name']} - {rewards[0]['points_required']} points")
        return rewards
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_wallet(user_id):
    print_header("Testing Wallet Balance")
    try:
        response = requests.get(f"{BASE_URL}/wallet/balance", params={"user_id": user_id})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_transactions(user_id):
    print_header("Testing Transactions")
    try:
        response = requests.get(f"{BASE_URL}/wallet/transactions", params={"user_id": user_id})
        txs = response.json()
        print(f"Status: {response.status_code}")
        print(f"Found {len(txs)} transactions")
        for tx in txs[:3]: # Show last 3
            print(f"- {tx['date']}: {tx['type']} {tx['amount']} pts ({tx['description']})")
    except Exception as e:
        print(f"Error: {e}")

def test_cart(user_id, product_id):
    print_header("Testing Add to Cart")
    payload = {"user_id": user_id, "product_id": product_id}
    try:
        response = requests.post(f"{BASE_URL}/products/cart/add", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_scan(user_id, qr_uuid):
    if not qr_uuid:
        print("\nSkipping Scan Test: No valid QR UUID provided")
        return
    
    print_header("Testing QR Scan")
    payload = {"user_id": user_id, "uuid": qr_uuid}
    try:
        response = requests.post(f"{BASE_URL}/wallet/scan", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_scan_via_file(user_id):
    print_header("Testing QR Scan via File Selection")
    print("Opening file dialog... Please select a QR code image or text file containing the UUID.")
    
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw() # Hide the main window
        root.attributes('-topmost', True) # Bring to front
        
        file_path = filedialog.askopenfilename(
            title="Select QR Code File",
            filetypes=[("All Files", "*.*"), ("Images", "*.png *.jpg *.jpeg"), ("Text Files", "*.txt")]
        )
        root.destroy()
        
        if not file_path:
            print("No file selected. Skipping.")
            return

        print(f"File selected: {file_path}")
        
        # Simple logic: if it's a text file, read the uuid. 
        # If it's an image, we try to extract uuid from filename or content.
        # For this demo, we'll try to read it as a string if it's small, 
        # or if it has 'qr_' in it, try to find a UUID in the string.
        
        content = ""
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r') as f:
                content = f.read().strip()
        else:
            # If it's an image, let's see if the user has pyzbar. 
            # If not, we ask for the UUID manually as a fallback.
            try:
                from PIL import Image
                from pyzbar.pyzbar import decode
                decoded = decode(Image.open(file_path))
                if decoded:
                    content = decoded[0].data.decode('utf-8')
                else:
                    print("Could not decode QR from image.")
            except ImportError:
                print("PIL or pyzbar not installed. Cannot decode image automatically.")
        
        if not content:
            content = input("Could not auto-detect UUID. Please enter the UUID manually: ").strip()

        if content:
            test_scan(user_id, content)
            
    except Exception as e:
        print(f"Error in file selection: {e}")

def get_unredeemed_qr():
    # Helper to find a QR code from DB for testing
    print_header("Finding Test QR Code")
    try:
        from app import create_app
        from models import db, QRCode
        app = create_app()
        with app.app_context():
            qr = QRCode.query.filter_by(is_redeemed=False).first()
            if qr:
                print(f"Found unredeemed QR: {qr.uuid} ({qr.points} pts)")
                return qr.uuid
            else:
                print("No unredeemed QR codes found in database.")
                return None
    except Exception as e:
        print(f"Could not access DB directly: {e}")
        return None

def test_redeem(user_id, rewards, points):
    if not rewards:
        print("\nSkipping Redemption Test: No rewards available")
        return
    
    # Find a reward the user can afford
    reward_to_redeem = None
    for r in rewards:
        if r['points_required'] <= points:
            reward_to_redeem = r
            break
    
    if not reward_to_redeem:
        print(f"\nSkipping Redemption Test: Insufficient points ({points}) for any reward")
        return

    print_header(f"Testing Redemption: {reward_to_redeem['name']}")
    payload = {"user_id": user_id, "reward_id": reward_to_redeem['id']}
    try:
        response = requests.post(f"{BASE_URL}/rewards/redeem", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def run_all_tests():
    print("\n" + "#"*60)
    print("      LUCKY LUBRICANT API FEATURE CHECKER      ")
    print("#"*60)

    # 1. Registration
    creds = test_registration()
    if not creds:
        # Fallback to sample user if registration fails (e.g. already exists)
        creds = {"phone": "9876543210", "password": "user123"}
        print("Using fallback credentials: 9876543210 / user123")

    # 2. Login
    user = test_login(creds)
    if not user:
        print("Login failed, cannot continue with other tests.")
        return
    
    user_id = user['id']
    current_points = user.get('points', 0)

    # 3. Profile
    test_profile(user_id)

    # 4. Products & Cart
    products = test_products()
    if products:
        test_cart(user_id, products[0]['id'])

    # 5. Rewards
    rewards = test_rewards()

    # 6. Wallet & QR Scan
    test_wallet(user_id)
    
    # Optional QR Scan (requires direct DB access to find a valid code)
    qr_uuid = get_unredeemed_qr()
    test_scan(user_id, qr_uuid)

    # NEW: QR Scan via File Upload (Tkinter)
    use_file = input("\nDo you want to test QR scanning by selecting a file? (y/n): ").lower()
    if use_file == 'y':
        test_scan_via_file(user_id)

    # 7. Redemption Test
    # Refresh points after scan
    try:
        response = requests.get(f"{BASE_URL}/wallet/balance", params={"user_id": user_id})
        current_points = response.json().get('points', 0)
    except: pass
    
    test_redeem(user_id, rewards, current_points)

    # 8. Final Balance & Transactions
    test_wallet(user_id)
    test_transactions(user_id)

    print("\n" + "#"*60)
    print("               TESTING COMPLETE                ")
    print("#"*60)

if __name__ == "__main__":
    run_all_tests()
