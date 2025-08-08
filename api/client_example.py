"""
Client Example for Multi-Agent Campaign Generation API

This script demonstrates how to use the FastAPI backend to generate campaigns.
It shows how to authenticate, submit campaign briefs, check status, and download results.
"""

import requests
import time
import json
from typing import Dict, Any, Optional


class CampaignAPIClient:
    """Client for interacting with the Campaign Generation API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
    
    def login(self, username: str, password: str) -> bool:
        """Login and get access token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                print(f"✅ Login successful for user: {username}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def register(self, username: str, email: str, password: str, full_name: str = None) -> bool:
        """Register a new user account"""
        try:
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": "user"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Registration successful for user: {data['username']}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get user info: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Get user info error: {e}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    def generate_campaign(self, campaign_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a campaign brief for generation (requires authentication)"""
        if not self.access_token:
            raise Exception("Not authenticated. Call login() first.")
        
        response = self.session.post(
            f"{self.base_url}/api/v1/campaigns/generate",
            json=campaign_brief
        )
        response.raise_for_status()
        return response.json()
    
    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign status and progress (requires authentication)"""
        if not self.access_token:
            raise Exception("Not authenticated. Call login() first.")
        
        response = self.session.get(f"{self.base_url}/api/v1/campaigns/{campaign_id}/status")
        response.raise_for_status()
        return response.json()
    
    def get_campaign_results(self, campaign_id: str) -> Dict[str, Any]:
        """Get complete campaign results (requires authentication)"""
        if not self.access_token:
            raise Exception("Not authenticated. Call login() first.")
        
        response = self.session.get(f"{self.base_url}/api/v1/campaigns/{campaign_id}")
        response.raise_for_status()
        return response.json()
    
    def download_website(self, campaign_id: str, filename: str = None) -> bool:
        """Download the generated campaign website (requires authentication)"""
        if not self.access_token:
            print("❌ Not authenticated. Call login() first.")
            return False
        
        if filename is None:
            filename = f"{campaign_id}_campaign_website.html"
        
        response = self.session.get(f"{self.base_url}/api/v1/campaigns/{campaign_id}/website")
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Website downloaded as {filename}")
            return True
        else:
            print(f"❌ Failed to download website: {response.status_code}")
            return False
    
    def download_pdf(self, campaign_id: str, filename: str = None) -> bool:
        """Download the generated campaign PDF (requires authentication)"""
        if not self.access_token:
            print("❌ Not authenticated. Call login() first.")
            return False
        
        if filename is None:
            filename = f"{campaign_id}_campaign_report.pdf"
        
        response = self.session.get(f"{self.base_url}/api/v1/campaigns/{campaign_id}/pdf")
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF downloaded as {filename}")
            return True
        else:
            print(f"❌ Failed to download PDF: {response.status_code}")
            return False
    
    def list_campaigns(self) -> Dict[str, Any]:
        """List all campaigns (requires authentication)"""
        if not self.access_token:
            raise Exception("Not authenticated. Call login() first.")
        
        response = self.session.get(f"{self.base_url}/api/v1/campaigns")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, campaign_id: str, timeout: int = 300, check_interval: int = 5) -> bool:
        """
        Wait for campaign generation to complete
        
        Args:
            campaign_id: Campaign ID to monitor
            timeout: Maximum time to wait in seconds
            check_interval: How often to check status in seconds
            
        Returns:
            bool: True if completed successfully, False if failed or timed out
        """
        start_time = time.time()
        
        print(f"⏳ Waiting for campaign {campaign_id} to complete...")
        
        while time.time() - start_time < timeout:
            try:
                status = self.get_campaign_status(campaign_id)
                
                if status["status"] == "completed":
                    print(f"✅ Campaign {campaign_id} completed successfully!")
                    return True
                elif status["status"] == "failed":
                    print(f"❌ Campaign {campaign_id} failed!")
                    return False
                elif status["status"] == "running":
                    progress = status.get("progress", {})
                    artifacts = progress.get("artifacts_generated", 0)
                    revisions = progress.get("revision_count", 0)
                    elapsed = progress.get("execution_time", 0)
                    
                    print(f"🔄 Campaign {campaign_id} running... "
                          f"Artifacts: {artifacts}, Revisions: {revisions}, "
                          f"Elapsed: {elapsed:.1f}s")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
                time.sleep(check_interval)
        
        print(f"⏰ Timeout reached for campaign {campaign_id}")
        return False


def main():
    """Example usage of the Campaign API Client with authentication"""
    
    # Initialize client
    client = CampaignAPIClient()
    
    try:
        # Check API health
        print("🔍 Checking API health...")
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"🔧 LLM Model: {health['llm_model']}")
        print(f"🎨 OpenAI Available: {health['openai_available']}")
        print(f"🔐 Authentication: {health.get('authentication', 'unknown')}")
        
        # Login with default user
        print("\n🔐 Authenticating...")
        if not client.login("user1", "password123"):
            print("❌ Authentication failed. Exiting.")
            return
        
        # Get current user info
        user_info = client.get_current_user()
        if user_info:
            print(f"👤 Logged in as: {user_info['username']} ({user_info['role']})")
        
        # Example campaign brief
        campaign_brief = {
            "product": "AI-Powered Marketing Analytics Platform",
            "client": "DataFlow Analytics",
            "client_website": "https://dataflowanalytics.com",
            "client_logo": "https://placehold.co/200x100?text=DataFlow+Analytics",
            "color_scheme": "blue and white with modern gradients",
            "target_audience": "Marketing professionals and agencies looking for data-driven insights",
            "goals": [
                "Increase platform adoption",
                "Generate qualified leads",
                "Establish thought leadership"
            ],
            "key_features": [
                "Real-time campaign analytics",
                "AI-powered insights",
                "Multi-platform integration",
                "Custom reporting dashboard"
            ],
            "budget": "$10,000",
            "timeline": "4 months",
            "additional_requirements": "Focus on B2B marketing, emphasize ROI and efficiency gains"
        }
        
        # Submit campaign for generation
        print("\n🚀 Submitting campaign brief...")
        response = client.generate_campaign(campaign_brief)
        campaign_id = response["campaign_id"]
        print(f"✅ Campaign submitted! ID: {campaign_id}")
        print(f"👤 Created by: {response.get('created_by', 'unknown')}")
        
        # Wait for completion
        if client.wait_for_completion(campaign_id, timeout=600):  # 10 minutes timeout
            # Get final results
            results = client.get_campaign_results(campaign_id)
            print(f"\n📊 Campaign Results:")
            print(f"   - Status: {results['status']}")
            print(f"   - Created by: {results.get('created_by', 'unknown')}")
            print(f"   - Execution Time: {results.get('execution_time', 0):.2f}s")
            print(f"   - Quality Score: {results.get('quality_score', 0)}")
            print(f"   - Revisions: {results.get('revision_count', 0)}")
            print(f"   - Artifacts Generated: {len(results.get('artifacts', {}))}")
            
            # Download outputs
            print(f"\n📥 Downloading outputs...")
            client.download_website(campaign_id)
            client.download_pdf(campaign_id)
            
            # Display some artifacts
            artifacts = results.get('artifacts', {})
            if 'strategy' in artifacts:
                print(f"\n📋 Strategy Preview:")
                strategy = artifacts['strategy']
                if hasattr(strategy, 'content'):
                    print(strategy.content[:200] + "...")
                else:
                    print(str(strategy)[:200] + "...")
            
            if 'campaign_summary' in artifacts:
                print(f"\n📝 Campaign Summary Preview:")
                summary = artifacts['campaign_summary']
                if hasattr(summary, 'content'):
                    print(summary.content[:200] + "...")
                else:
                    print(str(summary)[:200] + "...")
        
        else:
            print("❌ Campaign generation failed or timed out")
        
        # List all campaigns
        print(f"\n📋 Campaign History:")
        campaigns = client.list_campaigns()
        print(f"   - Total Campaigns: {campaigns['total']}")
        print(f"   - Completed: {campaigns['completed']}")
        print(f"   - Running: {campaigns['running']}")
        print(f"   - Failed: {campaigns['failed']}")
        
        # Show campaign details
        if campaigns['campaigns']:
            print(f"\n📋 Your Campaigns:")
            for campaign in campaigns['campaigns'][:3]:  # Show first 3
                print(f"   - {campaign['campaign_id']}: {campaign['status']} (by {campaign.get('created_by', 'unknown')})")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
        print("💡 Start the server with: python api/start_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_registration():
    """Demonstrate user registration"""
    print("\n" + "="*50)
    print("🔐 DEMO: User Registration")
    print("="*50)
    
    client = CampaignAPIClient()
    
    # Register a new user
    print("📝 Registering new user...")
    if client.register("demo_user", "demo@example.com", "demo123", "Demo User"):
        print("✅ Registration successful!")
        
        # Login with new user
        print("🔐 Logging in with new user...")
        if client.login("demo_user", "demo123"):
            print("✅ Login successful!")
            
            # Get user info
            user_info = client.get_current_user()
            if user_info:
                print(f"👤 User info: {user_info['username']} ({user_info['role']})")
        else:
            print("❌ Login failed!")
    else:
        print("❌ Registration failed!")


if __name__ == "__main__":
    # Run main example
    main()
    
    # Run registration demo
    demo_registration() 