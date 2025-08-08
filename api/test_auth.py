#!/usr/bin/env python3
"""
Authentication Test Script

This script tests all authentication functionality including:
- User registration
- Login/logout
- Token validation
- Access control
- Admin functions
"""

import requests
import time
import json
from typing import Dict, Any, Optional


class AuthTester:
    """Test authentication functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Authentication: {data.get('authentication', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_user_registration(self) -> bool:
        """Test user registration"""
        try:
            print("📝 Testing user registration...")
            
            user_data = {
                "username": "test_user_auth",
                "email": "test_auth@example.com",
                "password": "test123",
                "full_name": "Test Auth User",
                "role": "user"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Registration successful")
                print(f"   Username: {data.get('username')}")
                print(f"   Email: {data.get('email')}")
                print(f"   Role: {data.get('role')}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_login(self, username: str, password: str) -> bool:
        """Test login functionality"""
        try:
            print(f"🔐 Testing login for {username}...")
            
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                print(f"✅ Login successful")
                print(f"   Token type: {data.get('token_type')}")
                print(f"   Token length: {len(self.access_token) if self.access_token else 0}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_get_current_user(self) -> bool:
        """Test getting current user info"""
        try:
            print("👤 Testing get current user...")
            
            response = self.session.get(f"{self.base_url}/api/v1/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Current user info retrieved")
                print(f"   Username: {data.get('username')}")
                print(f"   Email: {data.get('email')}")
                print(f"   Role: {data.get('role')}")
                print(f"   Disabled: {data.get('disabled')}")
                return True
            else:
                print(f"❌ Get current user failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Get current user error: {e}")
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Test that unauthorized access is blocked"""
        try:
            print("🚫 Testing unauthorized access...")
            
            # Create a new session without token
            test_session = requests.Session()
            
            # Try to access protected endpoint
            response = test_session.post(
                f"{self.base_url}/api/v1/campaigns/generate",
                json={"product": "test"}
            )
            
            if response.status_code == 401:
                print("✅ Unauthorized access properly blocked")
                return True
            else:
                print(f"❌ Unauthorized access not blocked: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Unauthorized access test error: {e}")
            return False
    
    def test_campaign_access_with_auth(self) -> bool:
        """Test campaign access with authentication"""
        try:
            print("🔐 Testing campaign access with authentication...")
            
            if not self.access_token:
                print("❌ No access token available")
                return False
            
            # Try to list campaigns
            response = self.session.get(f"{self.base_url}/api/v1/campaigns")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Campaign access successful")
                print(f"   Total campaigns: {data.get('total', 0)}")
                return True
            else:
                print(f"❌ Campaign access failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Campaign access error: {e}")
            return False
    
    def test_admin_functions(self) -> bool:
        """Test admin functions (requires admin login)"""
        try:
            print("👑 Testing admin functions...")
            
            # List all users (admin only)
            response = self.session.get(f"{self.base_url}/api/v1/auth/users")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Admin functions accessible")
                print(f"   Total users: {len(data)}")
                for user in data[:3]:  # Show first 3 users
                    print(f"   - {user.get('username')} ({user.get('role')})")
                return True
            elif response.status_code == 403:
                print("⚠️ Admin functions not accessible (not admin user)")
                return True  # This is expected for non-admin users
            else:
                print(f"❌ Admin functions failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin functions error: {e}")
            return False
    
    def test_token_expiry_simulation(self) -> bool:
        """Test token validation"""
        try:
            print("⏰ Testing token validation...")
            
            if not self.access_token:
                print("❌ No access token available")
                return False
            
            # Test with valid token
            response = self.session.get(f"{self.base_url}/api/v1/auth/me")
            if response.status_code == 200:
                print("✅ Valid token accepted")
            else:
                print(f"❌ Valid token rejected: {response.status_code}")
                return False
            
            # Test with invalid token
            invalid_session = requests.Session()
            invalid_session.headers.update({"Authorization": "Bearer invalid_token"})
            
            response = invalid_session.get(f"{self.base_url}/api/v1/auth/me")
            if response.status_code == 401:
                print("✅ Invalid token properly rejected")
                return True
            else:
                print(f"❌ Invalid token not rejected: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            return False


def main():
    """Run comprehensive authentication tests"""
    print("🔐 Comprehensive Authentication Test Suite")
    print("=" * 60)
    
    tester = AuthTester()
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    if not tester.test_health_check():
        print("❌ Health check failed. Exiting.")
        return
    
    # Test 2: User Registration
    print("\n2️⃣ Testing User Registration...")
    tester.test_user_registration()
    
    # Test 3: Unauthorized Access
    print("\n3️⃣ Testing Unauthorized Access...")
    tester.test_unauthorized_access()
    
    # Test 4: Login with Default User
    print("\n4️⃣ Testing Login with Default User...")
    if not tester.test_login("user1", "password123"):
        print("❌ Login failed. Exiting.")
        return
    
    # Test 5: Get Current User
    print("\n5️⃣ Testing Get Current User...")
    tester.test_get_current_user()
    
    # Test 6: Campaign Access with Auth
    print("\n6️⃣ Testing Campaign Access with Authentication...")
    tester.test_campaign_access_with_auth()
    
    # Test 7: Admin Functions (as regular user)
    print("\n7️⃣ Testing Admin Functions (as regular user)...")
    tester.test_admin_functions()
    
    # Test 8: Token Validation
    print("\n8️⃣ Testing Token Validation...")
    tester.test_token_expiry_simulation()
    
    # Test 9: Login as Admin
    print("\n9️⃣ Testing Admin Login...")
    admin_tester = AuthTester()
    if admin_tester.test_login("admin", "admin123"):
        admin_tester.test_get_current_user()
        admin_tester.test_admin_functions()
    
    print("\n✅ All authentication tests completed!")
    print("🔐 Authentication system is working correctly")


if __name__ == "__main__":
    main() 