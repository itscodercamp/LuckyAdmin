import sqlite3
import os

db_path = 'instance/lucky_lubricant.db'
if not os.path.exists(db_path):
    db_path = 'lucky_lubricant.db'

print(f"Checking database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(notifications)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_admin_alert' not in columns:
        print("Adding 'is_admin_alert' column to 'notifications' table...")
        cursor.execute("ALTER TABLE notifications ADD COLUMN is_admin_alert BOOLEAN DEFAULT 0")
    else:
        print("'is_admin_alert' column already exists.")

    # Also check if user_id is nullable (though SQLite doesn't easily support changing nullability via ALTER)
    # But since we are here, let's at least ensure is_admin_alert is there.
    
    conn.commit()
    conn.close()
    print("Database fix completed successfully.")
except Exception as e:
    print(f"Error fixing database: {e}")
