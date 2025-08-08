#!/usr/bin/env python3
"""
Startup Script for FastAPI Campaign Generation Server

This script handles environment setup, dependency checking, and server startup
for the Multi-Agent Campaign Generation API.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "langchain",
        "langchain_openai",
        "langgraph",
        "openai",
       
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r api/requirements.txt")
        return False
    
    return True


def check_environment():
    """Check if environment variables are set"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env file not found")
        print("💡 Create .env file with your API keys:")
        print("""
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=your_openai_key_here
RATIONAL_MODEL=google/gemini-2.5-flash-lite
        """)
        # Not fatal; continue
    
    print("✅ Environment variables check complete")
    return True


def create_outputs_directory():
    """Create outputs directory if it doesn't exist"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        outputs_dir.mkdir()
        print("✅ Created outputs directory")
    else:
        print("✅ Outputs directory exists")


def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting FastAPI Campaign Generation Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Alternative Docs: http://localhost:8000/redoc")
    print("\n⏹️ Press Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        # Use import string so reload works reliably
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 If you see 'No module named api', ensure PYTHONPATH includes the repo root (e.g., export PYTHONPATH=$(pwd))")
        sys.exit(1)


def main():
    """Main startup function"""
    print("🎨 Multi-Agent Campaign Generation API")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        sys.exit(1)
    
    # Check environment
    print("\n🔍 Checking environment...")
    check_environment()
    
    # Create outputs directory
    print("\n🔍 Setting up directories...")
    create_outputs_directory()
    
    # Start server
    start_server()


if __name__ == "__main__":
    main() 