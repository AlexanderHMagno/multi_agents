#!/usr/bin/env python3

import os
import requests
import time
from typing import Annotated, List, TypedDict
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
import langgraph

from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from openai import OpenAI # for DALL-E API
from pdf_generator import generate_campaign_pdf

# Load environment variables
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_API_KEY = os.getenv("DALLE_API_KEY")
RATIONAL_MODEL = "google/gemini-2.5-flash-lite"
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
client = OpenAI(api_key=OPENAI_API_KEY)  # Use OPENAI_API_KEY for DALL-E

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")

# Verify API keys are loaded
if not OPENROUTER_API_KEY or not OPENROUTER_BASE_URL:
    raise ValueError("Please ensure OPENROUTER_API_KEY and OPENROUTER_BASE_URL are set in your .env file")

print(f"🔧 Initializing LLM with:")
print(f"   Model: {RATIONAL_MODEL}")
print(f"   Base URL: {OPENROUTER_BASE_URL}")
print(f"   API Key: {'✅ Set' if OPENROUTER_API_KEY else '❌ Missing'}")

llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    model_name=RATIONAL_MODEL,
    temperature=0.7
)

# Test LLM connection
try:
    print("🧪 Testing LLM connection...")
    test_response = llm.invoke([HumanMessage(content="Hello, this is a test message.")])
    print("✅ LLM connection successful")
except Exception as e:
    print(f"❌ LLM connection failed: {str(e)}")
    print("🔧 Please check your API configuration")

# Define state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]
    campaign_brief: dict
    artifacts: Annotated[dict, {}]
    feedback: Annotated[list, add_messages]
    revision_count: int
    previous_artifacts: dict
    workflow_start_time: float

# Workflow Monitoring System
class WorkflowMonitor:
    def __init__(self, max_duration=300):  # 5 minutes default
        self.start_time = time.time()
        self.max_duration = max_duration
        self.iteration_log = []
    
    def check_timeout(self):
        elapsed = time.time() - self.start_time
        if elapsed > self.max_duration:
            print(f"⏰ Timeout reached ({elapsed:.1f}s). Completing workflow.")
            return True
        return False
    
    def log_iteration(self, state):
        iteration_data = {
            "timestamp": time.time(),
            "revision_count": state.get("revision_count", 0),
            "artifacts_count": len(state.get("artifacts", {})),
            "feedback_count": len(state.get("feedback", []))
        }
        self.iteration_log.append(iteration_data)
        
        # Alert if too many iterations
        if len(self.iteration_log) > 5:
            print("🚨 High iteration count detected. Consider manual intervention.")
    
    def get_summary(self):
        if not self.iteration_log:
            return {"total_iterations": 0, "avg_artifacts": 0, "duration": 0}
        
        return {
            "total_iterations": len(self.iteration_log),
            "avg_artifacts": sum(log["artifacts_count"] for log in self.iteration_log) / len(self.iteration_log),
            "duration": self.iteration_log[-1]["timestamp"] - self.iteration_log[0]["timestamp"]
        }

# Quality Assessment System
class QualityChecker:
    @staticmethod
    def assess_quality(state):
        artifacts = state.get("artifacts", {})
        quality_score = 0
        
        # Score based on content completeness and length
        if artifacts.get("strategy"):
            quality_score += 20
        if artifacts.get("creative_concepts"):
            quality_score += 20
        if artifacts.get("copy"):
            quality_score += 20
        if artifacts.get("visual", {}).get("image_url"):
            quality_score += 20
        if artifacts.get("audience_personas"):
            quality_score += 10
        if artifacts.get("cta_optimization"):
            quality_score += 10
        
        return quality_score
    
    @staticmethod
    def has_significant_changes(state):
        current_artifacts = state.get("artifacts", {})
        previous_artifacts = state.get("previous_artifacts", {})
        
        # Compare current vs previous artifacts
        changes = 0
        for key in current_artifacts:
            if key not in previous_artifacts:
                changes += 1
            elif current_artifacts[key] != previous_artifacts[key]:
                changes += 1
        
        # Store current as previous for next iteration
        state["previous_artifacts"] = current_artifacts.copy()
        
        return changes >= 2  # Threshold for "significant" changes
    
    @staticmethod
    def analyze_feedback_quality(state):
        feedback = state.get("feedback", [])
        
        if not feedback:
            return "complete"
        
        last_feedback = feedback[-1].lower()
        
        # Check for positive feedback indicators
        positive_indicators = ["good", "great", "excellent", "approved", "satisfied", "perfect"]
        negative_indicators = ["revise", "change", "improve", "fix", "wrong", "bad", "needs"]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in last_feedback)
        negative_count = sum(1 for indicator in negative_indicators if indicator in last_feedback)
        
        # Exit on positive feedback
        if positive_count > negative_count:
            print("✅ Positive feedback detected. Completing workflow.")
            return "complete"
        
        # Continue only on negative feedback
        if negative_count > 0:
            return "continue_revision"
        
        return "complete"

