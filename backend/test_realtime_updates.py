#!/usr/bin/env python3
"""
Test script for real-time campaign updates

This script tests the new real-time progress tracking functionality
by monitoring a campaign generation process.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "user1"
PASSWORD = "password123"

def login():
    """Login and get access token"""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def create_campaign(token):
    """Create a new campaign"""
    headers = {"Authorization": f"Bearer {token}"}
    
    campaign_brief = {
        "product": "Test Product",
        "client": "Test Client",
        "target_audience": "Test Audience",
        "goals": ["Increase awareness", "Generate leads"],
        "key_features": ["Feature 1", "Feature 2"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/campaigns/generate",
        json=campaign_brief,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Campaign created: {result['campaign_id']}")
        return result['campaign_id']
    else:
        print(f"❌ Campaign creation failed: {response.status_code} - {response.text}")
        return None

def monitor_progress(token, campaign_id, duration=60):
    """Monitor campaign progress for specified duration"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Monitoring campaign {campaign_id} for {duration} seconds...")
    print("=" * 60)
    
    start_time = time.time()
    last_progress = None
    
    while time.time() - start_time < duration:
        try:
            # Get progress
            response = requests.get(
                f"{BASE_URL}/api/v1/campaigns/{campaign_id}/progress",
                headers=headers
            )
            
            if response.status_code == 200:
                progress = response.json()
                current_progress = progress['progress']
                
                # Only print if progress changed
                progress_key = f"{current_progress['step']}_{current_progress['completed_steps']}"
                if progress_key != last_progress:
                    last_progress = progress_key
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] Step: {current_progress['step_name']}")
                    print(f"         Progress: {current_progress['completed_steps']}/{current_progress['total_steps']} ({current_progress['progress_percentage']}%)")
                    print(f"         Status: {current_progress['step_description']}")
                    
                    # Show recent interactions
                    interactions = progress.get('agent_interactions', [])
                    if interactions:
                        latest = interactions[-1]
                        print(f"         Latest: {latest['agent']} - {latest['action']} - {latest['message']}")
                    
                    print("-" * 40)
                
                # Check if completed
                if progress['status'] in ['completed', 'failed']:
                    print(f"🎯 Campaign {progress['status']}!")
                    break
                    
            else:
                print(f"❌ Failed to get progress: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error monitoring progress: {e}")
        
        time.sleep(2)  # Check every 2 seconds
    
    print("=" * 60)
    print("Monitoring completed")

def test_workflow_steps(token, campaign_id):
    """Test the workflow steps endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📋 Testing workflow steps endpoint...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/campaigns/{campaign_id}/workflow-steps",
        headers=headers
    )
    
    if response.status_code == 200:
        steps = response.json()
        print(f"✅ Workflow steps retrieved successfully")
        print(f"   Total steps: {steps['workflow_stats']['total_steps']}")
        print(f"   Completed: {steps['workflow_stats']['completed']}")
        print(f"   Running: {steps['workflow_stats']['running']}")
        print(f"   Failed: {steps['workflow_stats']['failed']}")
        print(f"   Completion: {steps['workflow_stats']['completion_percentage']}%")
        
        # Show current step
        for step in steps['workflow_steps']:
            if step['status'] == 'running':
                print(f"   🚀 Currently running: {step['name']}")
                break
    else:
        print(f"❌ Failed to get workflow steps: {response.status_code} - {response.text}")

def main():
    """Main test function"""
    print("🧪 Testing Real-Time Campaign Updates")
    print("=" * 60)
    
    # Login
    print("🔐 Logging in...")
    token = login()
    if not token:
        return
    
    print(f"✅ Logged in successfully")
    
    # Create campaign
    print("\n🚀 Creating campaign...")
    campaign_id = create_campaign(token)
    if not campaign_id:
        return
    
    # Monitor progress
    monitor_progress(token, campaign_id, duration=300)  # Monitor for 5 minutes (300 seconds)
    
    # Test workflow steps
    test_workflow_steps(token, campaign_id)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 