"""
DynamoDB Service for Campaign Data Storage

This module handles storing and retrieving campaign metadata, state,
and progress information in Amazon DynamoDB.
"""

import os
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class DynamoDBService:
    """Service class for DynamoDB operations"""
    
    def __init__(self, table_name: str, region: str = "ca-central-1"):
        """
        Initialize DynamoDB service
        
        Args:
            table_name: DynamoDB table name
            region: AWS region
        """
        self.table_name = table_name
        self.region = region
        
        # Initialize DynamoDB client
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            self.table = self.dynamodb.Table(table_name)
            
            # Check if table exists, create if it doesn't
            self._ensure_table_exists()
            
            logger.info(f"DynamoDB service initialized successfully for table: {table_name}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please check your .env file.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB service: {e}")
            raise
    
    def _ensure_table_exists(self):
        """Ensure the DynamoDB table exists, create if it doesn't"""
        try:
            # Try to describe the table
            self.table.table_status
            logger.info(f"Table {self.table_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                # Table doesn't exist, create it
                try:
                    self._create_campaigns_table()
                    logger.info(f"Created table {self.table_name} in region {self.region}")
                except Exception as create_error:
                    logger.error(f"Failed to create table: {create_error}")
                    raise
            else:
                logger.error(f"Error checking table: {e}")
                raise
    
    def _create_campaigns_table(self):
        """Create the campaigns table with proper schema"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'campaign_id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'campaign_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'created_at',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'status',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',  # On-demand billing
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'user_campaigns_index',
                        'KeySchema': [
                            {
                                'AttributeName': 'user_id',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'created_at',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    },
                    {
                        'IndexName': 'status_created_index',
                        'KeySchema': [
                            {
                                'AttributeName': 'status',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'created_at',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ]
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            
            # Update table reference
            self.table = table
            
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise
    
    def store_campaign(self, campaign_data: Dict[str, Any]) -> bool:
        """
        Store campaign data in DynamoDB
        
        Args:
            campaign_data: Campaign data to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure required fields
            if 'campaign_id' not in campaign_data:
                raise ValueError("campaign_id is required")
            
            # Add timestamps if not present
            if 'created_at' not in campaign_data:
                campaign_data['created_at'] = datetime.now().isoformat()
            
            if 'updated_at' not in campaign_data:
                campaign_data['updated_at'] = datetime.now().isoformat()
            
            # Convert any non-serializable objects to strings
            campaign_data = self._serialize_data(campaign_data)
            
            # Store in DynamoDB
            self.table.put_item(Item=campaign_data)
            
            logger.info(f"Campaign {campaign_data['campaign_id']} stored in DynamoDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store campaign: {e}")
            return False
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve campaign data from DynamoDB
        
        Args:
            campaign_id: Unique campaign identifier
            
        Returns:
            Campaign data or None if not found
        """
        try:
            response = self.table.get_item(
                Key={'campaign_id': campaign_id}
            )
            
            if 'Item' in response:
                campaign_data = response['Item']
                # Deserialize data
                campaign_data = self._deserialize_data(campaign_data)
                return campaign_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get campaign: {e}")
            return None
    
    def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update campaign data in DynamoDB
        
        Args:
            campaign_id: Unique campaign identifier
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add update timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            # Convert updates to DynamoDB update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for key, value in updates.items():
                if key != 'campaign_id':  # Don't update the key
                    placeholder = f":{key.replace('_', '')}"
                    update_expression += f"#{key} = {placeholder}, "
                    expression_attribute_values[placeholder] = value
                    expression_attribute_names[f"#{key}"] = key
            
            # Remove trailing comma and space
            update_expression = update_expression.rstrip(", ")
            
            # Update item
            self.table.update_item(
                Key={'campaign_id': campaign_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names
            )
            
            logger.info(f"Campaign {campaign_id} updated in DynamoDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update campaign: {e}")
            return False
    
    def list_user_campaigns(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List campaigns for a specific user
        
        Args:
            user_id: User identifier
            limit: Maximum number of campaigns to return
            
        Returns:
            List of campaign data
        """
        try:
            response = self.table.query(
                IndexName='user_campaigns_index',
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            campaigns = []
            for item in response.get('Items', []):
                campaigns.append(self._deserialize_data(item))
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to list user campaigns: {e}")
            return []
    
    def list_campaigns_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List campaigns by status
        
        Args:
            status: Campaign status to filter by
            limit: Maximum number of campaigns to return
            
        Returns:
            List of campaign data
        """
        try:
            response = self.table.query(
                IndexName='status_created_index',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeValues={':status': status},
                ExpressionAttributeNames={'#status': 'status'},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            campaigns = []
            for item in response.get('Items', []):
                campaigns.append(self._deserialize_data(item))
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to list campaigns by status: {e}")
            return []
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete campaign from DynamoDB
        
        Args:
            campaign_id: Unique campaign identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.table.delete_item(
                Key={'campaign_id': campaign_id}
            )
            
            logger.info(f"Campaign {campaign_id} deleted from DynamoDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete campaign: {e}")
            return False
    
    def _serialize_data(self, data: Any) -> Any:
        """Serialize data for DynamoDB storage"""
        if isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_data(item) for item in data]
        elif isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, (int, float, str, bool)) or data is None:
            return data
        else:
            return str(data)
    
    def _deserialize_data(self, data: Any) -> Any:
        """Deserialize data from DynamoDB storage"""
        if isinstance(data, dict):
            return {k: self._deserialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._deserialize_data(item) for item in data]
        elif isinstance(data, str):
            # Try to parse as datetime
            try:
                return datetime.fromisoformat(data)
            except ValueError:
                return data
        else:
            return data
    
    def get_campaign_stats(self) -> Dict[str, Any]:
        """
        Get campaign statistics
        
        Returns:
            Dictionary with campaign statistics
        """
        try:
            # Scan table to get statistics
            response = self.table.scan(
                ProjectionExpression='campaign_id, status, created_at, execution_time'
            )
            
            total_campaigns = len(response.get('Items', []))
            status_counts = {}
            total_execution_time = 0
            completed_campaigns = 0
            
            for item in response.get('Items', []):
                status = item.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if status == 'completed' and 'execution_time' in item:
                    total_execution_time += item['execution_time']
                    completed_campaigns += 1
            
            avg_execution_time = total_execution_time / completed_campaigns if completed_campaigns > 0 else 0
            
            return {
                'total_campaigns': total_campaigns,
                'status_counts': status_counts,
                'completed_campaigns': completed_campaigns,
                'average_execution_time': round(avg_execution_time, 2),
                'total_execution_time': round(total_execution_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get campaign stats: {e}")
            return {} 