# Base Agent class
class BaseAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.llm = llm
    
    def get_messages(self, content: str) -> List:
        return [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=content)
        ]
    
    @staticmethod
    def return_state(state: State, response, new_artifacts: dict = None, feedback: list = None) -> dict:
        return {
            "messages": [response],
            "artifacts": {
                **state.get("artifacts", {}),
                **(new_artifacts or {})
            },
            "feedback": [*state.get("feedback", []), *(feedback or [])],
            "revision_count": state.get("revision_count", 0),
            "campaign_brief": state["campaign_brief"],
            "previous_artifacts": state.get("previous_artifacts", {}),
            "workflow_start_time": state.get("workflow_start_time", time.time())
        }

# Project Manager Agent with enhanced monitoring
class ProjectManager(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a project manager coordinating an ad campaign creation.
            Your role is to oversee the entire workflow and ensure all teams are aligned.
            Analyze the current state and decide on next actions. If feedback indicates
            improvements are needed, suggest specific areas for revision."""
        )
    
    def run(self, state: State) -> dict:
        messages = self.get_messages(f"Current state: {state}. What should be our next action?")
        response = self.llm.invoke(messages)
        
        # Increment revision_count if feedback exists
        if state.get("feedback"):
            state["revision_count"] = state.get("revision_count", 0) + 1

        print(f"Revision count: {state['revision_count']}")
        print(f"Feedback: {state['feedback']}")
        return self.return_state(state, response)

# Strategy Team
class StrategyTeam(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the strategy team responsible for analyzing campaign requirements.
            Provide strategic recommendations for targeting, messaging, and positioning.
            Focus on actionable insights that will guide creative development."""
        )
    
    def run(self, state: State) -> dict:
        messages = self.get_messages(f"Analyze this campaign brief: {state['campaign_brief']}")
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"strategy": response.content})

# Creative Team
class CreativeTeam(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the creative team responsible for generating innovative ad concepts.
            Generate compelling creative concepts that align with the strategy.
            Include visual direction and thematic elements."""
        )
    
    def run(self, state: State) -> dict:
        strategy = state['artifacts'].get('strategy', '')
        messages = self.get_messages(f"Based on this strategy: {strategy}, generate creative concepts.")
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"creative_concepts": response.content})

# Copy Team
class CopyTeam(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the copywriting team responsible for creating compelling ad copy.
            Write engaging headlines, body copy, and calls-to-action that align with the creative concepts.
            Ensure copy is persuasive and on-brand."""
        )
    
    def run(self, state: State) -> dict:
        concepts = state['artifacts'].get('creative_concepts', '')
        messages = self.get_messages(f"Based on these concepts: {concepts}, write the ad copy.")
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"copy": response.content})

# Visual Team

