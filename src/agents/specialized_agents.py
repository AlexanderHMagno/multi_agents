"""
Specialized Marketing Agents

This module contains agents with specialized focus areas including social media campaigns,
emotion-based personalization, media planning, and client communications.
"""

from .base_agent import BaseAgent
from ..utils.state import State


class SocialMediaCampaignAgent(BaseAgent):
    """
    Social Media Campaign Agent - Creates platform-specific social media strategies.
    
    Responsibilities:
    - TikTok and Instagram campaign development
    - Platform-specific content strategies
    - Hashtag research and trending keywords
    - Influencer collaboration planning
    - User-generated content strategies
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the social media campaign specialist responsible for creating comprehensive
            social media campaigns for TikTok and Instagram. Your role is to develop platform-specific strategies,
            content ideas, hashtags, and engagement tactics that align with the overall campaign goals.
            
            Create social media campaigns that include:
            - Platform-specific content strategies (TikTok vs Instagram)
            - Trending hashtags and keywords
            - Content calendar and posting schedule
            - Engagement tactics and community building
            - Influencer collaboration opportunities
            - User-generated content campaigns
            - Platform-specific features utilization
            - Analytics and performance tracking
            - Viral content strategies
            - Community engagement tactics""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        audience_personas = state['artifacts'].get('audience_personas', '')
        creative_concepts = state['artifacts'].get('creative_concepts', '')
        copy_content = state['artifacts'].get('copy', '')
        
        messages = self.get_messages(
            f"Create a comprehensive social media campaign for TikTok and Instagram based on: "
            f"Campaign Brief: {campaign_brief}, "
            f"Strategy: {strategy}, "
            f"Audience Personas: {audience_personas}, "
            f"Creative Concepts: {creative_concepts}, "
            f"Copy Content: {copy_content}. "
            f"Include platform-specific strategies, trending hashtags, content ideas, and engagement tactics."
        )
        response = self.invoke_llm_with_retry(messages, "Social Media Campaign Development")
        return self.return_state(state, response, {"social_media_campaign": response.content})


class EmotionPersonalizationAgent(BaseAgent):
    """
    Emotion Personalization Agent - Creates hyperpersonalized content based on emotional states.
    
    Responsibilities:
    - Emotion-based content personalization for 13 emotion types
    - Psychological trigger identification
    - Tailored messaging and tone adaptation
    - Emotional journey mapping
    - Personalized CTA optimization
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the emotion personalization specialist responsible for creating
            hyperpersonalized campaign messages based on different emotion types. Your role is to develop
            targeted messaging for each emotion category to maximize engagement and connection.
            
            Create personalized messages for these emotion types:
            - HAPPY: Joyful, positive, celebratory messaging
            - EXCITED: Energetic, enthusiastic, motivational content
            - CALM: Peaceful, reassuring, zen-like messaging
            - ANXIOUS: Supportive, comforting, solution-focused content
            - CONFIDENT: Empowering, bold, achievement-oriented messaging
            - CURIOUS: Intriguing, educational, discovery-focused content
            - SAD: Supportive, uplifting, hope-focused content
            - ANGRY: Understanding, solution-oriented, empowering messaging
            - SCARED: Reassuring, protective, confidence-building content
            - DISGUSTED: Clean, fresh, improvement-focused messaging
            - SURPRISED: Exciting, revelation-based, attention-grabbing content
            - LOVED: Warm, appreciation-focused, community-driven messaging
            - JEALOUS: Aspirational, achievement-focused, motivational content
            
            Develop for each emotion:
            - Personalized copy variations
            - Visual style recommendations
            - Tone and voice adjustments
            - Call-to-action variations
            - Content themes and topics
            - Engagement strategies""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        copy_content = state['artifacts'].get('copy', '')
        cta_optimization = state['artifacts'].get('cta_optimization', '')
        audience_personas = state['artifacts'].get('audience_personas', '')
        
        messages = self.get_messages(
            f"Create hyperpersonalized campaign messages for each emotion type based on: "
            f"Campaign Brief: {campaign_brief}, "
            f"Copy Content: {copy_content}, "
            f"CTA Optimization: {cta_optimization}, "
            f"Audience Personas: {audience_personas}. "
            f"Develop personalized messaging for all 13 emotion types: "
            f"HAPPY, EXCITED, CALM, ANXIOUS, CONFIDENT, CURIOUS, SAD, ANGRY, SCARED, DISGUSTED, SURPRISED, LOVED, JEALOUS. "
            f"Include copy variations, visual recommendations, tone adjustments, and engagement strategies for each emotion."
        )
        response = self.invoke_llm_with_retry(messages, "Emotion-Based Personalization")
        return self.return_state(state, response, {"emotion_personalization": response.content})


class MediaPlanner(BaseAgent):
    """
    Media Planner Agent - Develops comprehensive media distribution strategies.
    
    Responsibilities:
    - Multi-platform media strategy development
    - Budget allocation and optimization
    - Channel selection and prioritization
    - Performance tracking and analytics setup
    - Cross-platform campaign coordination
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the media planning specialist.
            Your role is to recommend the most effective ad distribution channels
            based on the campaign brief, target audience, and budget.
            Consider social media, paid search, display ads, email marketing, and other channels (TikTok, Instagram)""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        personas = state['artifacts'].get('audience_personas', '')
        
        messages = self.get_messages(
            f"Based on this campaign brief: {campaign_brief} and audience personas: {personas}, "
            f"recommend the optimal media mix for this campaign. Include specific platforms, "
            f"budget allocation, and reasoning for each recommendation."
        )
        response = self.invoke_llm_with_retry(messages, "Media Planning Strategy")
        return self.return_state(state, response, {"media_plan": response.content})


class ClientSummaryGenerator(BaseAgent):
    """
    Client Summary Generator Agent - Creates executive-level client communications.
    
    Responsibilities:
    - Executive summary creation for stakeholders
    - Business impact analysis and ROI projections
    - Key insights and recommendations highlighting
    - Client-friendly presentation of complex data
    - Strategic next steps and action items
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the client summary specialist.
            Your role is to create executive-level summaries for clients that clearly
            communicate the campaign's value proposition, expected outcomes, and ROI.
            Focus on business impact and measurable results.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        media_plan = state['artifacts'].get('media_plan', '')
        cta_optimization = state['artifacts'].get('cta_optimization', '')
        
        messages = self.get_messages(
            f"Create an executive summary for the client based on: "
            f"Campaign Brief: {campaign_brief}, "
            f"Strategy: {strategy}, "
            f"Media Plan: {media_plan}, "
            f"CTA Optimization: {cta_optimization}. "
            f"Focus on business value, expected outcomes, and ROI projections."
        )
        response = self.invoke_llm_with_retry(messages, "Client Executive Summary")
        return self.return_state(state, response, {"client_summary": response.content}) 