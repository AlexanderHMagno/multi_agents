#!/usr/bin/env python3
"""
Multi-Agent Marketing Campaign Generation System

Main entry point for the campaign generation workflow.
Run this script to generate comprehensive marketing campaigns using AI agents.

Usage:
    python main.py

Make sure to set up your .env file with the required API keys before running.
"""

import time
import traceback
from langgraph.checkpoint.memory import MemorySaver

from src.utils.config import load_configuration
from src.utils.state import State
from src.utils.monitoring import WorkflowMonitor, CampaignAnalytics
from src.utils.file_handlers import create_campaign_website
from src.workflows.campaign_workflow import create_workflow


def main():
    """Main execution function for campaign generation"""
    
    # Load configuration and initialize clients
    try:
        config = load_configuration()
        llm = config["llm"]
        openai_client = config["openai_client"]
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return
    
    # Sample campaign brief
    campaign_brief = {
        "product": "Generate Marketing Campaign for a product",
        "client": "Marketing.ai",
        "client_website": "",
        "client_logo": "https://cdn.pixabay.com/photo/2016/01/25/16/41/ottawa-1160993_1280.png",
        "color_scheme": "Pick a color scheme for the campaign",
        "target_audience": "Pick a target audience for the campaign",
        "goals": ["Increase lead generation", "Drive enrollment", "Increase website traffic"],
        "key_features": [
           "Pick a key feature for the campaign",
        ],
        "budget": "$2,000",
        "timeline": "2 month",
        "tone_style": "Professional and engaging",
        "language": "English"
    }

    # Initialize state with monitoring
    initial_state = {
        "messages": [],
        "campaign_brief": campaign_brief,
        "artifacts": {},
        "feedback": [],
        "revision_count": 0,
        "previous_artifacts": {},
        "workflow_start_time": time.time()
    }

    # Create workflow with memory and monitoring
    try:
        memory = MemorySaver()
        workflow, monitor = create_workflow(llm, openai_client)
        workflow_with_memory = workflow.compile(checkpointer=memory)

        print("🚀 Starting campaign generation workflow...")
        
        # Run workflow with enhanced error handling
        result = workflow_with_memory.invoke(
            initial_state, 
            config={"thread_id": "campaign_001", "recursion_limit": 250}
        )
        
        # Track analytics
        analytics = CampaignAnalytics()
        analytics.track_iteration(result)

        # Display workflow monitoring summary
        print("\n" + "="*40)
        print("🔄 Workflow Monitoring Summary")
        print("="*40)
        monitor_summary = monitor.get_summary()
        print(f"Total Iterations: {monitor_summary['total_iterations']}")
        print(f"Average Artifacts per Iteration: {monitor_summary['avg_artifacts']:.1f}")
        print(f"Total Duration: {monitor_summary['duration']:.1f} seconds")
        print(f"Final Revision Count: {result.get('revision_count', 0)}")
    
        # Generate output files
        create_campaign_website(result)
        
        # Display final summary
        print("\n" + "="*40)
        print("✅ Campaign Generation Complete")
        print("="*40)
        print(f"📊 Total Artifacts Generated: {len(result.get('artifacts', {}))}")
        print(f"🌐 Campaign Website: outputs/[timestamp]_campaign_website.html")
        print(f"🔄 Total Revisions: {result.get('revision_count', 0)}")
        print(f"⏱️ Total Duration: {monitor_summary['duration']:.1f} seconds")

    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Additional debugging information
        print(f"\n📋 Full traceback:")
        traceback.print_exc()
        
        # Check API configuration
        print(f"\n🔧 Configuration Check:")
        print(f"OpenRouter API Key: {'✅ Set' if config.get('openrouter_api_key') else '❌ Missing'}")
        print(f"OpenRouter Base URL: {'✅ Set' if config.get('openrouter_base_url') else '❌ Missing'}")
        print(f"OpenAI API Key: {'✅ Set' if config.get('openai_api_key') else '❌ Missing'}")
        
        print(f"\n💡 Troubleshooting Tips:")
        print(f"1. Check your .env file has all required API keys")
        print(f"2. Ensure OpenRouter API key is valid")
        print(f"3. Verify network connection")
        print(f"4. Check if API rate limits are exceeded")


if __name__ == "__main__":
    main() 