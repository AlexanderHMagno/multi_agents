"""
Content Generation Agents

This module contains agents responsible for generating the core content of marketing campaigns,
including strategy, creative concepts, copy, and visual direction.
"""

from .base_agent import BaseAgent
from ..utils.state import State


class ProjectManager(BaseAgent):
    """
    Project Manager Agent - Coordinates the overall workflow and manages revisions.
    
    Responsibilities:
    - Workflow coordination and oversight
    - Revision management and feedback integration
    - Quality gate enforcement
    - Team communication and alignment
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are a project manager coordinating an ad campaign creation.
            Your role is to oversee the entire workflow and ensure all teams are aligned.
            Analyze the current state and decide on next actions. If feedback indicates
            improvements are needed, suggest specific areas for revision.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        messages = self.get_messages(f"Current state: {state}. What should be our next action?")
        response = self.invoke_llm_with_retry(messages, "Project Management")
        
        # Increment revision_count if feedback exists
        if state.get("feedback"):
            state["revision_count"] = state.get("revision_count", 0) + 1

        print(f"Revision count: {state['revision_count']}")
        print(f"Feedback: {state['feedback']}")
        return self.return_state(state, response)


class StrategyTeam(BaseAgent):
    """
    Strategy Team Agent - Analyzes campaign requirements and provides strategic direction.
    
    Responsibilities:
    - Market analysis and competitive research
    - Target audience analysis and segmentation
    - Campaign positioning and messaging strategy
    - Goals alignment and success metrics definition
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the strategy team responsible for analyzing campaign requirements.
            Provide strategic recommendations for targeting, messaging, and positioning.
            Focus on actionable insights that will guide creative development.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        messages = self.get_messages(f"Analyze this campaign brief: {state['campaign_brief']}")
        response = self.invoke_llm_with_retry(messages, "Campaign Strategy Analysis")
        return self.return_state(state, response, {"strategy": response.content})


class CreativeTeam(BaseAgent):
    """
    Creative Team Agent - Generates innovative creative concepts and campaign ideas.
    
    Responsibilities:
    - Creative concept development and ideation
    - Campaign theme and narrative creation
    - Visual direction and aesthetic guidance
    - Brand alignment and creative consistency
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the creative team responsible for generating innovative ad concepts.
            Generate compelling creative concepts that align with the strategy.
            Include visual direction and thematic elements.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        strategy = state['artifacts'].get('strategy', '')
        messages = self.get_messages(f"Based on this strategy: {strategy}, generate creative concepts.")
        response = self.invoke_llm_with_retry(messages, "Creative Concept Development")
        return self.return_state(state, response, {"creative_concepts": response.content})


class CopyTeam(BaseAgent):
    """
    Copy Team Agent - Creates compelling and persuasive marketing copy.
    
    Responsibilities:
    - Headline and tagline creation
    - Body copy development
    - Message tone and voice consistency
    - Persuasive writing and emotional triggers
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the copywriting team responsible for creating compelling ad copy.
            Write engaging headlines, body copy, and calls-to-action that align with the creative concepts.
            Ensure copy is persuasive and on-brand.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        concepts = state['artifacts'].get('creative_concepts', '')
        messages = self.get_messages(f"Based on these concepts: {concepts}, write the ad copy.")
        response = self.invoke_llm_with_retry(messages, "Copywriting")
        return self.return_state(state, response, {"copy": response.content})


class VisualTeam(BaseAgent):
    """
    Visual Team Agent - Creates detailed image prompts for DALL-E generation.
    
    Responsibilities:
    - Visual concept translation into DALL-E prompts
    - Image composition and style direction
    - Brand visual consistency
    - Technical prompt optimization for AI generation
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the visual design lead for this campaign. 
            Your job is to create an image prompt for DALL·E that describes the ad in vivid visual terms.
            The prompt should be no more than 3800 characters.""",
            llm=llm
        )

    def run(self, state: State) -> dict:
        copy = state["artifacts"].get("copy", "")
        concepts = state["artifacts"].get("creative_concepts", "")
        messages = self.get_messages(
            f"Based on this copy: {copy} and concepts: {concepts}, create a detailed image prompt."
        )
        response = self.invoke_llm_with_retry(messages, "Visual Design Direction")

        return self.return_state(state, response, {"visual": {"image_prompt": response.content}}) 