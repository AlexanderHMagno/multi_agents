"""
Configuration Management

This module handles loading and validating environment variables,
API keys, and other configuration settings.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import OpenAI


def load_configuration():
    """
    Load and validate all configuration settings from environment variables.
    
    Returns:
        dict: Configuration dictionary with API clients and settings
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Load environment variables
    load_dotenv()
    
    # Get API keys and configuration
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url = os.getenv("OPENROUTER_BASE_URL")
    rational_model = os.getenv("RATIONAL_MODEL", "google/gemini-2.5-flash-lite")
    
    # Validate required keys
    if not openrouter_api_key or not openrouter_base_url:
        raise ValueError(
            "Please ensure OPENROUTER_API_KEY and OPENROUTER_BASE_URL are set in your .env file"
        )
    
    # Print configuration status
    print(f"🔧 Initializing LLM with:")
    print(f"   Model: {rational_model}")
    print(f"   Base URL: {openrouter_base_url}")
    print(f"   OpenRouter API Key: {'✅ Set' if openrouter_api_key else '❌ Missing'}")
    print(f"   OpenAI API Key: {'✅ Set' if openai_api_key else '❌ Missing'}")
    
    # Initialize LLM client
    llm = ChatOpenAI(
        api_key=openrouter_api_key,
        base_url=openrouter_base_url,
        model_name=rational_model,
        temperature=0.7
    )
    
    # Initialize OpenAI client for DALL-E (if available)
    openai_client = None
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
    
    # Test LLM connection
    try:
        print("🧪 Testing LLM connection...")
        from langchain_core.messages import HumanMessage
        test_response = llm.invoke([HumanMessage(content="Hello, this is a test message.")])
        print("✅ LLM connection successful")
    except Exception as e:
        print(f"❌ LLM connection failed: {str(e)}")
        print("🔧 Please check your API configuration")
    
    return {
        "llm": llm,
        "openai_client": openai_client,
        "openai_api_key": openai_api_key,
        "openrouter_api_key": openrouter_api_key,
        "openrouter_base_url": openrouter_base_url,
        "rational_model": rational_model
    } 