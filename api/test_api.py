#!/usr/bin/env python3
"""
Simple API Test Script

This script tests the basic functionality of the FastAPI backend
to ensure it's working correctly, including authentication.
"""

import requests
import time
import json
from typing import Dict, Any


def test_health_check(base_url: str = "http://localhost:8000") -> bool:
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   LLM Model: {data.get('llm_model')}")
            print(f"   OpenAI Available: {data.get('openai_available')}")
            print(f"   Authentication: {data.get('authentication', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_authentication(base_url: str = "http://localhost:8000") -> str:
    """Test authentication with default user"""
    try:
        print("🔐 Testing authentication...")
        
        # Test login
        login_data = {
            "username": "user1",
            "password": "password123"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            data=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print(f"✅ Login successful")
            print(f"   Token type: {data.get('token_type')}")
            print(f"   Token length: {len(access_token) if access_token else 0}")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None


def test_user_registration(base_url: str = "http://localhost:8000") -> bool:
    """Test user registration"""
    try:
        print("📝 Testing user registration...")
        
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User",
            "role": "user"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
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


def test_campaign_generation(base_url: str = "http://localhost:8000", access_token: str = None) -> str:
    """Test campaign generation with authentication"""
    
    if not access_token:
        print("❌ No access token provided for campaign generation")
        return None
    
    campaign_brief = {
        "product": "Test Product",
        "client": "Test Client",
        "target_audience": "Test audience for API testing",
        "goals": ["Test goal 1", "Test goal 2"],
        "key_features": ["Feature 1", "Feature 2"],
        "budget": "$1,000",
        "timeline": "1 month"
    }
    
    try:
        print("🚀 Testing campaign generation...")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(
            f"{base_url}/api/v1/campaigns/generate",
            json=campaign_brief,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            campaign_id = data.get("campaign_id")
            print(f"✅ Campaign generation started")
            print(f"   Campaign ID: {campaign_id}")
            print(f"   Status: {data.get('status')}")
            print(f"   Created by: {data.get('created_by', 'unknown')}")
            return campaign_id
        else:
            print(f"❌ Campaign generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Campaign generation error: {e}")
        return None


def test_campaign_status(base_url: str, campaign_id: str, access_token: str = None) -> bool:
    """Test campaign status endpoint with authentication"""
    if not access_token:
        print("❌ No access token provided for status check")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{base_url}/api/v1/campaigns/{campaign_id}/status",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campaign status retrieved")
            print(f"   Status: {data.get('status')}")
            if data.get('progress'):
                progress = data['progress']
                print(f"   Artifacts: {progress.get('artifacts_generated', 0)}")
                print(f"   Revisions: {progress.get('revision_count', 0)}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False


def test_list_campaigns(base_url: str = "http://localhost:8000", access_token: str = None) -> bool:
    """Test listing campaigns with authentication"""
    if not access_token:
        print("❌ No access token provided for campaign listing")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{base_url}/api/v1/campaigns",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campaign listing retrieved")
            print(f"   Total Campaigns: {data.get('total', 0)}")
            print(f"   Completed: {data.get('completed', 0)}")
            print(f"   Running: {data.get('running', 0)}")
            print(f"   Failed: {data.get('failed', 0)}")
            return True
        else:
            print(f"❌ Campaign listing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Campaign listing error: {e}")
        return False


def test_unauthorized_access(base_url: str = "http://localhost:8000") -> bool:
    """Test that unauthorized access is properly blocked"""
    try:
        print("🚫 Testing unauthorized access...")
        
        # Try to access protected endpoint without token
        response = requests.post(
            f"{base_url}/api/v1/campaigns/generate",
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


def main():
    """Run all API tests with authentication"""
    print("🧪 Testing Multi-Agent Campaign Generation API with Authentication")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    if not test_health_check(base_url):
        print("❌ Health check failed. Exiting.")
        return
    
    # Test 2: User Registration
    print("\n2️⃣ Testing User Registration...")
    test_user_registration(base_url)
    
    # Test 3: Authentication
    print("\n3️⃣ Testing Authentication...")
    access_token = test_authentication(base_url)
    if not access_token:
        print("❌ Authentication failed. Exiting.")
        return
    
    # Test 4: Unauthorized Access
    print("\n4️⃣ Testing Unauthorized Access...")
    test_unauthorized_access(base_url)
    
    # Test 5: Campaign Generation
    print("\n5️⃣ Testing Campaign Generation...")
    campaign_id = test_campaign_generation(base_url, access_token)
    if not campaign_id:
        print("❌ Campaign generation failed. Exiting.")
        return
    
    # Test 6: Campaign Status
    print("\n6️⃣ Testing Campaign Status...")
    test_campaign_status(base_url, campaign_id, access_token)
    
    # Test 7: List Campaigns
    print("\n7️⃣ Testing Campaign Listing...")
    test_list_campaigns(base_url, access_token)
    
    print("\n✅ All API tests completed!")
    print(f"📋 Campaign ID for further testing: {campaign_id}")
    print(f"🌐 API Documentation: {base_url}/docs")
    print(f"📊 Monitor campaign at: {base_url}/api/v1/campaigns/{campaign_id}/status")
    print(f"🔑 Access Token: {access_token[:20]}..." if access_token else "No token")


if __name__ == "__main__":
    main() 