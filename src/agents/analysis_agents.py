"""
Analysis and Optimization Agents

This module contains agents responsible for reviewing content, optimizing campaign elements,
and providing analytical insights.
"""

from .base_agent import BaseAgent
from ..utils.state import State


class ReviewTeam(BaseAgent):
    """
    Review Team Agent - Evaluates campaign quality and provides feedback.
    
    Responsibilities:
    - Campaign element evaluation and assessment
    - Quality assurance and consistency checking
    - Feedback generation for improvements
    - Strategic alignment verification
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the review team responsible for evaluating the campaign.
            Assess the strategy, creative, copy, and visuals for effectiveness and alignment.
            Provide specific feedback and recommendations for improvements.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        artifacts = state['artifacts']
        messages = self.get_messages(f"Review these campaign elements: {artifacts}")
        response = self.invoke_llm_with_retry(messages, "Campaign Review")
        return self.return_state(state, response, feedback=[response.content])


class CampaignSummaryAgent(BaseAgent):
    """
    Campaign Summary Agent - Creates comprehensive campaign summaries.
    
    Responsibilities:
    - Campaign element consolidation and synthesis
    - Executive summary creation
    - Key insights and recommendations highlighting
    - Structured presentation of campaign data
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the campaign summarizer. Your job is to take all campaign elements
            (strategy, concepts, copy, visuals, feedback) and create a beautiful, structured summary
            that can be used by both web developers and reporting tools.""",
            llm=llm
        )

    def run(self, state: State) -> dict:
        strategy = state["artifacts"].get("strategy", "")
        concepts = state["artifacts"].get("creative_concepts", "")
        copy = state["artifacts"].get("copy", "")
        feedback = state.get("feedback", [])
        image_url = state["artifacts"].get("visual", {}).get("image_url", "")

        prompt = f"""
            Create a structured summary of the campaign. Include:

            1. A headline title for the campaign
            2. A one-paragraph summary
            3. A sectioned breakdown:
              - Strategy
              - Creative Concepts
              - Copy Highlights
              - Key Feedback Points
            4. Visual Asset URL: {image_url}

            Here is the data:
            Strategy: {strategy}
            Creative Concepts: {concepts}
            Copy: {copy}
            Feedback: {" | ".join([msg.content if hasattr(msg, "content") else str(msg) for msg in feedback])}
            """

        messages = self.get_messages(prompt)
        response = self.invoke_llm_with_retry(messages, "Campaign Summary Generation")
        return self.return_state(state, response, {"campaign_summary": response.content})


class CTAOptimizer(BaseAgent):
    """
    CTA Optimizer Agent - Optimizes call-to-action elements for maximum conversion.
    
    Responsibilities:
    - Call-to-action analysis and optimization
    - Psychological trigger identification
    - Conversion rate optimization recommendations
    - A/B testing suggestions for CTAs
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the CTA (Call-to-Action) optimization specialist.
            Your role is to analyze the campaign brief, target audience, and goals to suggest
            the most effective calls-to-action that will drive conversions.
            Consider psychological triggers, urgency, and audience-specific language.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        copy = state['artifacts'].get('copy', '')
        
        messages = self.get_messages(
            f"Based on this campaign brief: {campaign_brief}, strategy: {strategy}, and copy: {copy}, "
            f"suggest 3-5 optimal CTAs with explanations for why each would be effective."
        )
        response = self.invoke_llm_with_retry(messages, "CTA Optimization")
        return self.return_state(state, response, {"cta_optimization": response.content})


class AudiencePersonaAgent(BaseAgent):
    """
    Audience Persona Agent - Creates detailed target audience personas.
    
    Responsibilities:
    - Target audience analysis and segmentation
    - Demographic and psychographic profiling
    - Behavioral pattern identification
    - Communication preference mapping
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the audience persona specialist.
            Your role is to build detailed personas from the campaign brief to guide
            creative direction, tone, and targeting decisions.
            Create comprehensive personas including demographics, psychographics, pain points, and motivations.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        
        messages = self.get_messages(
            f"Based on this campaign brief: {campaign_brief}, create 2-3 detailed audience personas. "
            f"Include demographics, psychographics, pain points, motivations, and preferred communication channels."
        )
        response = self.invoke_llm_with_retry(messages, "Audience Persona Development")
        return self.return_state(state, response, {"audience_personas": response.content}) 