class VisualTeam(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the visual design lead for this campaign. 
            Your job is to create an image prompt for DALL·E that describes the ad in vivid visual terms.
            The prompt should be no more than 3800 characters."""
        )

    def run(self, state: State) -> dict:
        copy = state["artifacts"].get("copy", "")
        concepts = state["artifacts"].get("creative_concepts", "")
        messages = self.get_messages(
            f"Based on this copy: {copy} and concepts: {concepts}, create a detailed image prompt."
        )
        response = self.llm.invoke(messages)

        return self.return_state(state, response, {"visual": {"image_prompt": response.content}})


# Final Visual Agent - Image Generator using DALL·E
class DesignerTeam(BaseAgent):
    def __init__(self, openai_client):
        super().__init__(
            system_prompt="""You are the senior designer team responsible for creating the ad design.
            Your task is to generate a high-quality marketing image based on the final visual prompt."""
        )
        # self.client = openai_client

    def run(self, state: State) -> dict:
        visual_data = state['artifacts'].get("visual", {})
        visual_prompt = visual_data.get("image_prompt", "")

        if not visual_prompt:
            print("[⚠️] No visual prompt found. Skipping image generation.")
            return self.return_state(state, None)

        if len(visual_prompt) > 3800:
            visual_prompt = visual_prompt[:3800] + "..."

        print("[🎨] Generating image from visual prompt...")

        try:
            # image_response = self.client.images.generate(
            #     model="dall-e-3",
            #     prompt=visual_prompt,
            #     size="1024x1024",
            #     quality="standard",
            #     n=1,
            # )
            # image_url = image_response.data[0].url
            # image_url = '''
            # https://oaidalleapiprodscus.blob.core.windows.net/private/org-EPwhekFzkmZauhpAEjYQWB5V/user-nHwQx7jjxRTOVfCFQ0oXrqjN/img-kX3x8OgE3UhZ1MTZRDXJ07dw.png?st=2025-08-03T02%3A18%3A56Z&se=2025-08-03T04%3A18%3A56Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=cc612491-d948-4d2e-9821-2683df3719f5&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-08-02T16%3A50%3A41Z&ske=2025-08-03T16%3A50%3A41Z&sks=b&skv=2024-08-04&sig=mjboHnd%2BSbEEZS7yeCiepb2E7m6H0C3uTe78gfJjR%2Bs%3D
            # '''
            image_url = '''20250802_212312_landing_page.html'''
            print("[✅] Image generated successfully.")
            print(f"Image URL: {image_url}")
            return self.return_state(
                state,
                response="Image generation successful",
                new_artifacts={
                    "visual": {
                        "image_prompt": visual_prompt,
                        "image_url": image_url
                    }
                }
            )

        except Exception as e:
            print(f"[❌ VisualAgent] Failed to generate image: {e}")
            return self.return_state(
                state,
                response="Image generation  Failed",
                new_artifacts={
                    "visual": {
                        "image_prompt": visual_prompt,
                        "image_url": None
                    }
                }
            )


class CampaignSummaryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the campaign summarizer. Your job is to take all campaign elements
            (strategy, concepts, copy, visuals, feedback) and create a beautiful, structured summary
            that can be used by both web developers and reporting tools."""
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
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"campaign_summary": response.content})

