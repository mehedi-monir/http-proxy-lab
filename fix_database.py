import sqlite3
import os
from datetime import datetime

def backup_database():
    """Create backup of existing database"""
    if os.path.exists('proxy_server.db'):
        backup_name = f'proxy_server_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil
        shutil.copy('proxy_server.db', backup_name)
        print(f"Database backed up to: {backup_name}")
        return True
    return False

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_database():
    """Migrate database to add missing columns"""
    print("Starting database migration...")
    
    # Connect to database
    conn = sqlite3.connect('proxy_server.db')
    cursor = conn.cursor()
    
    try:
        # Check if access_logs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='access_logs'")
        if not cursor.fetchone():
            print("access_logs table doesn't exist!")
            print("Creating new database schema...")
            create_fresh_database(conn, cursor)
            return
        
        # Check if 'blocked' column exists
        if not check_column_exists(cursor, 'access_logs', 'blocked'):
            print(" 'blocked' column missing in access_logs table")
            print(" Adding 'blocked' column...")
            
            cursor.execute("""
                ALTER TABLE access_logs 
                ADD COLUMN blocked INTEGER DEFAULT 0
            """)
            
            conn.commit()
            print("Successfully added 'blocked' column")
        else:
            print(" Database is up to date")
        
        # Verify all required tables exist
        verify_schema(cursor)
        
    except Exception as e:
        print(f" Migration error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print(" Database migration completed successfully!")

def create_fresh_database(conn, cursor):
    """Create fresh database with correct schema"""
    
    # Create blocked_sites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_pattern TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create access_logs table with 'blocked' column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_ip TEXT,
            url TEXT,
            method TEXT,
            status_code INTEGER,
            blocked INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            url TEXT PRIMARY KEY,
            content BLOB,
            content_type TEXT,
            expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("Fresh database created with correct schema")

def verify_schema(cursor):
    """Verify all tables and columns exist"""
    required_tables = {
        'blocked_sites': ['id', 'url_pattern', 'created_at'],
        'access_logs': ['id', 'client_ip', 'url', 'method', 'status_code', 'blocked', 'timestamp'],
        'cache': ['url', 'content', 'content_type', 'expires', 'created_at']
    }
    
    print("\n Verifying database schema...")
    
    for table, columns in required_tables.items():
        cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        missing = set(columns) - set(existing_columns)
        if missing:
            print(f" Table '{table}' missing columns: {missing}")
        else:
            print(f" Table '{table}' - OK ({len(existing_columns)} columns)")

def main():
    """Main entry point"""
    print("  DATABASE MIGRATION TOOL                 ")
    print("   HTTP Proxy Server                      \n")
    
    # Check if database exists
    if not os.path.exists('proxy_server.db'):
        print(" No existing database found")
        print(" Creating new database...")
        conn = sqlite3.connect('proxy_server.db')
        cursor = conn.cursor()
        create_fresh_database(conn, cursor)
        conn.close()
    else:
        # Backup existing database
        if backup_database():
            # Run migration
            migrate_database()
    
    print("\n All done! You can now run: python run.py")

if __name__ == '__main__':
    main()