import sqlite3
import os

db_path = 'instance/lucky_lubricant.db'
if not os.path.exists(db_path):
    db_path = 'lucky_lubricant.db'

print(f"Fixing Notification table at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(notifications)")
    cols = cursor.fetchall()
    col_names = [c[1] for c in cols]
    
    # If notifications exists, we migrate it
    cursor.execute("ALTER TABLE notifications RENAME TO notifications_old")
    
    # Create new table with nullable user_id
    cursor.execute("""
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title VARCHAR(100),
            message TEXT,
            is_read BOOLEAN DEFAULT 0,
            is_admin_alert BOOLEAN DEFAULT 0,
            created_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    # Copy data back
    # Handle the case where is_admin_alert might not exist in old table if fix_db failed earlier
    if 'is_admin_alert' in col_names:
        cursor.execute("""
            INSERT INTO notifications (id, user_id, title, message, is_read, is_admin_alert, created_at)
            SELECT id, user_id, title, message, is_read, is_admin_alert, created_at FROM notifications_old
        """)
    else:
        cursor.execute("""
            INSERT INTO notifications (id, user_id, title, message, is_read, created_at)
            SELECT id, user_id, title, message, is_read, created_at FROM notifications_old
        """)
        
    cursor.execute("DROP TABLE notifications_old")
    
    conn.commit()
    conn.close()
    print("Notification table migrated successfully. user_id is now nullable.")
except Exception as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()