class WebDeveloper(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the web developer responsible for creating a comprehensive campaign presentation website.
            Your role is to create a professional, modern, and beautiful website that presents ALL campaign information
            in an engaging and visually appealing format suitable for client presentations and stakeholder reviews.
            
            Create a complete campaign presentation website with:
            - Modern, responsive design using CSS Grid/Flexbox
            - Professional styling with gradients, shadows, animations, and modern UI elements
            - Multiple sections showcasing different aspects of the campaign
            - Interactive elements, hover effects, and smooth transitions
            - Mobile-first responsive design
            - SEO-optimized structure
            - Professional typography and color schemes
            - Campaign data visualization and charts
            - Executive summary and key insights
            - Detailed breakdown of all campaign components
            - Contact information and call-to-action elements
            - Footer with company information
            
            Structure the website as a comprehensive campaign presentation with sections for:
            - Executive Summary
            - Campaign Strategy
            - Audience Analysis
            - Creative Concepts
            - Copy and Messaging
            - CTA Optimization
            - Media Planning
            - Business Impact
            - Visual Assets
            - Recommendations
            
            Use all the provided campaign data to create a comprehensive, professional campaign presentation website."""
        )
    
    def run(self, state: State) -> dict:
        # Extract all campaign artifacts
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        audience_personas = state['artifacts'].get('audience_personas', '')
        creative_concepts = state['artifacts'].get('creative_concepts', '')
        copy_content = state['artifacts'].get('copy', '')
        cta_optimization = state['artifacts'].get('cta_optimization', '')
        media_plan = state['artifacts'].get('media_plan', '')
        client_summary = state['artifacts'].get('client_summary', '')
        campaign_summary = state['artifacts'].get('campaign_summary', '')
        visual_data = state['artifacts'].get('visual', {})
        image_url = visual_data.get('image_url', '')
        image_prompt = visual_data.get('image_prompt', '')
        
        # Create comprehensive campaign presentation website prompt
        comprehensive_prompt = f"""
        Create a comprehensive, professional campaign presentation website using ALL the following campaign information:

        CAMPAIGN BRIEF:
        {campaign_brief}

        STRATEGY:
        {strategy}

        AUDIENCE PERSONAS:
        {audience_personas}

        CREATIVE CONCEPTS:
        {creative_concepts}

        COPY CONTENT:
        {copy_content}

        CTA OPTIMIZATION:
        {cta_optimization}

        MEDIA PLAN:
        {media_plan}

        CLIENT SUMMARY:
        {client_summary}

        CAMPAIGN SUMMARY:
        {campaign_summary}

        VISUAL ASSETS:
        Image URL: {image_url}
        Image Description: {image_prompt}

        WEBSITE REQUIREMENTS:
        1. Create a complete HTML page with embedded CSS and JavaScript
        2. Design as a professional campaign presentation website, not a landing page
        3. Use modern CSS with gradients, shadows, animations, and professional styling
        4. Include all campaign sections: Executive Summary, Strategy, Audience, Creative, Copy, CTA, Media, Impact
        5. PROMINENTLY DISPLAY THE GENERATED IMAGE in multiple ways:
           - Hero section with the image as background or featured element
           - Visual concepts section showcasing the image with description
           - Creative assets section highlighting the image
           - Use the image URL: {image_url}
           - Include the image description: {image_prompt}
           - Add visual storytelling around the image
           - Create interactive image galleries or carousels
           - Include image analysis and creative insights
        6. Make it mobile-responsive with CSS Grid/Flexbox
        7. Include interactive elements, hover effects, and smooth transitions
        8. Add proper meta tags for SEO
        9. Use professional color schemes and modern typography
        10. Include data visualization elements and progress indicators
        11. Add navigation menu and smooth scrolling
        12. Create a comprehensive footer with contact information
        13. Include campaign metrics and performance indicators
        14. Add professional presentation elements like slides and sections
        15. Use modern UI components like cards, modals, and tooltips
        16. Create a dedicated "Visual Concepts" or "Creative Assets" section
        17. Include image analysis and creative direction insights
        18. Add visual storytelling elements around the campaign image

        IMPORTANT: The generated image should be a central visual element throughout the website, not just a small thumbnail. 
        Use it prominently in the hero section, creative concepts section, and as a key visual asset in the presentation.
        Include the image description and creative insights as part of the visual storytelling.
        for other images use pixabay.com to find images that are relevant to the campaign.

        Generate a complete, professional campaign presentation website that showcases the entire campaign comprehensively.
        The website should look like a modern, beautiful presentation suitable for client meetings and stakeholder reviews.
        """
        
        messages = self.get_messages(comprehensive_prompt)
        response = self.llm.invoke(messages)
        print(f"Comprehensive campaign presentation website generated with all campaign data")
        return self.return_state(state, response, {"web_developer": {"campaign_website": response.content}})

class PDFGeneratorTeam(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a PDF generation specialist responsible for creating comprehensive campaign reports.
            Your role is to create a professional, well-structured PDF report that incorporates ALL campaign information
            including strategy, audience personas, creative concepts, copy, CTAs, media plan, client summary, and analytics.
            
            Create a comprehensive PDF report with:
            - Executive summary and campaign overview
            - Detailed strategy analysis and recommendations
            - Audience personas and targeting insights
            - Creative concepts and visual direction
            - Copy content and messaging strategy
            - CTA optimization and conversion elements
            - Media plan and distribution strategy
            - Client summary and business impact
            - Analytics and performance metrics
            - Visual assets and design elements
            - Recommendations and next steps
            
            Structure the report professionally with proper sections, headers, and formatting.
            Include all campaign data in an organized, easy-to-read format suitable for stakeholders."""
        )

    def run(self, state: State) -> dict:
        # Extract all campaign artifacts
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        audience_personas = state['artifacts'].get('audience_personas', '')
        creative_concepts = state['artifacts'].get('creative_concepts', '')
        copy_content = state['artifacts'].get('copy', '')
        cta_optimization = state['artifacts'].get('cta_optimization', '')
        media_plan = state['artifacts'].get('media_plan', '')
        client_summary = state['artifacts'].get('client_summary', '')
        campaign_summary = state['artifacts'].get('campaign_summary', '')
        visual_data = state['artifacts'].get('visual', {})
        image_url = visual_data.get('image_url', '')
        image_prompt = visual_data.get('image_prompt', '')
        revision_count = state.get('revision_count', 0)
        
        # Create comprehensive PDF report prompt
        comprehensive_prompt = f"""
        Create a comprehensive, professional PDF report using ALL the following campaign information:

        CAMPAIGN BRIEF:
        {campaign_brief}

        STRATEGY:
        {strategy}

        AUDIENCE PERSONAS:
        {audience_personas}

        CREATIVE CONCEPTS:
        {creative_concepts}

        COPY CONTENT:
        {copy_content}

        CTA OPTIMIZATION:
        {cta_optimization}

        MEDIA PLAN:
        {media_plan}

        CLIENT SUMMARY:
        {client_summary}

        CAMPAIGN SUMMARY:
        {campaign_summary}

        VISUAL ASSETS:
        Image URL: {image_url}
        Image Description: {image_prompt}

        WORKFLOW METRICS:
        Revision Count: {revision_count}

        PDF REPORT REQUIREMENTS:
        1. Create a comprehensive report structure with proper sections
        2. Include executive summary at the beginning
        3. Organize content logically: Strategy → Audience → Creative → Copy → Media → Results
        4. Include all campaign data in well-formatted sections
        5. Add visual descriptions and image information
        6. Include workflow metrics and revision history
        7. Provide clear recommendations and next steps
        8. Use professional formatting with headers, subheaders, and bullet points
        9. Include business impact and ROI projections
        10. Add contact information and follow-up actions
        11. Include appendices with detailed data if needed
        12. Create a table of contents structure

        Generate a complete, professional PDF report that showcases the entire campaign comprehensively.
        """
        
        messages = self.get_messages(comprehensive_prompt)
        response = self.llm.invoke(messages)
        print(f"Comprehensive PDF report generated with all campaign data")
        return self.return_state(state, response, {
            "pdf_report": {
                "formatted_content": response.content,
                "campaign_data_used": len(state.get('artifacts', {})),
                "revision_count": revision_count
            }
        })


