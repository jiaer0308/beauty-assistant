import asyncio
import sqlite3
import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

class VerifyForgotPassword:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "beauty_assistant.db")
        self.client = TestClient(app)
        
    def _alter_table(self):
        """Add the new columns to the database if they don't exist yet using SQLAlchemy"""
        from sqlalchemy import text
        from app.core.database import engine
        
        print("Checking database schema...")
        try:
            with engine.begin() as conn:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN reset_password_token VARCHAR(255)"))
                    try:
                        conn.execute(text("CREATE UNIQUE INDEX ix_users_reset_password_token ON users (reset_password_token)"))
                    except Exception:
                        pass
                    print("Added reset_password_token column.")
                except Exception as e:
                    pass # Probably already exists
                    
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN reset_password_expires DATETIME"))
                    print("Added reset_password_expires column.")
                except Exception as e:
                    pass # Probably already exists
                    
            print("Database schema check complete.")
            return True
        except Exception as e:
            print(f"Error altering table via SQLAlchemy: {e}")
            return False
            
    def run_tests(self):
        print("Starting forgot password verification tests...")
        
        # 1. First ensure db is altered
        db_ready = self._alter_table()
        if not db_ready:
            print("Failed to prepare database structure!")
            # Will continue anyway to let SQLAlchemy handle it if dynamic, but usually SQLite crashes without alter
            
        test_email = "test_reset@example.com"
        test_password = "old_password123"
        test_new_password = "new_password456"
        
        # 2. Create guest and register
        print("\nStep 1 & 2: Creating guest and registering user...")
        resp = self.client.post("/api/v1/auth/guest")
        if resp.status_code != 201:
            print(f"Failed to create guest: {resp.text}")
            return
            
        guest_token = resp.json().get("guest_token")
        
        # Ignore registration error if user exists from previous test run
        resp = self.client.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": test_password,
            "guest_token": guest_token
        })
        
        if resp.status_code != 200 and "already registered" not in resp.text:
            print(f"Failed to register user: {resp.text}")
            return
            
        print(f"User ready: {test_email}")
        
        # 3. Test Forgot Password
        print("\nStep 3: Requesting forgot password token...")
        resp = self.client.post("/api/v1/auth/forgot-password", json={
            "email": test_email
        })
        
        if resp.status_code != 200:
            print(f"Failed to request forgot password: {resp.status_code} - {resp.text}")
            return
            
        result = resp.json()
        token = result.get("reset_token")
        print(f"Successfully generated token: {token}")
        
        if not token:
            print("Token is missing from response!")
            return
            
        # 4. Test Reset Password
        print("\nStep 4: Resetting password using token...")
        resp = self.client.post("/api/v1/auth/reset-password", json={
            "token": token,
            "new_password": test_new_password
        })
        
        if resp.status_code != 200:
            print(f"Failed to reset password: {resp.status_code} - {resp.text}")
            return
            
        print("Password reset successful!")
        
        # 5. Verify old password fails
        print("\nStep 5: Verifying login with OLD password fails...")
        resp = self.client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        
        if resp.status_code == 401:
            print("✓ Login correctly failed with old password")
        else:
            print(f"❌ Login with old password returned {resp.status_code}")
            return
            
        # 6. Verify new password succeeds
        print("\nStep 6: Verifying login with NEW password succeeds...")
        resp = self.client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": test_new_password
        })
        
        if resp.status_code == 200:
            print("✓ Login successful with new password!")
            print("\n✅ Verification complete! Forgot Password feature works seamlessly.")
        else:
            print(f"❌ Login with new password failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    verifier = VerifyForgotPassword()
    verifier.run_tests()
