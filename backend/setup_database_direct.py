"""
Direct Database Setup for Adhi Compliance
Executes SQL queries directly against Supabase PostgreSQL
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get direct PostgreSQL connection to Supabase"""
    
    # Parse the database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("[ERROR] DATABASE_URL not found in environment")
        return None
    
    try:
        print("[INFO] Connecting to Supabase database...")
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("[SUCCESS] Connected to database")
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def execute_sql_file(conn, file_path):
    """Execute SQL commands from a file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        cursor = conn.cursor()
        
        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        for i, command in enumerate(commands):
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    print(f"[OK] Executed command {i+1}/{len(commands)}")
                except Exception as e:
                    print(f"[WARNING] Command {i+1} failed: {e}")
        
        cursor.close()
        print(f"[SUCCESS] Executed SQL file: {file_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to execute {file_path}: {e}")
        return False

def setup_complete_database():
    """Setup the complete Adhi Compliance database"""
    
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        print("\n=== SETTING UP ADHI COMPLIANCE DATABASE ===")
        
        # Step 1: Create enum types
        print("\n[STEP 1] Creating enum types...")
        if execute_sql_file(conn, "supabase_schema_fixed.sql"):
            print("[SUCCESS] Enum types created")
        
        # Step 2: Create tables
        print("\n[STEP 2] Creating tables...")
        if execute_sql_file(conn, "supabase_tables_uuid.sql"):
            print("[SUCCESS] Tables created")
        
        # Step 3: Insert seed data
        print("\n[STEP 3] Inserting demo data...")
        if execute_sql_file(conn, "supabase_seed_data_uuid.sql"):
            print("[SUCCESS] Demo data inserted")
        
        # Step 4: Verify setup
        print("\n[STEP 4] Verifying setup...")
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'ai_systems', 'compliance_checks', 'bias_audits', 'incidents')
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"[VERIFY] Found {len(tables)} Adhi tables: {[t[0] for t in tables]}")
        
        # Check data counts
        cursor.execute("SELECT COUNT(*) FROM ai_systems")
        ai_systems_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM compliance_checks")
        compliance_count = cursor.fetchone()[0]
        
        print(f"[VERIFY] Data counts:")
        print(f"  - AI Systems: {ai_systems_count}")
        print(f"  - Users: {users_count}")
        print(f"  - Compliance Checks: {compliance_count}")
        
        cursor.close()
        
        print("\n[SUCCESS] Database setup complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
        return False
    finally:
        conn.close()

def link_auth_user():
    """Link the Supabase auth user to database user"""
    
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("\n[LINKING] Connecting auth user to database user...")
        
        # Check if auth user exists
        cursor.execute("""
            SELECT id, email FROM auth.users 
            WHERE email = 'ganeshkhovalan2203@gmail.com'
        """)
        auth_user = cursor.fetchone()
        
        if not auth_user:
            print("[ERROR] Auth user not found. Please create it in Supabase Dashboard first.")
            return False
        
        auth_user_id, auth_email = auth_user
        print(f"[FOUND] Auth user: {auth_email} (ID: {auth_user_id})")
        
        # Update database user
        cursor.execute("""
            UPDATE users 
            SET 
                id = %s,
                email = %s
            WHERE email = 'ganesh@rootedai.co.in'
        """, (auth_user_id, auth_email))
        
        # Verify the update
        cursor.execute("""
            SELECT id, email, name, role FROM users 
            WHERE email = %s
        """, (auth_email,))
        
        db_user = cursor.fetchone()
        if db_user:
            print(f"[SUCCESS] Linked user: {db_user[1]} ({db_user[2]}) - Role: {db_user[3]}")
            print(f"[SUCCESS] User ID matches: {db_user[0] == auth_user_id}")
            cursor.close()
            return True
        else:
            print("[ERROR] Failed to link user")
            cursor.close()
            return False
            
    except Exception as e:
        print(f"[ERROR] User linking failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Adhi Compliance - Direct Database Setup")
    print("=" * 50)
    
    # Setup database
    if setup_complete_database():
        # Link auth user
        if link_auth_user():
            print("\n[COMPLETE] Database setup and user linking successful!")
            print("\nNext steps:")
            print("1. Test authentication: py test_auth_simple.py")
            print("2. Access frontend: http://localhost:3000")
        else:
            print("\n[PARTIAL] Database setup complete, but user linking failed.")
            print("Please create auth user in Supabase Dashboard first.")
    else:
        print("\n[FAILED] Database setup failed.")