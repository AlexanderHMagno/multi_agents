"""
State Management for Multi-Agent Workflow

This module defines the shared state structure used throughout the campaign generation workflow.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    """
    Shared state structure for the multi-agent campaign generation workflow.
    
    Attributes:
        messages: List of messages exchanged between agents
        campaign_brief: Initial campaign requirements and specifications
        artifacts: Generated content from each agent (strategy, copy, visuals, etc.)
        feedback: Feedback messages from review processes
        revision_count: Number of revision iterations performed
        previous_artifacts: Previous version of artifacts for change detection
        workflow_start_time: Timestamp when workflow began (for timeout monitoring)
    """
    messages: Annotated[list, add_messages]
    campaign_brief: dict
    artifacts: Annotated[dict, {}]
    feedback: Annotated[list, add_messages]
    revision_count: int
    previous_artifacts: dict
    workflow_start_time: float 