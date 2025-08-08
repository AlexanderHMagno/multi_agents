"""
Multi-Agent Marketing Campaign Generation System

A sophisticated multi-agent system for generating comprehensive marketing campaigns
using LangChain, LangGraph, and OpenAI APIs.
"""

__version__ = "1.0.0"
__author__ = "Marketing AI Team"

from .workflows.campaign_workflow import create_workflow
from .utils.file_handlers import create_campaign_website

__all__ = [
    "create_workflow", 
    "create_campaign_website"
] 