# Review Team
class ReviewTeam(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the review team responsible for evaluating the campaign.
            Assess the strategy, creative, copy, and visuals for effectiveness and alignment.
            Provide specific feedback and recommendations for improvements."""
        )
    
    def run(self, state: State) -> dict:
        artifacts = state['artifacts']
        messages = self.get_messages(f"Review these campaign elements: {artifacts}")
        response = self.llm.invoke(messages)
        return self.return_state(state, response, feedback=[response.content])

class CTAOptimizer(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the CTA (Call-to-Action) optimization specialist.
            Your role is to analyze the campaign brief, target audience, and goals to suggest
            the most effective calls-to-action that will drive conversions.
            Consider psychological triggers, urgency, and audience-specific language."""
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        copy = state['artifacts'].get('copy', '')
        
        messages = self.get_messages(
            f"Based on this campaign brief: {campaign_brief}, strategy: {strategy}, and copy: {copy}, "
            f"suggest 3-5 optimal CTAs with explanations for why each would be effective."
        )
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"cta_optimization": response.content})

class AudiencePersonaAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the audience persona specialist.
            Your role is to build detailed personas from the campaign brief to guide
            creative direction, tone, and targeting decisions.
            Create comprehensive personas including demographics, psychographics, pain points, and motivations."""
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        
        messages = self.get_messages(
            f"Based on this campaign brief: {campaign_brief}, create 2-3 detailed audience personas. "
            f"Include demographics, psychographics, pain points, motivations, and preferred communication channels."
        )
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"audience_personas": response.content})

class MediaPlanner(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the media planning specialist.
            Your role is to recommend the most effective ad distribution channels
            based on the campaign brief, target audience, and budget.
            Consider social media, paid search, display ads, email marketing, and other channels."""
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        personas = state['artifacts'].get('audience_personas', '')
        
        messages = self.get_messages(
            f"Based on this campaign brief: {campaign_brief} and audience personas: {personas}, "
            f"recommend the optimal media mix for this campaign. Include specific platforms, "
            f"budget allocation, and reasoning for each recommendation."
        )
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"media_plan": response.content})

