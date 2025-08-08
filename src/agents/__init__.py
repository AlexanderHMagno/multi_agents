"""
Agent Classes for Multi-Agent Marketing Campaign System

This module contains all the specialized agent classes used in the campaign generation workflow.
"""

from .base_agent import BaseAgent, WorkflowErrorTracker
from .content_agents import ProjectManager, StrategyTeam, CreativeTeam, CopyTeam, VisualTeam
from .design_agents import DesignerTeam, HTMLValidationAgent
from .analysis_agents import ReviewTeam, CampaignSummaryAgent, CTAOptimizer, AudiencePersonaAgent
from .output_agents import WebDeveloper, PDFGeneratorTeam
from .specialized_agents import SocialMediaCampaignAgent, EmotionPersonalizationAgent, MediaPlanner, ClientSummaryGenerator

__all__ = [
    # Base classes
    "BaseAgent",
    "WorkflowErrorTracker",
    
    # Content generation agents
    "ProjectManager",
    "StrategyTeam", 
    "CreativeTeam",
    "CopyTeam",
    "VisualTeam",
    
    # Design and validation agents
    "DesignerTeam",
    "HTMLValidationAgent",
    
    # Analysis agents
    "ReviewTeam",
    "CampaignSummaryAgent",
    "CTAOptimizer",
    "AudiencePersonaAgent",
    
    # Output generation agents
    "WebDeveloper",
    "PDFGeneratorTeam",
    
    # Specialized agents
    "SocialMediaCampaignAgent",
    "EmotionPersonalizationAgent",
    "MediaPlanner",
    "ClientSummaryGenerator",
] 