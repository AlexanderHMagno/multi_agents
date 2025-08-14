#!/usr/bin/env python3
"""
Test script to verify file generation and AWS storage
"""

import os
import sys
sys.path.append('.')

from src.utils.file_handlers import create_campaign_website
from src.utils.s3_service import S3Service
from src.utils.dynamodb_service import DynamoDBService

def test_file_generation():
    """Test the file generation process"""
    print("🧪 Testing File Generation Process")
    print("=" * 50)
    
    # Mock workflow result with HTML content
    mock_result = {
        'web_developer': {
            'campaign_website': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Campaign</title>
</head>
<body>
    <h1>Test Campaign Website</h1>
    <p>This is a test campaign website.</p>
</body>
</html>'''
        },
        'artifacts': {
            'strategy': 'Test strategy',
            'creative_concepts': 'Test concepts'
        }
    }
    
    # Test website generation
    print("📝 Testing website generation...")
    try:
        create_campaign_website(mock_result, "test_campaign_website.html")
        print("✅ Website generation successful")
        
        # Check if file was created
        if os.path.exists("outputs"):
            files = os.listdir("outputs")
            print(f"📁 Files in outputs directory: {files}")
        else:
            print("❌ Outputs directory not created")
            
    except Exception as e:
        print(f"❌ Website generation failed: {e}")
    
    print("\n" + "=" * 50)

def test_aws_services():
    """Test AWS services"""
    print("☁️ Testing AWS Services")
    print("=" * 50)
    
    try:
        # Test S3 service
        print("📦 Testing S3 service...")
        s3_service = S3Service("campaign-outputs", "ca-central-1")
        print("✅ S3 service initialized")
        
        # Test DynamoDB service
        print("🗄️ Testing DynamoDB service...")
        db_service = DynamoDBService("campaigns", "ca-central-1")
        print("✅ DynamoDB service initialized")
        
        # Test storing a campaign
        print("💾 Testing campaign storage...")
        test_campaign = {
            "campaign_id": "test_campaign_123",
            "user_id": "test_user",
            "campaign_name": "Test Campaign",
            "status": "completed",
            "created_at": "2025-08-14T20:00:00",
            "completed_at": "2025-08-14T20:05:00",
            "execution_time": 300.0,
            "s3_website_url": "https://example.com/website.html",
            "s3_pdf_url": "https://example.com/report.pdf",
            "s3_artifacts_url": "https://example.com/artifacts.json",
            "s3_metadata_url": "https://example.com/metadata.json",
            "campaign_brief": {"name": "Test Campaign"},
            "final_state": {"status": "completed"},
            "progress_log": {"step": "completed"},
            "agent_interactions": [{"agent": "test", "action": "completed"}]
        }
        
        db_service.store_campaign(test_campaign)
        print("✅ Test campaign stored in DynamoDB")
        
        # Verify storage
        retrieved = db_service.get_campaign("test_campaign_123")
        if retrieved:
            print("✅ Campaign retrieved from DynamoDB")
            print(f"   Campaign ID: {retrieved.get('campaign_id')}")
            print(f"   Status: {retrieved.get('status')}")
        else:
            print("❌ Campaign not found in DynamoDB")
            
    except Exception as e:
        print(f"❌ AWS service test failed: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_file_generation()
    test_aws_services()
    print("🎯 Test completed!") 