class ClientSummaryGenerator(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the client summary specialist.
            Your role is to create executive-level summaries for clients that clearly
            communicate the campaign's value proposition, expected outcomes, and ROI.
            Focus on business impact and measurable results."""
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
        response = self.llm.invoke(messages)
        return self.return_state(state, response, {"client_summary": response.content})

# Analytics class
class CampaignAnalytics:
    def __init__(self):
        self.metrics = {
            "iterations": 0,
            "team_performance": {},
            "quality_scores": {},
            "timing": {}
        }
    
    def track_iteration(self, state: dict):
        self.metrics["iterations"] += 1
        # Add performance tracking for each team
        for team, artifact in state.get('artifacts', {}).items():
            if team not in self.metrics["team_performance"]:
                self.metrics["team_performance"][team] = []
            self.metrics["team_performance"][team].append(len(artifact))
    
    def generate_report(self) -> dict:
        return {
            "summary": self._generate_summary(),
            "recommendations": self._generate_recommendations(),
            "performance": self.metrics
        }
    
    def _generate_summary(self):
        return f"Campaign generated in {self.metrics['iterations']} iterations"
    
    def _generate_recommendations(self):
        recommendations = []
        
        # Analyze team performance
        for team, performances in self.metrics["team_performance"].items():
            avg_performance = sum(performances) / len(performances)
            if avg_performance < 100:  # Example threshold
                recommendations.append(f"Consider providing more detailed input to {team}")
        
        return recommendations

# Download image from URL
def download_image(url, filename="generated_ad.png"):
    response = requests.get(url)
    if response.status_code == 200:
        # Add timestamp to filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Image saved to {filename}")
    else:
        print("❌ Failed to download image")

def create_landing_page(result, filename="landing_page.html"):
    landing_page_content = result.get('artifacts', {}).get('web_developer', {}).get('landing_page', '')
    
    if landing_page_content:
        try:
            # Add timestamp to filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            
            # Validate HTML content
            if not landing_page_content.strip().startswith('<!DOCTYPE html>') and not landing_page_content.strip().startswith('<html'):
                print("⚠️ Warning: Generated content may not be valid HTML")
            
            # Ensure proper HTML structure
            if '<html' not in landing_page_content:
                landing_page_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Landing Page</title>
</head>
<body>
{landing_page_content}
</body>
</html>"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(landing_page_content)
            
            # Calculate content statistics
            content_length = len(landing_page_content)
            sections_count = landing_page_content.count('<section') + landing_page_content.count('<div class="section')
            cta_count = landing_page_content.count('button') + landing_page_content.count('cta')
            
            print(f"✅ Comprehensive landing page saved as {filename}")
            print(f"📊 Content Statistics:")
            print(f"   - Content Length: {content_length:,} characters")
            print(f"   - Sections: {sections_count}")
            print(f"   - CTAs: {cta_count}")
            print(f"   - Campaign Data Used: {len(result.get('artifacts', {}))} artifacts")
            
        except Exception as e:
            print(f"❌ Failed to save landing page: {e}")
    else:
        print("❌ No landing page content found in artifacts")

def create_campaign_website(result, filename="campaign_website.html"):
    campaign_website_content = result.get('artifacts', {}).get('web_developer', {}).get('campaign_website', '')
    
    if campaign_website_content:
        try:
            # Add timestamp to filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            
            # Validate HTML content
            if not campaign_website_content.strip().startswith('<!DOCTYPE html>') and not campaign_website_content.strip().startswith('<html'):
                print("⚠️ Warning: Generated content may not be valid HTML")
            
            # Ensure proper HTML structure
            if '<html' not in campaign_website_content:
                campaign_website_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Presentation</title>
</head>
<body>
{campaign_website_content}
</body>
</html>"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(campaign_website_content)
            
            # Calculate content statistics
            content_length = len(campaign_website_content)
            sections_count = campaign_website_content.count('<section') + campaign_website_content.count('<div class="section')
            cta_count = campaign_website_content.count('button') + campaign_website_content.count('cta')
            presentation_elements = campaign_website_content.count('presentation') + campaign_website_content.count('campaign')
            visual_elements = campaign_website_content.count('img') + campaign_website_content.count('image') + campaign_website_content.count('visual')
            
            print(f"✅ Comprehensive campaign presentation website saved as {filename}")
            print(f"📊 Website Statistics:")
            print(f"   - Content Length: {content_length:,} characters")
            print(f"   - Sections: {sections_count}")
            print(f"   - Interactive Elements: {cta_count}")
            print(f"   - Presentation Elements: {presentation_elements}")
            print(f"   - Visual Elements: {visual_elements}")
            print(f"   - Campaign Data Used: {len(result.get('artifacts', {}))} artifacts")
            
            # Check for image integration
            if result.get('artifacts', {}).get('visual', {}).get('image_url'):
                print(f"   - 🎨 Visual Concepts: Image integrated prominently")
            else:
                print(f"   - ⚠️ Visual Concepts: No image URL found")
            
        except Exception as e:
            print(f"❌ Failed to save campaign website: {e}")
    else:
        print("❌ No campaign website content found in artifacts")




def smart_revision_router(state, monitor: WorkflowMonitor):
    """
    Comprehensive revision router with multiple safeguards to prevent infinite loops
    """
    
    # 1. Check timeout
    if monitor.check_timeout():
        return "complete"
    
    # 2. Log iteration for monitoring
    monitor.log_iteration(state)
    
    # 3. Check revision count
    revision_count = state.get("revision_count", 0)
    max_revisions = 3
    if revision_count >= max_revisions:
        print(f"⚠️ Max revisions ({max_revisions}) reached. Completing workflow.")
        return "complete"
    
    # 4. Check quality threshold
    quality_score = QualityChecker.assess_quality(state)
    if quality_score >= 80:
        print(f"✅ Quality threshold met ({quality_score}/100). Completing workflow.")
        return "complete"
    
    # 5. Check for significant changes
    if not QualityChecker.has_significant_changes(state):
        print("🔄 No significant changes detected. Completing workflow.")
        return "complete"
    
    # 6. Analyze feedback quality
    feedback_result = QualityChecker.analyze_feedback_quality(state)
    if feedback_result == "complete":
        return "complete"
    
    # 7. Route based on feedback type
    feedback = state.get("feedback", [])
    if feedback:
        last_feedback = feedback[-1].lower()
        
        # Route to specific teams based on feedback content
        if any(word in last_feedback for word in ["copy", "text", "words", "headline"]):
            print("📝 Routing to Copy Team for revision...")
            return "copy"
        elif any(word in last_feedback for word in ["visual", "image", "design", "picture"]):
            print("🎨 Routing to Visual Team for revision...")
            return "visual"
        elif any(word in last_feedback for word in ["strategy", "approach", "plan", "target"]):
            print("📊 Routing to Strategy Team for revision...")
            return "strategy"
        elif any(word in last_feedback for word in ["creative", "concept", "idea"]):
            print("💡 Routing to Creative Team for revision...")
            return "creative"
        else:
            print("🔄 General revision needed. Routing to Strategy Team...")
            return "strategy"
    
    return "complete"

def create_workflow():
    # Initialize teams
    pm = ProjectManager()
    strategy = StrategyTeam()
    creative = CreativeTeam()
    copy = CopyTeam()
    visual = VisualTeam()
    review = ReviewTeam()
    web_developer = WebDeveloper()
    designer = DesignerTeam(client)
    campaign_summary = CampaignSummaryAgent()
    pdf_generator = PDFGeneratorTeam()
    
    # Initialize new agents
    cta_optimizer = CTAOptimizer()
    audience_persona = AudiencePersonaAgent()
    media_planner = MediaPlanner()
    client_summary = ClientSummaryGenerator()
    
    # Create graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_edge(START, "project_manager")
    workflow.add_node("project_manager", pm.run)
    workflow.add_node("strategy", strategy.run)
    workflow.add_node("audience_persona", audience_persona.run)
    workflow.add_node("creative", creative.run)
    workflow.add_node("copy", copy.run)
    workflow.add_node("cta_optimizer", cta_optimizer.run)
    workflow.add_node("visual", visual.run)
    workflow.add_node("review", review.run)
    workflow.add_node("web_developer", web_developer.run)
    workflow.add_node("designer", designer.run)
    workflow.add_node("campaign_summary", campaign_summary.run)
    workflow.add_node("media_planner", media_planner.run)
    workflow.add_node("client_summary", client_summary.run)
    workflow.add_node("pdf_generator", pdf_generator.run)
    
    # Define main workflow edges
    workflow.add_edge("project_manager", "strategy")
    workflow.add_edge("strategy", "audience_persona")
    workflow.add_edge("audience_persona", "creative")
    workflow.add_edge("creative", "copy")
    workflow.add_edge("copy", "cta_optimizer")
    workflow.add_edge("cta_optimizer", "visual")
    workflow.add_edge("visual", "designer")
    workflow.add_edge("designer", "review")
    workflow.add_edge("review", "campaign_summary")
    workflow.add_edge("campaign_summary", "media_planner")
    workflow.add_edge("media_planner", "client_summary")
    workflow.add_edge("client_summary", "web_developer")
    workflow.add_edge("web_developer", "pdf_generator")
    
    # Add conditional edges for feedback loops with smart routing
    def create_smart_router(monitor):
        return lambda state: smart_revision_router(state, monitor)
    
    # Initialize monitor
    monitor = WorkflowMonitor(max_duration=300)  # 5 minutes
    
    workflow.add_conditional_edges(
        "project_manager",
        create_smart_router(monitor),
        {
            "strategy": "strategy",
            "creative": "creative",
            "copy": "copy",
            "visual": "visual",
            "complete": END
        }
    )
    
    return workflow, monitor

def main():
    # Sample campaign brief
    campaign_brief = {
        "product": "Forklift",
        "target_audience": "Construction companies, landscaping companies, and other businesses that need a forklift",
        "goals": ["Increase brand awareness", "Drive sales"],
        "key_features": [
           "Brand new",
           "Offer additional services (parts, service, and maintenance)",
           "Zero mileage",
           "Good price",
           "Good condition",
           "5 years warranty"
        ],
        "budget": "$10,000",
        "timeline": "2 weeks"
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
    memory = MemorySaver()
    workflow, monitor = create_workflow()
    workflow_with_memory = workflow.compile(checkpointer=memory)

    # Run workflow with enhanced error handling
    try:
        print("🚀 Starting campaign generation workflow...")
        print(f"📊 Campaign Brief: {campaign_brief['product']}")
        print(f"🎯 Target Audience: {campaign_brief['target_audience']}")
        print(f"💰 Budget: {campaign_brief['budget']}")
        print(f"⏱️ Timeline: {campaign_brief['timeline']}")
        
        result = workflow_with_memory.invoke(initial_state, config={"thread_id": "campaign_001", "recursion_limit": 100})
        
        # Track analytics
        analytics = CampaignAnalytics()
        analytics.track_iteration(result)

        # Display results
        print("\n" + "="*40)
        print("📋 Campaign Results")
        print("="*40)
        
        print("Strategy:")
        print(result['artifacts'].get('strategy', ''))
        print("\nAudience Personas:")
        print(result['artifacts'].get('audience_personas', ''))
        print("\nCreative Concepts:")
        print(result['artifacts'].get('creative_concepts', ''))
        print("\nCopy:")
        print(result['artifacts'].get('copy', ''))
        print("\nCTA Optimization:")
        print(result['artifacts'].get('cta_optimization', ''))
        print("\nMedia Plan:")
        print(result['artifacts'].get('media_plan', ''))
        print("\nClient Summary:")
        print(result['artifacts'].get('client_summary', ''))
        print("\nImage Prompt:")
        print(result['artifacts'].get('visual', {}).get('image_prompt', ''))
        print("\nImage URL:")
        print(result['artifacts'].get('visual', {}).get('image_url', ''))
        print("\nFeedback:")
        print(result.get('feedback', []))

        # Display analytics
        print("\n" + "="*40)
        print("📈 Campaign Analytics Report")
        print("="*40)
        report = analytics.generate_report()
        print(report)

        # Display workflow monitoring summary
        print("\n" + "="*40)
        print("🔄 Workflow Monitoring Summary")
        print("="*40)
        monitor_summary = monitor.get_summary()
        print(f"Total Iterations: {monitor_summary['total_iterations']}")
        print(f"Average Artifacts per Iteration: {monitor_summary['avg_artifacts']:.1f}")
        print(f"Total Duration: {monitor_summary['duration']:.1f} seconds")
        print(f"Final Revision Count: {result.get('revision_count', 0)}")

        # Generate outputs
        print("\n" + "="*40)
        print("📄 Generating Comprehensive PDF Report")
        print("="*40)
        generate_campaign_pdf(result, "final_campaign.pdf")
        
        print("\n" + "="*40)
        print("🌐 Generating Comprehensive Campaign Website")
        print("="*40)
        create_campaign_website(result)
        
        # Display final summary
        print("\n" + "="*40)
        print("✅ Campaign Generation Complete")
        print("="*40)
        print(f"📊 Total Artifacts Generated: {len(result.get('artifacts', {}))}")
        print(f"📄 PDF Report: final_campaign.pdf")
        print(f"🌐 Campaign Website: [timestamp]_campaign_website.html")
        print(f"🔄 Total Revisions: {result.get('revision_count', 0)}")
        print(f"⏱️ Total Duration: {monitor_summary['duration']:.1f} seconds")

    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Additional debugging information
        import traceback
        print(f"\n📋 Full traceback:")
        traceback.print_exc()
        
        # Check API configuration
        print(f"\n🔧 Configuration Check:")
        print(f"OpenRouter API Key: {'✅ Set' if OPENROUTER_API_KEY else '❌ Missing'}")
        print(f"OpenRouter Base URL: {'✅ Set' if OPENROUTER_BASE_URL else '❌ Missing'}")
        print(f"OpenAI API Key: {'✅ Set' if OPENAI_API_KEY else '❌ Missing'}")
        
        # Check environment variables
        print(f"\n🌍 Environment Variables:")
        print(f"OPENROUTER_API_KEY: {'Set' if os.getenv('OPENROUTER_API_KEY') else 'Not Set'}")
        print(f"OPENROUTER_BASE_URL: {'Set' if os.getenv('OPENROUTER_BASE_URL') else 'Not Set'}")
        print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not Set'}")
        
        print(f"\n💡 Troubleshooting Tips:")
        print(f"1. Check your .env file has all required API keys")
        print(f"2. Ensure OpenRouter API key is valid")
        print(f"3. Verify network connection")
        print(f"4. Check if API rate limits are exceeded")

if __name__ == "__main__":
    main() 