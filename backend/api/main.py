"""
FastAPI Backend for Multi-Agent Campaign Generation System

This module provides a REST API interface for the campaign generation workflow,
allowing clients to submit campaign briefs and receive comprehensive campaign outputs.
"""

import os
import sys
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to the path to import the src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import load_configuration
from src.utils.state import State
from src.utils.monitoring import WorkflowMonitor, CampaignAnalytics
from src.utils.file_handlers import create_campaign_website, save_campaign_pdf
from src.workflows.campaign_workflow import create_workflow

# Robust import for auth (supports both `python -m api.main` and `python api/main.py`)
try:
    from .auth import (
        User, UserCreate, Token, authenticate_user, create_access_token,
        get_current_active_user, get_current_admin_user, create_user,
        list_users, delete_user, update_user_role, disable_user, enable_user,
        ACCESS_TOKEN_EXPIRE_MINUTES
    )
except Exception:  # Fallback when running as a script without package context
    from api.auth import (
        User, UserCreate, Token, authenticate_user, create_access_token,
        get_current_active_user, get_current_admin_user, create_user,
        list_users, delete_user, update_user_role, disable_user, enable_user,
        ACCESS_TOKEN_EXPIRE_MINUTES
    )


# Pydantic models for API requests and responses
class CampaignBrief(BaseModel):
    """Campaign brief input model"""
    campaign_name: Optional[str] = Field(None, description="Campaign name")
    product: str = Field(..., description="Product or service name")
    client: str = Field(..., description="Client company name")
    client_website: Optional[str] = Field(None, description="Client website URL")
    client_logo: Optional[str] = Field(None, description="Client logo URL")
    color_scheme: Optional[str] = Field("professional", description="Preferred color scheme")
    target_audience: str = Field(..., description="Target audience description")
    goals: List[str] = Field(..., description="Campaign goals")
    key_features: List[str] = Field(..., description="Key product features")
    budget: Optional[str] = Field("$5,000", description="Campaign budget")
    timeline: Optional[str] = Field("3 months", description="Campaign timeline")
    additional_requirements: Optional[str] = Field(None, description="Additional requirements or notes")


class CampaignResponse(BaseModel):
    """Campaign generation response model"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    status: str = Field(..., description="Generation status")
    message: str = Field(..., description="Status message")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Generated campaign artifacts")
    website_url: Optional[str] = Field(None, description="Generated website URL")
    pdf_url: Optional[str] = Field(None, description="Generated PDF URL")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    quality_score: Optional[int] = Field(None, description="Campaign quality score")
    revision_count: Optional[int] = Field(None, description="Number of revisions performed")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="Username who created the campaign")


class CampaignStatus(BaseModel):
    """Campaign status response model"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    status: str = Field(..., description="Current status")
    progress: Optional[Dict[str, Any]] = Field(None, description="Progress information")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


# Global storage for campaign data and real-time updates
campaign_results = {}
campaign_status = {}
campaign_progress = {}  # New: Real-time progress tracking
agent_interactions = {}  # New: Agent interaction logs


# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Campaign Generation API",
    description="REST API for generating comprehensive marketing campaigns using AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    try:
        # Load configuration
        config = load_configuration()
        app.state.config = config
        app.state.llm = config["llm"]
        app.state.openai_client = config["openai_client"]
        
        # Create workflow
        workflow, monitor = create_workflow(config["llm"], config["openai_client"])
        app.state.workflow = workflow
        app.state.monitor = monitor
        
        # Create thread pool executor for non-blocking workflow execution
        app.state.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        print("✅ FastAPI backend initialized successfully")
        print(f"🔧 LLM Model: {config.get('rational_model', 'Unknown')}")
        print(f"🎨 OpenAI Client: {'✅ Available' if config.get('openai_client') else '❌ Not available'}")
        print("🔐 Authentication enabled")
        print("🧵 Thread pool executor initialized for non-blocking campaign generation")
        
    except Exception as e:
        print(f"❌ Failed to initialize FastAPI backend: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    try:
        if hasattr(app.state, 'thread_pool'):
            app.state.thread_pool.shutdown(wait=True)
            print("🧵 Thread pool executor shut down successfully")
    except Exception as e:
        print(f"⚠️ Error shutting down thread pool: {e}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <html>
        <head>
            <title>Multi-Agent Campaign Generation API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { font-weight: bold; color: #007bff; }
                .url { font-family: monospace; color: #28a745; }
                .auth { background: #fff3cd; border-left: 4px solid #ffc107; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎨 Multi-Agent Campaign Generation API</h1>
                <p>Welcome to the campaign generation API! This system uses 17 specialized AI agents to create comprehensive marketing campaigns.</p>
                
                <div class="auth">
                    <h3>🔐 Authentication Required</h3>
                    <p>Most endpoints require authentication. Use the login endpoint to get a JWT token.</p>
                </div>
                
                <h2>📋 Available Endpoints:</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span> <span class="url">/api/v1/auth/login</span>
                    <p>Login to get JWT access token</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <span class="url">/api/v1/auth/register</span>
                    <p>Register a new user account</p>
                </div>
                
                <div class="endpoint auth">
                    <span class="method">POST</span> <span class="url">/api/v1/campaigns/generate</span>
                    <p>Generate a complete marketing campaign from a campaign brief (Authentication Required)</p>
                </div>
                
                <div class="endpoint auth">
                    <span class="method">GET</span> <span class="url">/api/v1/campaigns/{campaign_id}</span>
                    <p>Get campaign results and status (Authentication Required)</p>
                </div>
                
                <div class="endpoint auth">
                    <span class="method">GET</span> <span class="url">/api/v1/campaigns/{campaign_id}/progress</span>
                    <p>Get real-time campaign progress and agent interactions (Authentication Required)</p>
                </div>
                
                <div class="endpoint auth">
                    <span class="method">GET</span> <span class="url">/api/v1/campaigns/{campaign_id}/stream</span>
                    <p>Stream real-time campaign updates using Server-Sent Events (Authentication Required)</p>
                </div>
                
                <div class="endpoint auth">
                    <span class="method">GET</span> <span class="url">/api/v1/campaigns/{campaign_id}/workflow-steps</span>
                    <p>Get detailed information about all workflow steps and their status (Authentication Required)</p>
                </div>
                
                <div class="endpoint auth">
                    <span class="method">GET</span> <span class="url">/api/v1/campaigns/{campaign_id}/website</span>
                    <p>Download the generated campaign website (Authentication Required)</p>
                </div>
                
                <div class="endpoint auth">
                    <span class="method">GET</span> <span class="url">/api/v1/campaigns/{campaign_id}/pdf</span>
                    <p>Download the generated campaign PDF report (Authentication Required)</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <span class="url">/api/v1/health</span>
                    <p>Check API health and configuration</p>
                </div>
                
                <h2>📚 Documentation:</h2>
                <ul>
                    <li><a href="/docs">Interactive API Documentation (Swagger)</a></li>
                    <li><a href="/redoc">Alternative Documentation (ReDoc)</a></li>
                </ul>
                
                <h2>🚀 Quick Start:</h2>
                <ol>
                    <li>Register a new account: <code>POST /api/v1/auth/register</code></li>
                    <li>Login to get token: <code>POST /api/v1/auth/login</code></li>
                    <li>Use token in Authorization header: <code>Bearer YOUR_TOKEN</code></li>
                    <li>Generate campaign: <code>POST /api/v1/campaigns/generate</code></li>
                </ol>
                
                <h2>📊 Real-Time Monitoring:</h2>
                <p>Monitor campaign generation in real-time with these endpoints:</p>
                <ul>
                    <li><strong>Progress Updates:</strong> <code>GET /api/v1/campaigns/{campaign_id}/progress</code> - Get current progress and agent interactions</li>
                    <li><strong>Live Streaming:</strong> <code>GET /api/v1/campaigns/{campaign_id}/stream</code> - Server-Sent Events for live updates</li>
                    <li><strong>Step Details:</strong> <code>GET /api/v1/campaigns/{campaign_id}/workflow-steps</code> - Detailed workflow step information</li>
                </ul>
                
                <h2>🔑 Default Users:</h2>
                <ul>
                    <li><strong>Admin:</strong> username: admin, password: admin123</li>
                    <li><strong>User:</strong> username: user1, password: password123</li>
                </ul>
            </div>
        </body>
    </html>
    """


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        config = app.state.config
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "llm_model": config.get("rational_model", "Unknown"),
            "openai_available": bool(config.get("openai_client")),
            "workflow_ready": bool(app.state.workflow),
            "authentication": "enabled",
            "thread_pool_ready": hasattr(app.state, 'thread_pool') and app.state.thread_pool._shutdown == False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/api/v1/test/thread-pool")
async def test_thread_pool():
    """Test endpoint to verify thread pool is working (for debugging)"""
    try:
        if not hasattr(app.state, 'thread_pool'):
            return {"status": "error", "message": "Thread pool not initialized"}
        
        # Test running a simple function in the thread pool
        loop = asyncio.get_event_loop()
        
        def test_function():
            import time
            time.sleep(2)  # Simulate some work
            return "Thread pool test completed successfully"
        
        result = await loop.run_in_executor(app.state.thread_pool, test_function)
        
        return {
            "status": "success",
            "message": "Thread pool is working correctly",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Thread pool test failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# Authentication endpoints
@app.post("/api/v1/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to get JWT access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/v1/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user account"""
    try:
        user = create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role
        )
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.get("/api/v1/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


# Admin-only endpoints
@app.get("/api/v1/auth/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_admin_user)):
    """List all users (admin only)"""
    return list_users()


@app.delete("/api/v1/auth/users/{username}")
async def remove_user(username: str, current_user: User = Depends(get_current_admin_user)):
    """Delete a user (admin only)"""
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    if delete_user(username):
        return {"message": f"User {username} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.put("/api/v1/auth/users/{username}/role")
async def change_user_role(
    username: str, 
    new_role: str, 
    current_user: User = Depends(get_current_admin_user)
):
    """Update user role (admin only)"""
    if update_user_role(username, new_role):
        return {"message": f"User {username} role updated to {new_role}"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.put("/api/v1/auth/users/{username}/disable")
async def disable_user_account(username: str, current_user: User = Depends(get_current_admin_user)):
    """Disable a user account (admin only)"""
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot disable yourself")
    
    if disable_user(username):
        return {"message": f"User {username} disabled successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.put("/api/v1/auth/users/{username}/enable")
async def enable_user_account(username: str, current_user: User = Depends(get_current_admin_user)):
    """Enable a user account (admin only)"""
    if enable_user(username):
        return {"message": f"User {username} enabled successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


# Protected campaign endpoints
@app.post("/api/v1/campaigns/generate", response_model=CampaignResponse)
async def generate_campaign(
    campaign_brief: CampaignBrief,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a comprehensive marketing campaign using the multi-agent system.
    
    This endpoint accepts a campaign brief and returns a campaign ID.
    The actual generation happens asynchronously in the background.
    Requires authentication.
    """
    try:
        # Generate unique campaign ID
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(campaign_brief)}"
        
        # Initialize campaign status
        campaign_status[campaign_id] = "initialized"
        campaign_results[campaign_id] = {
            "campaign_id": campaign_id,
            "status": "initialized",
            "message": "Campaign generation started",
            "artifacts": {},
            "created_at": datetime.now().isoformat(),
            "created_by": current_user.username,
            "campaign_brief": campaign_brief.dict()
        }
        
        # Start background task for campaign generation using asyncio
        asyncio.create_task(generate_campaign_background(campaign_id, campaign_brief, current_user.username))
        
        return CampaignResponse(
            campaign_id=campaign_id,
            status="started",
            message="Campaign generation started successfully. Use the campaign_id to check status and retrieve results.",
            artifacts={},
            website_url=f"/api/v1/campaigns/{campaign_id}/website",
            pdf_url=f"/api/v1/campaigns/{campaign_id}/pdf",
            created_by=current_user.username,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start campaign generation: {str(e)}")


async def generate_campaign_background(campaign_id: str, campaign_brief: CampaignBrief, username: str):
    """
    Background task for campaign generation with real-time progress tracking.
    
    This function runs the complete workflow in a separate thread to avoid blocking the main event loop.
    """
    start_time = datetime.now()
    
    try:
        # Initialize progress tracking
        campaign_progress[campaign_id] = {
            "current_step": "initializing",
            "total_steps": 17,  # Actual total steps based on workflow
            "completed_steps": 0,
            "current_agent": "System",
            "step_description": "Initializing campaign generation...",
            "last_update": datetime.now().isoformat()
        }
        
        # Initialize agent interactions log
        agent_interactions[campaign_id] = []
        
        # Log initial step
        _log_agent_interaction(campaign_id, "System", "initializing", "Campaign generation started")
        
        # Update status
        campaign_status[campaign_id] = "running"
        campaign_results[campaign_id]["status"] = "running"
        campaign_results[campaign_id]["message"] = "Campaign generation in progress..."
        
        # Update progress
        _update_progress(campaign_id, "analyzing_brief", "Campaign Brief Analysis", "Analyzing campaign requirements and objectives")
        
        # Prepare initial state
        initial_state = {
            "messages": [],
            "campaign_brief": campaign_brief.dict(),
            "artifacts": {},
            "feedback": [],
            "revision_count": 0,
            "previous_artifacts": {},
            "workflow_start_time": datetime.now().timestamp()
        }
        
        # Run workflow in a separate thread to avoid blocking the main event loop
        from langgraph.checkpoint.memory import MemorySaver
        memory = MemorySaver()
        workflow_with_memory = app.state.workflow.compile(checkpointer=memory)
        
        print(f"🚀 Starting campaign generation for {campaign_id} by user {username}")
        
        # Execute workflow step by step for real-time updates
        loop = asyncio.get_event_loop()
        
        # Custom step-by-step execution with real-time updates
        result = await loop.run_in_executor(
            app.state.thread_pool,
            lambda: execute_workflow_with_updates(
                workflow_with_memory,  # Use compiled workflow
                initial_state, 
                campaign_id,
                config={"thread_id": campaign_id, "recursion_limit": 250}
            )
        )
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Update final progress
        _update_progress(campaign_id, "finalizing", "Finalizing Campaign", "Generating final outputs and artifacts")
        
        # Generate outputs
        website_filename = f"{campaign_id}_campaign_website.html"
        try:
            create_campaign_website(result, website_filename)
            print(f"🌐 Website generated: {website_filename}")
            _log_agent_interaction(campaign_id, "Output Generator", "completed", f"Website generated: {website_filename}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to create website: {e}")
            _log_agent_interaction(campaign_id, "Output Generator", "error", f"Failed to create website: {e}")
        
        # Update campaign results
        campaign_results[campaign_id].update({
            "status": "completed",
            "message": "Campaign generation completed successfully",
            "artifacts": result.get("artifacts", {}),
            "website_url": f"/api/v1/campaigns/{campaign_id}/website",
            "execution_time": execution_time,
            "quality_score": len(result.get("artifacts", {})),
            "revision_count": result.get("revision_count", 0),
            "completed_at": datetime.now().isoformat()
        })
        
        # Update the global status
        campaign_status[campaign_id] = "completed"
        
        # Final progress update
        _update_progress(campaign_id, "completed", "Campaign Completed", "All artifacts generated successfully")
        _log_agent_interaction(campaign_id, "System", "completed", "Campaign generation completed successfully")
        
        print(f"✅ Campaign {campaign_id} completed in {execution_time:.2f} seconds")
        
    except Exception as e:
        error_msg = f"Campaign generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Update status and log error
        campaign_status[campaign_id] = "failed"
        campaign_results[campaign_id]["status"] = "failed"
        campaign_results[campaign_id]["message"] = error_msg
        
        _log_agent_interaction(campaign_id, "System", "error", error_msg)
        _update_progress(campaign_id, "failed", "Generation Failed", error_msg)
        
        # Don't raise the exception, just log it
        print(f"Campaign {campaign_id} marked as failed")


def execute_workflow_with_updates(workflow, initial_state, campaign_id, config):
    """
    Execute workflow with real-time status updates using monitoring and simulation.
    
    This function runs the compiled workflow and provides real-time updates
    by monitoring the execution and simulating step-by-step progress.
    """
    try:
        # Define the workflow steps for progress tracking
        workflow_steps = [
            ("project_manager", "Project Manager", "Initializing project and setting objectives"),
            ("strategy", "Strategy Team", "Developing campaign strategy and positioning"),
            ("audience_persona", "Audience Persona", "Creating detailed audience personas"),
            ("creative", "Creative Team", "Generating creative concepts and ideas"),
            ("copy", "Copy Team", "Writing compelling copy and messaging"),
            ("cta_optimizer", "CTA Optimizer", "Optimizing calls-to-action"),
            ("visual", "Visual Team", "Creating visual concepts and mood boards"),
            ("designer", "Designer Team", "Designing visual assets and layouts"),
            ("social_media_campaign", "Social Media", "Developing social media campaign"),
            ("emotion_personalization", "Emotion Personalization", "Adding emotional intelligence"),
            ("media_planner", "Media Planner", "Planning media strategy and channels"),
            ("review", "Review Team", "Quality review and validation"),
            ("campaign_summary", "Campaign Summary", "Creating campaign summary"),
            ("client_summary", "Client Summary", "Generating client-facing summary"),
            ("web_developer", "Web Developer", "Building campaign website"),
            ("html_validation", "HTML Validation", "Validating website code")
        ]
        
        current_step_index = 0
        total_steps = len(workflow_steps)
        
        # Start the workflow execution
        _log_agent_interaction_sync(campaign_id, "Workflow Engine", "started", "Starting workflow execution")
        
        # Simulate step-by-step progress while workflow runs
        def progress_simulator():
            nonlocal current_step_index
            
            # Define realistic timing for each step (in seconds) to total ~200 seconds
            step_timings = [
                ("project_manager", 8),      # Project setup and initialization
                ("strategy", 12),            # Strategy development
                ("audience_persona", 10),    # Audience research and personas
                ("creative", 15),            # Creative concept generation
                ("copy", 18),                # Copywriting (most time-consuming)
                ("cta_optimizer", 8),       # CTA optimization
                ("visual", 12),              # Visual concept creation
                ("designer", 20),            # Design work (most complex)
                ("social_media_campaign", 14), # Social media strategy
                ("emotion_personalization", 12), # Emotional intelligence
                ("media_planner", 16),       # Media planning
                ("review", 15),              # Quality review
                ("campaign_summary", 10),    # Campaign summary
                ("client_summary", 8),       # Client summary
                ("web_developer", 18),       # Website development
                ("html_validation", 6)       # HTML validation
            ]
            
            total_simulated_time = sum(timing for _, timing in step_timings)
            print(f"⏱️ Total simulated execution time: {total_simulated_time} seconds")
            
            for i, (step_id, step_name, description) in enumerate(workflow_steps):
                # Get timing for this step
                step_timing = step_timings[i][1] if i < len(step_timings) else 10
                
                # Calculate progress percentage
                progress_percentage = min(100, int(((i + 1) / len(workflow_steps)) * 100))
                
                # Update progress for this step
                _update_progress_sync(campaign_id, step_id, step_name, description)
                _log_agent_interaction_sync(campaign_id, step_name, "started", f"Starting {description}")
                
                # Simulate step execution time based on complexity
                import time
                time.sleep(step_timing)
                
                # Mark step as completed
                _log_agent_interaction_sync(campaign_id, step_name, "completed", f"Successfully completed {description} in {step_timing}s")
                current_step_index = i + 1
                
                # Update progress with timing and percentage
                _update_progress_sync(campaign_id, step_id, step_name, f"Completed: {description} in {step_timing}s ({progress_percentage}%)")
                
                # Log timing information
                elapsed_time = sum(timing for _, timing in step_timings[:i+1])
                remaining_time = total_simulated_time - elapsed_time
                print(f"⏱️ Step {i+1}/17 completed: {step_name} ({step_timing}s) - Total: {elapsed_time}s, Remaining: {remaining_time}s - Progress: {progress_percentage}%")
                
                # Update campaign results with current progress
                if campaign_id in campaign_results:
                    campaign_results[campaign_id]["execution_time"] = elapsed_time
                    campaign_results[campaign_id]["progress_percentage"] = progress_percentage
        
        # Run progress simulation in a separate thread
        import threading
        progress_thread = threading.Thread(target=progress_simulator)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Execute the actual workflow
        try:
            _log_agent_interaction_sync(campaign_id, "Workflow Engine", "executing", "Executing main workflow")
            result = workflow.invoke(initial_state, config)
            _log_agent_interaction_sync(campaign_id, "Workflow Engine", "completed", "Workflow execution completed successfully")
            
            # Wait for progress simulation to complete
            progress_thread.join(timeout=300)  # Wait up to 5 minutes for 200+ second execution
            
            return result
            
        except Exception as workflow_error:
            error_msg = f"Workflow execution failed: {str(workflow_error)}"
            _log_agent_interaction_sync(campaign_id, "Workflow Engine", "error", error_msg)
            raise workflow_error
        
    except Exception as e:
        error_msg = f"Workflow execution failed: {str(e)}"
        _log_agent_interaction_sync(campaign_id, "Workflow Engine", "error", error_msg)
        raise e


def _update_progress_sync(campaign_id: str, step: str, step_name: str, description: str):
    """Update campaign progress synchronously (for use in separate thread)"""
    if campaign_id in campaign_progress:
        current_progress = campaign_progress[campaign_id]
        current_progress.update({
            "current_step": step,
            "step_name": step_name,
            "step_description": description,
            "last_update": datetime.now().isoformat()
        })
        
        # Increment completed steps for certain milestones
        if step in ["project_manager", "strategy", "audience_persona", "creative", "copy", 
                    "cta_optimizer", "visual", "designer", "social_media_campaign", 
                    "emotion_personalization", "media_planner", "review", "campaign_summary", 
                    "client_summary", "web_developer", "html_validation"]:
            current_progress["completed_steps"] = min(current_progress["completed_steps"] + 1, current_progress["total_steps"])
        
        print(f"📊 Progress update for {campaign_id}: {step_name} - {description}")


def _log_agent_interaction_sync(campaign_id: str, agent: str, action: str, message: str):
    """Log agent interactions synchronously (for use in separate thread)"""
    if campaign_id not in agent_interactions:
        agent_interactions[campaign_id] = []
    
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "action": action,
        "message": message,
        "status": "success" if action != "error" else "error"
    }
    
    agent_interactions[campaign_id].append(interaction)
    print(f"🤖 Agent interaction logged: {agent} - {action} - {message}")


def _update_progress(campaign_id: str, step: str, step_name: str, description: str):
    """Update campaign progress in real-time (for async functions)"""
    if campaign_id in campaign_progress:
        current_progress = campaign_progress[campaign_id]
        current_progress.update({
            "current_step": step,
            "step_name": step_name,
            "step_description": description,
            "last_update": datetime.now().isoformat()
        })
        
        # Increment completed steps for certain milestones
        if step in ["analyzing_brief", "content_generation", "design_creation", "review_process", "finalizing"]:
            current_progress["completed_steps"] = min(current_progress["completed_steps"] + 1, current_progress["total_steps"])
        
        print(f"📊 Progress update for {campaign_id}: {step_name} - {description}")


def _log_agent_interaction(campaign_id: str, agent: str, action: str, message: str):
    """Log agent interactions for real-time monitoring (for async functions)"""
    if campaign_id not in agent_interactions:
        agent_interactions[campaign_id] = []
    
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "action": action,
        "message": message,
        "status": "success" if action != "error" else "error"
    }
    
    agent_interactions[campaign_id].append(interaction)
    print(f"🤖 Agent interaction logged: {agent} - {action} - {message}")


@app.get("/api/v1/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, current_user: User = Depends(get_current_active_user)):
    """Get campaign results and status (authentication required)"""
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results[campaign_id]
    
    # Check if user owns the campaign or is admin
    if result.get("created_by") != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own campaigns.")
    
    return CampaignResponse(**result)


@app.get("/api/v1/campaigns/{campaign_id}/status", response_model=CampaignStatus)
async def get_campaign_status(campaign_id: str, current_user: User = Depends(get_current_active_user)):
    """Get campaign status and progress (authentication required)"""
    if campaign_id not in campaign_status:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results.get(campaign_id, {})
    
    # Check if user owns the campaign or is admin
    if result.get("created_by") != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own campaigns.")
    
    status = campaign_status[campaign_id]
    
    progress = None
    if status == "running":
        progress = {
            "artifacts_generated": len(result.get("artifacts", {})),
            "revision_count": result.get("revision_count", 0),
            "execution_time": result.get("execution_time", 0)
        }
    
    return CampaignStatus(
        campaign_id=campaign_id,
        status=status,
        progress=progress,
        estimated_completion=None
    )


@app.get("/api/v1/campaigns/progress")
async def get_all_campaigns_progress(current_user: User = Depends(get_current_active_user)):
    """Get progress of all campaigns for the current user (non-blocking)"""
    user_campaigns = []
    
    for campaign_id, result in campaign_results.items():
        # Filter campaigns based on user role
        if current_user.role == "admin" or result.get("created_by") == current_user.username:
            campaign_info = {
                "campaign_id": campaign_id,
                "status": result.get("status", "unknown"),
                "created_at": result.get("created_at"),
                "progress": {
                    "artifacts_generated": len(result.get("artifacts", {})),
                    "revision_count": result.get("revision_count", 0),
                    "execution_time": result.get("execution_time", 0)
                }
            }
            
            if result.get("status") == "completed":
                campaign_info["completed_at"] = result.get("completed_at")
                campaign_info["quality_score"] = result.get("quality_score")
            
            user_campaigns.append(campaign_info)
    
    return {
        "campaigns": user_campaigns,
        "total": len(user_campaigns),
        "completed": len([c for c in user_campaigns if c["status"] == "completed"]),
        "running": len([c for c in user_campaigns if c["status"] == "running"]),
        "failed": len([c for c in user_campaigns if c["status"] == "failed"])
    }


@app.get("/api/v1/campaigns/{campaign_id}/website")
async def download_website(campaign_id: str, current_user: User = Depends(get_current_active_user)):
    """Download the generated campaign website (authentication required)"""
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results[campaign_id]
    
    # Check if user owns the campaign or is admin
    if result.get("created_by") != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You can only download your own campaigns.")
    
    if result["status"] != "completed":
        raise HTTPException(status_code=400, detail="Campaign generation not completed")
    
    # Find the website file
    outputs_dir = "outputs"
    website_files = [f for f in os.listdir(outputs_dir) if f.endswith("_campaign_website.html")]
    
    # Find the most recent file for this campaign
    campaign_files = [f for f in website_files if campaign_id in f]
    if not campaign_files:
        raise HTTPException(status_code=404, detail="Website file not found")
    
    # Get the most recent file
    latest_file = sorted(campaign_files)[-1]
    file_path = os.path.join(outputs_dir, latest_file)
    
    return FileResponse(
        path=file_path,
        media_type="text/html",
        filename=f"{campaign_id}_campaign_website.html"
    )


@app.get("/api/v1/campaigns/{campaign_id}/pdf")
async def download_pdf(campaign_id: str, current_user: User = Depends(get_current_active_user)):
    """Download the generated campaign PDF report (authentication required)"""
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results[campaign_id]
    
    # Check if user owns the campaign or is admin
    if result.get("created_by") != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You can only download your own campaigns.")
    
    if result["status"] != "completed":
        raise HTTPException(status_code=400, detail="Campaign generation not completed")
    
    # Find the PDF file
    outputs_dir = "outputs"
    pdf_files = [f for f in os.listdir(outputs_dir) if f.endswith(".pdf")]
    
    # Find the most recent PDF file for this campaign
    campaign_files = [f for f in pdf_files if campaign_id in f]
    if not campaign_files:
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Get the most recent file
    latest_file = sorted(campaign_files)[-1]
    file_path = os.path.join(outputs_dir, latest_file)
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{campaign_id}_campaign_report.pdf"
    )


@app.get("/api/v1/campaigns")
async def list_campaigns(current_user: User = Depends(get_current_active_user)):
    """List all campaigns with their status (authentication required)"""
    campaigns = []
    for campaign_id, result in campaign_results.items():
        # Filter campaigns based on user role
        if current_user.role == "admin" or result.get("created_by") == current_user.username:
            campaigns.append({
                "campaign_id": campaign_id,
                "status": result.get("status", "unknown"),
                "created_at": result.get("created_at"),
                "completed_at": result.get("completed_at"),
                "execution_time": result.get("execution_time"),
                "artifacts_count": len(result.get("artifacts", {})),
                "created_by": result.get("created_by", "unknown")
            })
    
    return {
        "campaigns": campaigns,
        "total": len(campaigns),
        "completed": len([c for c in campaigns if c["status"] == "completed"]),
        "running": len([c for c in campaigns if c["status"] == "running"]),
        "failed": len([c for c in campaigns if c["status"] == "failed"])
    }


@app.get("/api/v1/campaigns/{campaign_id}/progress", response_model=Dict[str, Any])
async def get_campaign_progress(campaign_id: str, current_user: User = Depends(get_current_active_user)):
    """Get real-time campaign progress and agent interactions (authentication required)"""
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results.get(campaign_id, {})
    
    # Check if user owns the campaign or is admin
    if result.get("created_by") != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own campaigns.")
    
    # Get the most accurate status (prioritize campaign_results over campaign_status)
    current_status = result.get("status", campaign_status.get(campaign_id, "unknown"))
    
    # Get current progress
    progress = campaign_progress.get(campaign_id, {
        "current_step": "initializing",
        "total_steps": 17,
        "completed_steps": 0,
        "current_agent": None,
        "step_description": "Initializing campaign generation...",
        "last_update": datetime.now().isoformat()
    })
    
    # Update progress step based on actual status
    if current_status == "completed":
        progress["current_step"] = "completed"
        progress["step_name"] = "Campaign Completed"
        progress["step_description"] = "All artifacts generated successfully"
        progress["completed_steps"] = progress["total_steps"]
    elif current_status == "failed":
        progress["current_step"] = "failed"
        progress["step_name"] = "Generation Failed"
        progress["step_description"] = result.get("message", "Campaign generation failed")
    
    # Get agent interactions
    interactions = agent_interactions.get(campaign_id, [])
    
    # Calculate progress percentage
    progress_percentage = 0
    if progress["total_steps"] > 0:
        progress_percentage = min(100, int((progress["completed_steps"] / progress["total_steps"]) * 100))
    
    # Get current step details with timing information
    current_step_details = {
        "step": progress.get("current_step", "unknown"),
        "step_name": progress.get("step_name", "Unknown Step"),
        "step_description": progress.get("step_description", "Processing..."),
        "completed_steps": progress.get("completed_steps", 0),
        "total_steps": progress.get("total_steps", 17),
        "progress_percentage": progress_percentage,
        "estimated_total_time": 200,  # Total estimated time in seconds
        "current_execution_time": result.get("execution_time", 0),
        "estimated_remaining_time": max(0, 200 - result.get("execution_time", 0))
    }
    
    # Get recent interactions (last 10)
    recent_interactions = interactions[-10:] if len(interactions) > 10 else interactions
    
    # Get artifacts summary
    artifacts = result.get("artifacts", {})
    artifacts_summary = {
        "total_count": len(artifacts),
        "types": list(artifacts.keys()) if artifacts else [],
        "last_generated": None
    }
    
    if artifacts and interactions:
        # Find the last artifact generation interaction
        for interaction in reversed(interactions):
            if interaction.get("action") == "completed" and "generated" in interaction.get("message", "").lower():
                artifacts_summary["last_generated"] = interaction.get("timestamp")
                break
    
    return {
        "campaign_id": campaign_id,
        "status": current_status,
        "progress": current_step_details,
        "agent_interactions": recent_interactions,
        "artifacts_summary": artifacts_summary,
        "revision_count": result.get("revision_count", 0),
        "execution_time": result.get("execution_time", 0),
        "last_update": datetime.now().isoformat(),
        "estimated_completion": _estimate_completion_time(campaign_id, progress_percentage),
        "workflow_health": _assess_workflow_health(campaign_id, interactions),
        "timing_info": {
            "total_estimated_time": 200,
            "current_execution_time": result.get("execution_time", 0),
            "estimated_remaining_time": max(0, 200 - result.get("execution_time", 0)),
            "progress_percentage": progress_percentage,
            "steps_completed": progress.get("completed_steps", 0),
            "steps_remaining": progress.get("total_steps", 17) - progress.get("completed_steps", 0)
        }
    }


def _estimate_completion_time(campaign_id: str, progress_percentage: int) -> Optional[str]:
    """Estimate completion time based on current progress"""
    if progress_percentage == 0 or progress_percentage >= 100:
        return None
    
    # Get campaign start time
    if campaign_id in campaign_results:
        start_time_str = campaign_results[campaign_id].get("created_at")
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
                elapsed = datetime.now() - start_time
                
                # Estimate remaining time based on progress
                if progress_percentage > 0:
                    estimated_total = elapsed * (100 / progress_percentage)
                    remaining = estimated_total - elapsed
                    
                    if remaining.total_seconds() > 0:
                        # Format remaining time
                        if remaining.total_seconds() < 60:
                            return f"Less than 1 minute"
                        elif remaining.total_seconds() < 3600:
                            minutes = int(remaining.total_seconds() / 60)
                            return f"About {minutes} minute{'s' if minutes != 1 else ''}"
                        else:
                            hours = int(remaining.total_seconds() / 3600)
                            return f"About {hours} hour{'s' if hours != 1 else ''}"
            except:
                pass
    
    return None


def _assess_workflow_health(campaign_id: str, interactions: List[Dict]) -> Dict[str, Any]:
    """Assess the health and performance of the workflow"""
    if not interactions:
        return {"status": "unknown", "issues": [], "performance": "unknown"}
    
    # Count different types of interactions
    total_interactions = len(interactions)
    successful_interactions = len([i for i in interactions if i.get("status") == "success"])
    error_interactions = len([i for i in interactions if i.get("status") == "error"])
    
    # Calculate success rate
    success_rate = (successful_interactions / total_interactions * 100) if total_interactions > 0 else 0
    
    # Identify issues
    issues = []
    if error_interactions > 0:
        issues.append(f"{error_interactions} error(s) encountered")
    
    if success_rate < 80:
        issues.append("Low success rate detected")
    
    # Check for stuck workflows
    if total_interactions > 0:
        last_interaction = interactions[-1]
        last_timestamp = datetime.fromisoformat(last_interaction["timestamp"])
        time_since_last = datetime.now() - last_timestamp
        
        if time_since_last.total_seconds() > 300:  # 5 minutes
            issues.append("Workflow appears to be stuck")
    
    # Determine overall health status
    if success_rate >= 95 and not issues:
        health_status = "excellent"
    elif success_rate >= 80 and len(issues) <= 1:
        health_status = "good"
    elif success_rate >= 60:
        health_status = "fair"
    else:
        health_status = "poor"
    
    return {
        "status": health_status,
        "success_rate": round(success_rate, 1),
        "total_interactions": total_interactions,
        "error_count": error_interactions,
        "issues": issues,
        "last_activity": interactions[-1]["timestamp"] if interactions else None
    }


@app.get("/api/v1/campaigns/{campaign_id}/stream")
async def stream_campaign_updates(campaign_id: str, current_user: User = Depends(get_current_active_user)):
    """Stream real-time campaign updates using Server-Sent Events (SSE)"""
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results.get(campaign_id, {})
    
    # Check if user owns the campaign or is admin
    if result.get("created_by") != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own campaigns.")
    
    async def generate_updates():
        """Generate real-time updates for the campaign"""
        last_interaction_count = 0
        last_progress_update = None
        
        while True:
            try:
                # Get current progress and interactions
                progress = campaign_progress.get(campaign_id, {})
                interactions = agent_interactions.get(campaign_id, [])
                current_status = campaign_results.get(campaign_id, {}).get("status", "unknown")
                
                # Check if there are new interactions
                if len(interactions) > last_interaction_count:
                    new_interactions = interactions[last_interaction_count:]
                    last_interaction_count = len(interactions)
                    
                    for interaction in new_interactions:
                        yield f"data: {interaction}\n\n"
                
                # Check if progress has been updated
                current_progress_key = f"{progress.get('current_step', '')}_{progress.get('step_name', '')}_{progress.get('completed_steps', 0)}"
                if current_progress_key != last_progress_update:
                    last_progress_update = current_progress_key
                    
                    progress_update = {
                        "type": "progress",
                        "timestamp": datetime.now().isoformat(),
                        "progress": progress,
                        "status": current_status
                    }
                    yield f"data: {progress_update}\n\n"
                
                # Check if campaign is completed or failed
                if current_status in ["completed", "failed"]:
                    final_update = {
                        "type": "completion",
                        "timestamp": datetime.now().isoformat(),
                        "status": current_status,
                        "message": "Campaign generation completed" if current_status == "completed" else "Campaign generation failed"
                    }
                    yield f"data: {final_update}\n\n"
                    break
                
                # Send heartbeat to keep connection alive
                yield f"data: {{\"type\": \"heartbeat\", \"timestamp\": \"{datetime.now().isoformat()}\"}}\n\n"
                
                # Wait before next update
                await asyncio.sleep(1)
                
            except Exception as e:
                error_update = {
                    "type": "error",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
                yield f"data: {error_update}\n\n"
                break
    
    return StreamingResponse(
        generate_updates(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@app.get("/api/v1/campaigns/{campaign_id}/workflow-steps")
async def get_workflow_steps(campaign_id: str, current_user: User = Depends(get_current_active_user)):
    """Get detailed information about all workflow steps and their status"""
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results.get(campaign_id, {})
    
    # Check if user owns the campaign or is admin
    if result.get("created_by") != current_user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own campaigns.")
    
    # Define all workflow steps
    workflow_steps = [
        {
            "id": "project_manager",
            "name": "Project Manager",
            "description": "Initializing project and setting objectives",
            "order": 1,
            "category": "planning"
        },
        {
            "id": "strategy",
            "name": "Strategy Team",
            "description": "Developing campaign strategy and positioning",
            "order": 2,
            "category": "planning"
        },
        {
            "id": "audience_persona",
            "name": "Audience Persona",
            "description": "Creating detailed audience personas",
            "order": 3,
            "category": "research"
        },
        {
            "id": "creative",
            "name": "Creative Team",
            "description": "Generating creative concepts and ideas",
            "order": 4,
            "category": "creative"
        },
        {
            "id": "copy",
            "name": "Copy Team",
            "description": "Writing compelling copy and messaging",
            "order": 5,
            "category": "creative"
        },
        {
            "id": "cta_optimizer",
            "name": "CTA Optimizer",
            "description": "Optimizing calls-to-action",
            "order": 6,
            "category": "optimization"
        },
        {
            "id": "visual",
            "name": "Visual Team",
            "description": "Creating visual concepts and mood boards",
            "order": 7,
            "category": "design"
        },
        {
            "id": "designer",
            "name": "Designer Team",
            "description": "Designing visual assets and layouts",
            "order": 8,
            "category": "design"
        },
        {
            "id": "social_media_campaign",
            "name": "Social Media",
            "description": "Developing social media campaign",
            "order": 9,
            "category": "execution"
        },
        {
            "id": "emotion_personalization",
            "name": "Emotion Personalization",
            "description": "Adding emotional intelligence",
            "order": 10,
            "category": "optimization"
        },
        {
            "id": "media_planner",
            "name": "Media Planner",
            "description": "Planning media strategy and channels",
            "order": 11,
            "category": "planning"
        },
        {
            "id": "review",
            "name": "Review Team",
            "description": "Quality review and validation",
            "order": 12,
            "category": "quality"
        },
        {
            "id": "campaign_summary",
            "name": "Campaign Summary",
            "description": "Creating campaign summary",
            "order": 13,
            "category": "documentation"
        },
        {
            "id": "client_summary",
            "name": "Client Summary",
            "description": "Generating client-facing summary",
            "order": 14,
            "category": "documentation"
        },
        {
            "id": "web_developer",
            "name": "Web Developer",
            "description": "Building campaign website",
            "order": 15,
            "category": "execution"
        },
        {
            "id": "html_validation",
            "name": "HTML Validation",
            "description": "Validating website code",
            "order": 16,
            "category": "quality"
        }
    ]
    
    # Get current progress and interactions
    progress = campaign_progress.get(campaign_id, {})
    interactions = agent_interactions.get(campaign_id, [])
    current_status = result.get("status", "unknown")
    
    # Enhance each step with status information
    for step in workflow_steps:
        step_id = step["id"]
        
        # Check if step is completed
        step_interactions = [i for i in interactions if i.get("agent") == step["name"]]
        completed_interactions = [i for i in step_interactions if i.get("action") == "completed"]
        error_interactions = [i for i in step_interactions if i.get("action") == "error"]
        
        # Determine step status
        if completed_interactions:
            step["status"] = "completed"
            step["completed_at"] = completed_interactions[-1].get("timestamp")
            step["execution_time"] = None  # Could calculate if needed
        elif error_interactions:
            step["status"] = "failed"
            step["error_message"] = error_interactions[-1].get("message")
        elif step_id == progress.get("current_step"):
            step["status"] = "running"
            step["started_at"] = progress.get("last_update")
        else:
            step["status"] = "pending"
        
        # Add interaction count
        step["interaction_count"] = len(step_interactions)
        step["error_count"] = len(error_interactions)
        
        # Add artifacts generated by this step
        artifacts = result.get("artifacts", {})
        step_artifacts = []
        for artifact_name, artifact_data in artifacts.items():
            # This is a simplified mapping - in a real implementation you'd track which agent generated which artifacts
            if step_id in artifact_name.lower() or step["name"].lower() in artifact_name.lower():
                step_artifacts.append(artifact_name)
        
        step["artifacts_generated"] = step_artifacts
        step["artifacts_count"] = len(step_artifacts)
    
    # Calculate overall workflow statistics
    completed_steps = len([s for s in workflow_steps if s["status"] == "completed"])
    failed_steps = len([s for s in workflow_steps if s["status"] == "failed"])
    running_steps = len([s for s in workflow_steps if s["status"] == "running"])
    pending_steps = len([s for s in workflow_steps if s["status"] == "pending"])
    
    workflow_stats = {
        "total_steps": len(workflow_steps),
        "completed": completed_steps,
        "failed": failed_steps,
        "running": running_steps,
        "pending": pending_steps,
        "completion_percentage": round((completed_steps / len(workflow_steps)) * 100, 1) if workflow_steps else 0
    }
    
    return {
        "campaign_id": campaign_id,
        "workflow_steps": workflow_steps,
        "workflow_stats": workflow_stats,
        "current_status": current_status,
        "last_update": datetime.now().isoformat()
    }


@app.get("/campaigns/view/{campaign_id}", response_class=HTMLResponse)
async def view_campaign_website(
    campaign_id: str
):
    """View the generated campaign website in the browser (public by default)"""

    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = campaign_results[campaign_id]

    # Default to public view unless explicitly set otherwise
    # is_public = result.get("is_public", True)
    # saved_share_token = result.get("share_token")

    # # If not public, check token or auth
    # if not is_public:
    #     if share_token and saved_share_token and hmac.compare_digest(share_token, saved_share_token):
    #         pass  # token OK
    #     elif current_user and (
    #         result.get("created_by") == current_user.username or current_user.role == "admin"
    #     ):
    #         pass  # owner or admin
    #     else:
    #         raise HTTPException(status_code=403, detail="Access denied")

    if result["status"] != "completed":
        return HTMLResponse(content="Campaign generation not completed stay tuned")
        # raise HTTPException(status_code=400, detail="Campaign generation not completed")

    # Locate HTML file
    outputs_dir = "outputs"
    website_files = [f for f in os.listdir(outputs_dir) if f.endswith("_campaign_website.html")]
    campaign_files = [f for f in website_files if campaign_id in f]

    if not campaign_files:
        raise HTTPException(status_code=404, detail="Website file not found")

    latest_file = sorted(campaign_files)[-1]
    file_path = os.path.join(outputs_dir, latest_file)

    # Return HTML directly
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 