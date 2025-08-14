"""
AWS Configuration Service

This module handles loading and managing AWS configuration settings
from environment variables for S3 and DynamoDB services.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AWSConfig:
    """AWS configuration management"""
    
    @staticmethod
    def get_s3_config() -> Dict[str, str]:
        """Get S3 configuration from environment variables"""
        return {
            'bucket_name': os.getenv('S3_BUCKET_NAME', 'campaign-outputs'),
            'region': os.getenv('S3_BUCKET_REGION', 'ca-central-1'),
            'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'default_region': os.getenv('AWS_DEFAULT_REGION', 'ca-central-1')
        }
    
    @staticmethod
    def get_dynamodb_config() -> Dict[str, str]:
        """Get DynamoDB configuration from environment variables"""
        return {
            'table_name': os.getenv('DYNAMODB_TABLE_NAME', 'campaigns'),
            'region': os.getenv('DYNAMODB_REGION', 'ca-central-1'),
            'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'default_region': os.getenv('AWS_DEFAULT_REGION', 'ca-central-1')
        }
    
    @staticmethod
    def get_aws_credentials() -> Dict[str, Optional[str]]:
        """Get AWS credentials from environment variables"""
        return {
            'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'region': os.getenv('AWS_REGION', 'ca-central-1'),
            'default_region': os.getenv('AWS_DEFAULT_REGION', 'ca-central-1')
        }
    
    @staticmethod
    def validate_aws_config() -> bool:
        """Validate that required AWS configuration is present"""
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required AWS environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file and ensure all required variables are set.")
            return False
        
        print("✅ AWS configuration validated successfully")
        return True
    
    @staticmethod
    def print_config_summary():
        """Print a summary of AWS configuration"""
        s3_config = AWSConfig.get_s3_config()
        dynamodb_config = AWSConfig.get_dynamodb_config()
        
        print("🔧 AWS Configuration Summary:")
        print(f"   S3 Bucket: {s3_config['bucket_name']} ({s3_config['region']})")
        print(f"   DynamoDB Table: {dynamodb_config['table_name']} ({dynamodb_config['region']})")
        print(f"   AWS Region: {s3_config['default_region']}")
        
        # Check if credentials are set (without exposing them)
        credentials = AWSConfig.get_aws_credentials()
        if credentials['access_key_id'] and credentials['secret_access_key']:
            print("   AWS Credentials: ✅ Configured")
        else:
            print("   AWS Credentials: ❌ Not configured")
        
        print()


def load_aws_services():
    """Load and initialize AWS services"""
    try:
        from .s3_service import S3Service
        from .dynamodb_service import DynamoDBService
        
        # Validate configuration
        if not AWSConfig.validate_aws_config():
            return None, None
        
        # Get configurations
        s3_config = AWSConfig.get_s3_config()
        dynamodb_config = AWSConfig.get_dynamodb_config()
        
        # Initialize services
        s3_service = S3Service(
            bucket_name=s3_config['bucket_name'],
            region=s3_config['region']
        )
        
        dynamodb_service = DynamoDBService(
            table_name=dynamodb_config['table_name'],
            region=dynamodb_config['region']
        )
        
        print("🚀 AWS services initialized successfully")
        AWSConfig.print_config_summary()
        
        return s3_service, dynamodb_service
        
    except Exception as e:
        print(f"❌ Failed to initialize AWS services: {e}")
        return None, None 