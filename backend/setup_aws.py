#!/usr/bin/env python3
"""
AWS Setup Script for Campaign Storage

This script helps configure and test AWS S3 and DynamoDB services
for the campaign generation system.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("🔐 Checking AWS credentials...")
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not access_key or not secret_key:
        print("❌ AWS credentials not found!")
        print("Please set the following environment variables:")
        print("  AWS_ACCESS_KEY_ID=your_access_key")
        print("  AWS_SECRET_ACCESS_KEY=your_secret_key")
        return False
    
    print("✅ AWS credentials found")
    return True

def check_aws_config():
    """Check AWS configuration"""
    print("\n🔧 Checking AWS configuration...")
    
    config_vars = {
        'AWS_REGION': os.getenv('AWS_REGION', 'ca-central-1'),
        'S3_BUCKET_NAME': os.getenv('S3_BUCKET_NAME', 'campaign-outputs'),
        'S3_BUCKET_REGION': os.getenv('S3_BUCKET_REGION', 'ca-central-1'),
        'DYNAMODB_TABLE_NAME': os.getenv('DYNAMODB_TABLE_NAME', 'campaigns'),
        'DYNAMODB_REGION': os.getenv('DYNAMODB_REGION', 'ca-central-1')
    }
    
    print("Configuration:")
    for key, value in config_vars.items():
        print(f"  {key}: {value}")
    
    return True

def test_aws_services():
    """Test AWS services"""
    print("\n🧪 Testing AWS services...")
    
    try:
        # Test S3 service
        from src.utils.s3_service import S3Service
        s3_config = {
            'bucket_name': os.getenv('S3_BUCKET_NAME', 'campaign-outputs'),
            'region': os.getenv('S3_BUCKET_REGION', 'ca-central-1')
        }
        
        print(f"  Testing S3 service...")
        s3_service = S3Service(**s3_config)
        print(f"  ✅ S3 service initialized successfully")
        
        # Test DynamoDB service
        from src.utils.dynamodb_service import DynamoDBService
        dynamodb_config = {
            'table_name': os.getenv('DYNAMODB_TABLE_NAME', 'campaigns'),
            'region': os.getenv('DYNAMODB_REGION', 'ca-central-1')
        }
        
        print(f"  Testing DynamoDB service...")
        dynamodb_service = DynamoDBService(**dynamodb_config)
        print(f"  ✅ DynamoDB service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AWS service test failed: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Creating .env file...")
    
    if os.path.exists('.env'):
        print("  .env file already exists")
        return True
    
    env_template = """# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=ca-central-1
AWS_DEFAULT_REGION=ca-central-1

# S3 Configuration
S3_BUCKET_NAME=campaign-outputs
S3_BUCKET_REGION=ca-central-1

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=campaigns
DYNAMODB_REGION=ca-central-1

# Application Configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4
MAX_WORKFLOW_DURATION=300
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_template)
        print("  ✅ .env file created successfully")
        print("  Please edit .env with your actual AWS credentials")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create .env file: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        import boto3
        print("  ✅ boto3 already installed")
    except ImportError:
        print("  Installing boto3...")
        os.system("pip install boto3 botocore python-dotenv")
        print("  ✅ Dependencies installed")
    
    return True

def main():
    """Main setup function"""
    print("🚀 AWS Setup for Campaign Storage System")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('src/utils/aws_config.py'):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file if it doesn't exist
    create_env_file()
    
    # Check AWS credentials
    if not check_aws_credentials():
        print("\n❌ Setup incomplete. Please configure AWS credentials and run again.")
        print("\nNext steps:")
        print("1. Edit .env file with your AWS credentials")
        print("2. Run this script again")
        sys.exit(1)
    
    # Check configuration
    check_aws_config()
    
    # Test AWS services
    if test_aws_services():
        print("\n🎉 AWS setup completed successfully!")
        print("\nYour campaign system is now configured to:")
        print("  ☁️ Store campaign websites in S3 bucket: outputs")
        print("  🗄️ Store campaign metadata in DynamoDB table: campaigns")
        print("  🔄 Automatically upload completed campaigns to AWS")
        print("  📊 Access campaigns from anywhere via S3 URLs")
    else:
        print("\n❌ AWS setup failed. Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 