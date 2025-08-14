"""
S3 Service for Campaign Artifact Storage

This module handles uploading and managing campaign artifacts in AWS S3,
including websites, PDFs, and workflow state data.
"""

import os
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class S3Service:
    """Service class for S3 operations"""
    
    def __init__(self, bucket_name: str, region: str = "ca-central-1"):
        """
        Initialize S3 service
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region
        """
        self.bucket_name = bucket_name
        self.region = region
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # Check if bucket exists, create if it doesn't
            self._ensure_bucket_exists()
            
            logger.info(f"S3 service initialized successfully for bucket: {bucket_name}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please check your .env file.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            raise
    
    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                    logger.info(f"Created bucket {self.bucket_name} in region {self.region}")
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
    
    def upload_campaign_website(self, campaign_id: str, html_content: str) -> str:
        """
        Upload campaign website HTML to S3
        
        Args:
            campaign_id: Unique campaign identifier
            html_content: HTML content of the website
            
        Returns:
            S3 URL of the uploaded file
        """
        try:
            # Create S3 key for the website
            s3_key = f"campaigns/{campaign_id}/website/index.html"
            
            # Upload HTML content
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=html_content.encode('utf-8'),
                ContentType='text/html',
                Metadata={
                    'campaign_id': campaign_id,
                    'upload_time': datetime.now().isoformat(),
                    'content_type': 'website'
                }
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Campaign website uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload campaign website: {e}")
            raise
    
    def upload_campaign_pdf(self, campaign_id: str, pdf_file_path: str) -> str:
        """
        Upload campaign PDF to S3
        
        Args:
            campaign_id: Unique campaign identifier
            pdf_file_path: Local path to PDF file
            
        Returns:
            S3 URL of the uploaded file
        """
        try:
            # Create S3 key for the PDF
            s3_key = f"campaigns/{campaign_id}/pdf/campaign_report.pdf"
            
            # Upload PDF file
            with open(pdf_file_path, 'rb') as pdf_file:
                self.s3_client.upload_fileobj(
                    pdf_file,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': 'application/pdf',
                        'Metadata': {
                            'campaign_id': campaign_id,
                            'upload_time': datetime.now().isoformat(),
                            'content_type': 'pdf'
                        }
                    }
                )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Campaign PDF uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload campaign PDF: {e}")
            raise
    
    def upload_campaign_artifacts(self, campaign_id: str, artifacts: Dict[str, Any]) -> str:
        """
        Upload campaign artifacts (workflow state) to S3
        
        Args:
            campaign_id: Unique campaign identifier
            artifacts: Campaign artifacts and workflow state
            
        Returns:
            S3 URL of the uploaded artifacts
        """
        try:
            # Create S3 key for artifacts
            s3_key = f"campaigns/{campaign_id}/artifacts/workflow_state.json"
            
            # Convert artifacts to JSON
            artifacts_json = json.dumps(artifacts, indent=2, default=str)
            
            # Upload artifacts
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=artifacts_json.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'campaign_id': campaign_id,
                    'upload_time': datetime.now().isoformat(),
                    'content_type': 'artifacts'
                }
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Campaign artifacts uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload campaign artifacts: {e}")
            raise
    
    def upload_campaign_metadata(self, campaign_id: str, metadata: Dict[str, Any]) -> str:
        """
        Upload campaign metadata to S3
        
        Args:
            campaign_id: Unique campaign identifier
            metadata: Campaign metadata including progress, interactions, etc.
            
        Returns:
            S3 URL of the uploaded metadata
        """
        try:
            # Create S3 key for metadata
            s3_key = f"campaigns/{campaign_id}/metadata/campaign_metadata.json"
            
            # Convert metadata to JSON
            metadata_json = json.dumps(metadata, indent=2, default=str)
            
            # Upload metadata
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=metadata_json.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'campaign_id': campaign_id,
                    'upload_time': datetime.now().isoformat(),
                    'content_type': 'metadata'
                }
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Campaign metadata uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload campaign metadata: {e}")
            raise
    
    def upload_campaign_files(self, campaign_id: str, local_outputs_dir: str) -> Dict[str, str]:
        """
        Upload all campaign files from local outputs directory to S3
        
        Args:
            campaign_id: Unique campaign identifier
            local_outputs_dir: Local directory containing campaign files
            
        Returns:
            Dictionary mapping file types to S3 URLs
        """
        try:
            uploaded_urls = {}
            
            # List all files in the outputs directory for debugging
            all_files = os.listdir(local_outputs_dir) if os.path.exists(local_outputs_dir) else []
            logger.info(f"Files in {local_outputs_dir}: {all_files}")
            
            # Upload website if exists - try multiple naming patterns
            website_patterns = [
                f"{campaign_id}_campaign_website.html",
                f"{campaign_id}_website.html",
                "campaign_website.html",
                "index.html"
            ]
            
            # Also look for timestamped files (format: YYYYMMDD_HHMMSS_campaign_website.html)
            timestamp_pattern = re.compile(r'\d{8}_\d{6}_campaign_website\.html')
            timestamped_files = [f for f in all_files if timestamp_pattern.match(f)]
            if timestamped_files:
                website_patterns.extend(timestamped_files)
            
            website_uploaded = False
            for pattern in website_patterns:
                website_path = os.path.join(local_outputs_dir, pattern)
                if os.path.exists(website_path):
                    logger.info(f"Found website file: {pattern}")
                    try:
                        with open(website_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        uploaded_urls['website'] = self.upload_campaign_website(campaign_id, html_content)
                        website_uploaded = True
                        logger.info(f"Successfully uploaded website: {pattern}")
                        break
                    except Exception as e:
                        logger.error(f"Failed to upload website file {pattern}: {e}")
            
            # If no specific website file found, look for any HTML file with campaign ID
            if not website_uploaded:
                html_files = [f for f in all_files if f.endswith('.html') and campaign_id in f]
                if html_files:
                    website_path = os.path.join(local_outputs_dir, html_files[0])
                    logger.info(f"Found HTML file with campaign ID: {html_files[0]}")
                    try:
                        with open(website_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        uploaded_urls['website'] = self.upload_campaign_website(campaign_id, html_content)
                        website_uploaded = True
                        logger.info(f"Successfully uploaded HTML file: {html_files[0]}")
                    except Exception as e:
                        logger.error(f"Failed to upload HTML file {html_files[0]}: {e}")
            
            # If still no website found, look for any HTML file that might be a campaign website
            if not website_uploaded:
                html_files = [f for f in all_files if f.endswith('.html')]
                if html_files:
                    website_path = os.path.join(local_outputs_dir, html_files[0])
                    logger.info(f"Found general HTML file: {html_files[0]}")
                    try:
                        with open(website_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        uploaded_urls['website'] = self.upload_campaign_website(campaign_id, html_content)
                        website_uploaded = True
                        logger.info(f"Successfully uploaded general HTML file: {html_files[0]}")
                    except Exception as e:
                        logger.error(f"Failed to upload general HTML file {html_files[0]}: {e}")
            
            # Upload PDF if exists
            pdf_files = [f for f in all_files if f.endswith('.pdf') and campaign_id in f]
            if pdf_files:
                pdf_path = os.path.join(local_outputs_dir, pdf_files[-1])  # Get most recent PDF
                try:
                    uploaded_urls['pdf'] = self.upload_campaign_pdf(campaign_id, pdf_path)
                    logger.info(f"Successfully uploaded PDF: {pdf_files[-1]}")
                except Exception as e:
                    logger.error(f"Failed to upload PDF file {pdf_files[-1]}: {e}")
            
            logger.info(f"Uploaded {len(uploaded_urls)} campaign files to S3: {list(uploaded_urls.keys())}")
            return uploaded_urls
            
        except Exception as e:
            logger.error(f"Failed to upload campaign files: {e}")
            raise
    
    def get_campaign_files(self, campaign_id: str) -> Dict[str, str]:
        """
        Get S3 URLs for all campaign files
        
        Args:
            campaign_id: Unique campaign identifier
            
        Returns:
            Dictionary mapping file types to S3 URLs
        """
        try:
            urls = {}
            
            # Website URL
            website_key = f"campaigns/{campaign_id}/website/index.html"
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=website_key)
                urls['website'] = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{website_key}"
            except ClientError:
                pass
            
            # PDF URL
            pdf_key = f"campaigns/{campaign_id}/pdf/campaign_report.pdf"
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=pdf_key)
                urls['pdf'] = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{pdf_key}"
            except ClientError:
                pass
            
            # Artifacts URL
            artifacts_key = f"campaigns/{campaign_id}/artifacts/workflow_state.json"
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=artifacts_key)
                urls['artifacts'] = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{artifacts_key}"
            except ClientError:
                pass
            
            # Metadata URL
            metadata_key = f"campaigns/{campaign_id}/metadata/campaign_metadata.json"
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=metadata_key)
                urls['metadata'] = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{metadata_key}"
            except ClientError:
                pass
            
            return urls
            
        except Exception as e:
            logger.error(f"Failed to get campaign files: {e}")
            raise
    
    def delete_campaign_files(self, campaign_id: str) -> bool:
        """
        Delete all campaign files from S3
        
        Args:
            campaign_id: Unique campaign identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # List all objects with campaign prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=f"campaigns/{campaign_id}/")
            
            objects_to_delete = []
            for page in pages:
                if 'Contents' in page:
                    objects_to_delete.extend([{'Key': obj['Key']} for obj in page['Contents']])
            
            if objects_to_delete:
                # Delete all objects
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                logger.info(f"Deleted {len(objects_to_delete)} files for campaign {campaign_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete campaign files: {e}")
            return False 