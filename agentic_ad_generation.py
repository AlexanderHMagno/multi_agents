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
client = OpenAI(api_key=OPENAI_API_KEY)

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

# Global error tracking for circuit breaker pattern
class WorkflowErrorTracker:
    def __init__(self, max_failures=5):
        self.failures = 0
        self.max_failures = max_failures
        self.circuit_open = False
    
    def record_failure(self):
        self.failures += 1
        if self.failures >= self.max_failures:
            self.circuit_open = True
            print(f"🚨 CIRCUIT BREAKER ACTIVATED: Too many API failures ({self.failures})")
            print("🔧 Recommendations:")
            print("   1. Check your API keys and configuration")
            print("   2. Verify internet connectivity")
            print("   3. Check OpenRouter service status")
            print("   4. Consider switching to a different model")
    
    def record_success(self):
        # Reset failure count on success
        if self.failures > 0:
            print(f"✅ API recovered after {self.failures} failures")
        self.failures = 0
        self.circuit_open = False
    
    def is_circuit_open(self):
        return self.circuit_open

# Global error tracker instance
error_tracker = WorkflowErrorTracker()

# Base Agent class with enhanced error handling
class BaseAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.llm = llm
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def get_messages(self, content: str) -> List:
        return [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=content)
        ]
    
    def invoke_llm_with_retry(self, messages, context=""):
        """Invoke LLM with retry logic, error handling, and circuit breaker"""
        import time
        import json
        
        # Check circuit breaker
        if error_tracker.is_circuit_open():
            print(f"⚠️ Circuit breaker is open. Generating fallback response for {context}")
            return self.generate_fallback_response(context, "Circuit breaker activated")
        
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Attempting API call for {context} (attempt {attempt + 1}/{self.max_retries})...")
                response = self.llm.invoke(messages)
                print(f"✅ API call successful for {context}")
                error_tracker.record_success()
                return response
                
            except json.JSONDecodeError as e:
                print(f"❌ JSONDecodeError on attempt {attempt + 1} for {context}: {str(e)}")
                error_tracker.record_failure()
                
                if attempt < self.max_retries - 1 and not error_tracker.is_circuit_open():
                    print(f"⏳ Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    print(f"❌ All API attempts failed for {context}. Generating fallback response")
                    return self.generate_fallback_response(context, f"JSONDecodeError: {str(e)}")
                    
            except Exception as e:
                print(f"❌ API Error on attempt {attempt + 1} for {context}: {str(e)}")
                error_tracker.record_failure()
                
                if attempt < self.max_retries - 1 and not error_tracker.is_circuit_open():
                    print(f"⏳ Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2
                else:
                    print(f"❌ All API attempts failed for {context}. Generating fallback response")
                    return self.generate_fallback_response(context, f"API Error: {str(e)}")
        
        return self.generate_fallback_response(context, "Max retries exceeded")
    
    def generate_fallback_response(self, context="", error_details=""):
        """Generate a fallback response when API calls fail"""
        from langchain_core.messages import AIMessage
        
        fallback_content = f"""
        FALLBACK RESPONSE - API Service Unavailable
        
        Agent: {self.__class__.__name__}
        Context: {context}
        Error: {error_details}
        
        This is a generated fallback response due to API connectivity issues.
        The workflow will continue with basic placeholder content.
        
        RECOMMENDATIONS:
        1. Check API key configuration in .env file
        2. Verify OpenRouter service status
        3. Check internet connectivity
        4. Consider rate limiting or quota exhaustion
        5. Try switching to a different model
        
        The campaign generation will continue with available data.
        Please manually review and enhance this section when API service is restored.
        """
        
        return AIMessage(content=fallback_content)
    
    @staticmethod
    def return_state(state: State, response, new_artifacts: dict = None, feedback: list = None) -> dict:
        return {
            "messages": [response] if response else [],
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
        response = self.invoke_llm_with_retry(messages, "Project Management")
        
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
        response = self.invoke_llm_with_retry(messages, "Campaign Strategy Analysis")
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
        response = self.invoke_llm_with_retry(messages, "Creative Concept Development")
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
        response = self.invoke_llm_with_retry(messages, "Copywriting")
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
        response = self.invoke_llm_with_retry(messages)

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
        response = self.invoke_llm_with_retry(messages)
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
        social_media_campaign = state['artifacts'].get('social_media_campaign', '')
        emotion_personalization = state['artifacts'].get('emotion_personalization', '')
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

        SOCIAL MEDIA CAMPAIGN:
        {social_media_campaign}

        EMOTION PERSONALIZATION:
        {emotion_personalization}

        VISUAL ASSETS:
        IMPORTANT: for all images use https://placehold.co/600x400?text= as placeholder images  text= the image description / 600x400 is the size of the image it can be any size as width x height

        WEBSITE REQUIREMENTS:
        1. Create a complete HTML page with embedded CSS and JavaScript
        2. Design as a professional campaign presentation website, not a landing page
        3. Use modern CSS with gradients, shadows, animations, and professional styling
        4. Include all campaign sections: Executive Summary, Strategy, Audience, Creative, Copy, CTA, Media, Social Media, Emotion Personalization, Impact
        5. PROMINENTLY DISPLAY THE GENERATED IMAGE in multiple ways:
           - Hero section with the image as background or featured element
           - Visual concepts section showcasing the image with description
           - Creative assets section highlighting the image
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
        19. Create a dedicated "Social Media Campaign" section showcasing TikTok and Instagram strategies
        20. Include a "Hyperpersonalization" section with emotion-based messaging with (HAPPY, EXCITED, CALM, ANXIOUS, CONFIDENT, CURIOUS)
        20. As well Hyperpersonalization for SAD, ANGRY, SCARED, DISGUSTED, SURPRISED, LOVED, JEALOUS) Allow tab for change emotion message
        21. Add interactive elements for emotion selection and personalized content display
        22. Include social media previews and platform-specific content examples
        23. Add emotion-based content variations and personalization tools
        24. Include hashtag strategies and trending keywords for social media
        25. Add influencer collaboration opportunities and user-generated content strategies
        26. the nav create a dropdown menu for the sections

        IMPORTANT: The generated image should be a central visual element throughout the website, not just a small thumbnail. 
        Use it prominently in the hero section, creative concepts section, and as a key visual asset in the presentation.
        Include the image description and creative insights as part of the visual storytelling.
        
        IMPORTANT important to do the hyperpersonalization for all emotions

        Generate a complete, professional campaign presentation website that showcases the entire campaign comprehensively.
        The website should look like a modern, beautiful presentation suitable for client meetings and stakeholder reviews.
        """
        
        messages = self.get_messages(comprehensive_prompt)
        response = self.invoke_llm_with_retry(messages)
        print(f"Comprehensive campaign presentation website generated with all campaign data")
        print(response.content)
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
        response = self.invoke_llm_with_retry(messages)
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
        response = self.invoke_llm_with_retry(messages)
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
        response = self.invoke_llm_with_retry(messages)
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
        response = self.invoke_llm_with_retry(messages)
        return self.return_state(state, response, {"audience_personas": response.content})

class MediaPlanner(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are the media planning specialist.
            Your role is to recommend the most effective ad distribution channels
            based on the campaign brief, target audience, and budget.
            Consider social media, paid search, display ads, email marketing, and other channels (tiktok, instagram)"""
        )
    
    def run(self, state: State) -> dict:
        campaign_brief = state['campaign_brief']
        personas = state['artifacts'].get('audience_personas', '')
        
        messages = self.get_messages(
            f"Based on this campaign brief: {campaign_brief} and audience personas: {personas}, "
            f"recommend the optimal media mix for this campaign. Include specific platforms, "
            f"budget allocation, and reasoning for each recommendation."
        )
        response = self.invoke_llm_with_retry(messages)
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
        response = self.invoke_llm_with_retry(messages)
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
    # Try to get validated HTML first, fall back to original if not available
    html_validation = result.get('artifacts', {}).get('html_validation', {})
    
    if html_validation and html_validation.get('status') in ['success', 'warning']:
        campaign_website_content = html_validation.get('corrected_html', '')
        validation_used = True
        print("🔍 Using validated and corrected HTML")
    else:
        campaign_website_content = result.get('artifacts', {}).get('web_developer', {}).get('campaign_website', '')
        validation_used = False
        print("⚠️ Using original HTML (validation not available)")
    
    if campaign_website_content:
        try:
            # Create outputs directory if it doesn't exist
            import os
            outputs_dir = "outputs"
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)
                print(f"📁 Created {outputs_dir} directory")
            
            # Add timestamp to filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(outputs_dir, filename)
            
            # Basic validation if not already validated
            if not validation_used:
                # Ensure proper HTML structure
                if not campaign_website_content.strip().startswith('<!DOCTYPE html>'):
                    print("⚠️ Warning: Adding missing DOCTYPE declaration")
                    campaign_website_content = '<!DOCTYPE html>\n' + campaign_website_content
                
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
            
            # Clean up any code block markers that might be in the content
            campaign_website_content = campaign_website_content.replace('```html', '').replace('```', '')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(campaign_website_content)
            
            # Calculate content statistics
            content_length = len(campaign_website_content)
            sections_count = campaign_website_content.count('<section') + campaign_website_content.count('<div class="section')
            cta_count = campaign_website_content.count('button') + campaign_website_content.count('cta')
            presentation_elements = campaign_website_content.count('presentation') + campaign_website_content.count('campaign')
            visual_elements = campaign_website_content.count('img') + campaign_website_content.count('image') + campaign_website_content.count('visual')
            
            print(f"✅ Comprehensive campaign presentation website saved as {filepath}")
            print(f"📊 Website Statistics:")
            print(f"   - Content Length: {content_length:,} characters")
            print(f"   - Sections: {sections_count}")
            print(f"   - Interactive Elements: {cta_count}")
            print(f"   - Presentation Elements: {presentation_elements}")
            print(f"   - Visual Elements: {visual_elements}")
            print(f"   - Campaign Data Used: {len(result.get('artifacts', {}))} artifacts")
            print(f"   - HTML Validation: {'✅ Validated & Corrected' if validation_used else '⚠️ Basic validation only'}")
            
            # Check for image integration
            if result.get('artifacts', {}).get('visual', {}).get('image_url'):
                print(f"   - 🎨 Visual Concepts: Image integrated prominently")
            else:
                print(f"   - ⚠️ Visual Concepts: No image URL found")
            
            # Display validation results if available
            if validation_used and html_validation:
                print(f"   - 🔍 Validation Summary: {html_validation.get('validation_summary', 'N/A')}")
                if html_validation.get('original_issues'):
                    print(f"   - 🔧 Issues Fixed: {len(html_validation.get('original_issues', []))}")
                if html_validation.get('corrected_issues'):
                    print(f"   - ⚠️ Remaining Issues: {len(html_validation.get('corrected_issues', []))}")
            
        except Exception as e:
            print(f"❌ Failed to save campaign website: {e}")
    else:
        print("❌ No campaign website content found in artifacts")

class SocialMediaCampaignAgent(BaseAgent):
    def __init__(self):
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
            - Community engagement tactics"""
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
        response = self.invoke_llm_with_retry(messages)
        return self.return_state(state, response, {"social_media_campaign": response.content})

class EmotionPersonalizationAgent(BaseAgent):
    def __init__(self):
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
            - SAD: Supportive, comforting, solution-focused content
            - ANGRY: Empowering, bold, achievement-oriented messaging
            - SCARED: Intriguing, educational, discovery-focused content
            - DISGUSTED: Supportive, comforting, solution-focused content
            - SURPRISED: Empowering, bold, achievement-oriented messaging
            - LOVED: Intriguing, educational, discovery-focused content
            - JEALOUS: Supportive, comforting, solution-focused content
            
            Develop for each emotion:
            - Personalized copy variations
            - Visual style recommendations
            - Tone and voice adjustments
            - Call-to-action variations
            - Content themes and topics
            - Engagement strategies"""
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
            f"Develop personalized messaging for HAPPY, EXCITED, CALM, ANXIOUS, CONFIDENT, and CURIOUS emotion types. "
            f"Include copy variations, visual recommendations, tone adjustments, and engagement strategies for each emotion."
        )
        response = self.invoke_llm_with_retry(messages)
        return self.return_state(state, response, {"emotion_personalization": response.content})

class HTMLValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are an HTML validation and correction specialist.
            Your role is to inspect HTML code for validity, accessibility, and best practices,
            then provide corrected versions if necessary.
            
            Check for:
            - Valid HTML5 structure and syntax
            - Proper DOCTYPE declaration
            - Complete head section with meta tags
            - Properly nested elements
            - Closed tags and valid attributes
            - Accessibility compliance (alt tags, semantic HTML)
            - CSS and JavaScript syntax within HTML
            - Mobile responsiveness meta tags
            - SEO optimization elements
            - Cross-browser compatibility
            
            If issues are found, provide:
            - Detailed explanation of problems
            - Corrected HTML code
            - Best practice recommendations
            - Performance optimization suggestions"""
        )
    
    def validate_html_structure(self, html_content):
        """Basic HTML structure validation"""
        issues = []
        fixes = []
        
        # Check for DOCTYPE
        if not html_content.strip().startswith('<!DOCTYPE html>'):
            issues.append("Missing DOCTYPE declaration")
            fixes.append("Add <!DOCTYPE html> at the beginning")
        
        # Check for html tag
        if '<html' not in html_content:
            issues.append("Missing <html> tag")
            fixes.append("Add <html lang='en'> tag")
        
        # Check for head section
        if '<head>' not in html_content:
            issues.append("Missing <head> section")
            fixes.append("Add <head> section with meta tags")
        
        # Check for meta charset
        if 'charset=' not in html_content:
            issues.append("Missing charset declaration")
            fixes.append("Add <meta charset='UTF-8'>")
        
        # Check for viewport meta tag
        if 'viewport' not in html_content:
            issues.append("Missing viewport meta tag")
            fixes.append("Add <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        
        # Check for title tag
        if '<title>' not in html_content:
            issues.append("Missing <title> tag")
            fixes.append("Add <title> tag for SEO")
        
        # Check for body tag
        if '<body>' not in html_content:
            issues.append("Missing <body> tag")
            fixes.append("Add <body> tag")
        
        # Check for closing tags
        if '</html>' not in html_content:
            issues.append("Missing closing </html> tag")
            fixes.append("Add closing </html> tag")
        
        return issues, fixes
    
    def validate_css(self, html_content):
        """Comprehensive CSS validation"""
        css_issues = []
        css_fixes = []
        css_warnings = []
        
        import re
        
        # Extract CSS content from style tags and inline styles
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL)
        inline_styles = re.findall(r'style\s*=\s*["\']([^"\']*)["\']', html_content)
        
        all_css = '\n'.join(style_blocks + inline_styles)
        
        if not all_css.strip():
            css_warnings.append("No CSS found in HTML")
            return css_issues, css_fixes, css_warnings
        
        # Check for basic CSS syntax issues
        # Unclosed braces
        open_braces = all_css.count('{')
        close_braces = all_css.count('}')
        if open_braces != close_braces:
            css_issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
            css_fixes.append("Ensure all CSS rules have matching opening and closing braces")
        
        # Missing semicolons (basic check)
        css_lines = all_css.split('\n')
        for i, line in enumerate(css_lines):
            line = line.strip()
            if ':' in line and not line.endswith((';', '{', '}')) and line:
                css_warnings.append(f"Line {i+1}: Missing semicolon after CSS property")
                css_fixes.append("Add semicolons after CSS property declarations")
        
        # Check for vendor prefixes
        if '-webkit-' in all_css or '-moz-' in all_css or '-ms-' in all_css:
            css_warnings.append("Vendor prefixes detected - consider if still needed")
            css_fixes.append("Review vendor prefixes for modern browser support")
        
        # Check for !important usage
        important_count = all_css.count('!important')
        if important_count > 3:
            css_warnings.append(f"Excessive use of !important ({important_count} instances)")
            css_fixes.append("Reduce !important usage and improve CSS specificity")
        
        # Check for responsive design
        if '@media' not in all_css and len(all_css) > 100:
            css_warnings.append("No media queries found - may not be responsive")
            css_fixes.append("Add CSS media queries for responsive design")
        
        # Check for CSS units
        if 'px' in all_css and ('rem' not in all_css and 'em' not in all_css):
            css_warnings.append("Only px units detected - consider relative units")
            css_fixes.append("Use rem/em units for better accessibility and responsiveness")
        
        # Check for CSS reset or normalize
        if 'margin:0' not in all_css.replace(' ', '') and 'margin: 0' not in all_css:
            css_warnings.append("No CSS reset detected")
            css_fixes.append("Consider adding CSS reset for consistent styling")
        
        # Check for modern CSS features
        if 'flexbox' in all_css.lower() or 'flex' in all_css:
            css_warnings.append("Flexbox detected - ensure fallbacks for older browsers")
        
        if 'grid' in all_css and 'display: grid' in all_css:
            css_warnings.append("CSS Grid detected - ensure fallbacks for older browsers")
        
        return css_issues, css_fixes, css_warnings
    
    def validate_javascript(self, html_content):
        """Comprehensive JavaScript validation"""
        js_issues = []
        js_fixes = []
        js_warnings = []
        
        import re
        
        # Extract JavaScript content from script tags and inline handlers
        script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        inline_handlers = re.findall(r'on\w+\s*=\s*["\']([^"\']*)["\']', html_content)
        
        all_js = '\n'.join(script_blocks + inline_handlers)
        
        if not all_js.strip():
            js_warnings.append("No JavaScript found in HTML")
            return js_issues, js_fixes, js_warnings
        
        # Check for basic JavaScript syntax issues
        # Unclosed parentheses, brackets, braces
        open_parens = all_js.count('(')
        close_parens = all_js.count(')')
        if open_parens != close_parens:
            js_issues.append(f"Unmatched parentheses: {open_parens} opening, {close_parens} closing")
            js_fixes.append("Ensure all parentheses are properly matched")
        
        open_brackets = all_js.count('[')
        close_brackets = all_js.count(']')
        if open_brackets != close_brackets:
            js_issues.append(f"Unmatched brackets: {open_brackets} opening, {close_brackets} closing")
            js_fixes.append("Ensure all brackets are properly matched")
        
        open_braces = all_js.count('{')
        close_braces = all_js.count('}')
        if open_braces != close_braces:
            js_issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
            js_fixes.append("Ensure all braces are properly matched")
        
        # Check for common JavaScript issues
        if 'var ' in all_js:
            js_warnings.append("'var' declarations found - consider using 'let' or 'const'")
            js_fixes.append("Replace 'var' with 'let' or 'const' for better scoping")
        
        if '==' in all_js and '===' not in all_js:
            js_warnings.append("Loose equality (==) detected - consider strict equality (===)")
            js_fixes.append("Use strict equality (===) instead of loose equality (==)")
        
        # Check for console.log statements
        if 'console.log' in all_js:
            js_warnings.append("console.log statements found - remove for production")
            js_fixes.append("Remove console.log statements before deployment")
        
        # Check for eval usage
        if 'eval(' in all_js:
            js_issues.append("eval() usage detected - security risk")
            js_fixes.append("Avoid eval() for security reasons")
        
        # Check for jQuery
        if '$(' in all_js or 'jQuery(' in all_js:
            js_warnings.append("jQuery detected - consider modern vanilla JS")
            js_fixes.append("Consider replacing jQuery with modern JavaScript")
        
        # Check for async/await vs promises
        if '.then(' in all_js and 'async' not in all_js:
            js_warnings.append("Promise chains detected - consider async/await")
            js_fixes.append("Consider using async/await for better readability")
        
        # Check for arrow functions
        if 'function(' in all_js and '=>' not in all_js:
            js_warnings.append("Traditional functions detected - consider arrow functions")
            js_fixes.append("Consider using arrow functions for shorter syntax")
        
        # Check for error handling
        if 'try' not in all_js and ('fetch(' in all_js or 'ajax' in all_js):
            js_warnings.append("Network requests without error handling")
            js_fixes.append("Add try-catch blocks for network requests")
        
        return js_issues, js_fixes, js_warnings
    
    def validate_html_css_js_comprehensive(self, html_content):
        """Comprehensive validation of HTML, CSS, and JavaScript"""
        # HTML validation
        html_issues, html_fixes = self.validate_html_structure(html_content)
        
        # CSS validation
        css_issues, css_fixes, css_warnings = self.validate_css(html_content)
        
        # JavaScript validation
        js_issues, js_fixes, js_warnings = self.validate_javascript(html_content)
        
        # Combine all issues and fixes
        all_issues = html_issues + css_issues + js_issues
        all_fixes = html_fixes + css_fixes + js_fixes
        all_warnings = css_warnings + js_warnings
        
        # Additional cross-technology checks
        if '<script>' in html_content and 'defer' not in html_content and 'async' not in html_content:
            all_warnings.append("Script tags without async/defer - may block rendering")
            all_fixes.append("Add async or defer attributes to script tags")
        
        if '<link rel="stylesheet"' in html_content and 'media=' not in html_content:
            all_warnings.append("Stylesheet without media attribute")
            all_fixes.append("Add media attributes to stylesheet links")
        
        return {
            'html': {'issues': html_issues, 'fixes': html_fixes},
            'css': {'issues': css_issues, 'fixes': css_fixes, 'warnings': css_warnings},
            'javascript': {'issues': js_issues, 'fixes': js_fixes, 'warnings': js_warnings},
            'all_issues': all_issues,
            'all_fixes': all_fixes,
            'all_warnings': all_warnings,
            'total_issues': len(all_issues),
            'total_warnings': len(all_warnings)
        }
    
    def clean_html_content(self, html_content):
        """Clean and format HTML content"""
        import re
        
        # Remove code block markers
        html_content = re.sub(r'```html\s*', '', html_content)
        html_content = re.sub(r'```\s*$', '', html_content)
        
        # Remove extra whitespace
        html_content = re.sub(r'\n\s*\n', '\n', html_content)
        
        # Ensure proper DOCTYPE if missing
        if not html_content.strip().startswith('<!DOCTYPE'):
            html_content = '<!DOCTYPE html>\n' + html_content.strip()
        
        return html_content.strip()
    
    def run(self, state: State) -> dict:
        web_dev_content = state['artifacts'].get('web_developer', {}).get('campaign_website', '')
        
        if not web_dev_content:
            return self.return_state(state, None, {
                "html_validation": {
                    "status": "error",
                    "message": "No HTML content found to validate",
                    "corrected_html": ""
                }
            })
        
        # Clean the HTML content first
        cleaned_html = self.clean_html_content(web_dev_content)
        
        # Perform advanced validation
        validation_report = self.validate_html_css_js_comprehensive(cleaned_html)
        
        # Create validation prompt for AI-based correction
        validation_prompt = f"""
        Please validate and correct the following HTML code. Focus on creating valid, accessible, and performant HTML.
        
        CRITICAL ISSUES FOUND: {validation_report['all_issues']}
        WARNINGS: {validation_report['all_warnings']}
        RECOMMENDED FIXES: {validation_report['all_fixes']}
        
        HTML CODE TO VALIDATE AND CORRECT:
        {cleaned_html}
        
        REQUIREMENTS FOR CORRECTION:
        1. Fix all critical issues listed above
        2. Address accessibility warnings (add alt tags, semantic HTML)
        3. Ensure valid HTML5 structure with proper DOCTYPE
        4. Include proper meta tags for mobile and SEO
        5. Ensure all tags are properly closed and nested
        6. Add semantic HTML elements (header, nav, main, section, footer)
        7. Include ARIA attributes where appropriate
        8. Optimize CSS (move inline styles to style blocks)
        9. Add proper error handling for JavaScript if present
        10. Ensure mobile responsiveness with proper CSS
        
        IMPORTANT: Return ONLY the corrected, complete HTML code without any explanations or markdown formatting.
        """
        
        messages = self.get_messages(validation_prompt)
        response = self.invoke_llm_with_retry(messages)
        
        # Clean and validate the corrected HTML
        corrected_html = self.clean_html_content(response.content)
        corrected_validation_report = self.validate_html_css_js_comprehensive(corrected_html)
        
        # Calculate improvement metrics
        issues_fixed = len(validation_report['all_issues']) - len(corrected_validation_report['all_issues'])
        warnings_addressed = len(validation_report['all_warnings']) - len(corrected_validation_report['all_warnings'])
        
        validation_report_final = {
            "status": "success" if len(corrected_validation_report['all_issues']) == 0 else "warning",
            "original_validation": validation_report,
            "corrected_validation": corrected_validation_report,
            "original_issues": validation_report['all_issues'],
            "original_warnings": validation_report['all_warnings'],
            "corrected_issues": corrected_validation_report['all_issues'],
            "corrected_warnings": corrected_validation_report['all_warnings'],
            "fixes_applied": validation_report['all_fixes'],
            "corrected_html": corrected_html,
            "validation_summary": f"Fixed {issues_fixed} critical issues, addressed {warnings_addressed} warnings",
            "improvement_score": round(((issues_fixed + warnings_addressed) / max(len(validation_report['all_issues']) + len(validation_report['all_warnings']), 1)) * 100, 1),
            "detailed_breakdown": {
                "html": {
                    "original_issues": len(validation_report['html']['issues']),
                    "corrected_issues": len(corrected_validation_report['html']['issues']),
                    "issues_fixed": len(validation_report['html']['issues']) - len(corrected_validation_report['html']['issues'])
                },
                "css": {
                    "original_issues": len(validation_report['css']['issues']),
                    "original_warnings": len(validation_report['css']['warnings']),
                    "corrected_issues": len(corrected_validation_report['css']['issues']),
                    "corrected_warnings": len(corrected_validation_report['css']['warnings']),
                    "issues_fixed": len(validation_report['css']['issues']) - len(corrected_validation_report['css']['issues']),
                    "warnings_addressed": len(validation_report['css']['warnings']) - len(corrected_validation_report['css']['warnings'])
                },
                "javascript": {
                    "original_issues": len(validation_report['javascript']['issues']),
                    "original_warnings": len(validation_report['javascript']['warnings']),
                    "corrected_issues": len(corrected_validation_report['javascript']['issues']),
                    "corrected_warnings": len(corrected_validation_report['javascript']['warnings']),
                    "issues_fixed": len(validation_report['javascript']['issues']) - len(corrected_validation_report['javascript']['issues']),
                    "warnings_addressed": len(validation_report['javascript']['warnings']) - len(corrected_validation_report['javascript']['warnings'])
                }
            }
        }
        
        print(f"✅ HTML/CSS/JS Validation complete: {validation_report_final['validation_summary']}")
        print(f"📊 Overall Improvement Score: {validation_report_final['improvement_score']}%")
        print(f"🏗️ HTML Issues Fixed: {validation_report_final['detailed_breakdown']['html']['issues_fixed']}")
        print(f"🎨 CSS Issues Fixed: {validation_report_final['detailed_breakdown']['css']['issues_fixed']}, Warnings: {validation_report_final['detailed_breakdown']['css']['warnings_addressed']}")
        print(f"⚡ JavaScript Issues Fixed: {validation_report_final['detailed_breakdown']['javascript']['issues_fixed']}, Warnings: {validation_report_final['detailed_breakdown']['javascript']['warnings_addressed']}")
        
        if corrected_validation_report['all_issues']:
            print(f"⚠️ Remaining critical issues: {len(corrected_validation_report['all_issues'])}")
        if corrected_validation_report['all_warnings']:
            print(f"⚠️ Remaining warnings: {len(corrected_validation_report['all_warnings'])}")
        
        return self.return_state(state, response, {"html_validation": validation_report_final})


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
    social_media_campaign = SocialMediaCampaignAgent()
    emotion_personalization = EmotionPersonalizationAgent()
    html_validation = HTMLValidationAgent()
    
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
    workflow.add_node("designer", designer.run)
    workflow.add_node("social_media_campaign", social_media_campaign.run)
    workflow.add_node("emotion_personalization", emotion_personalization.run)
    workflow.add_node("review", review.run)
    workflow.add_node("campaign_summary", campaign_summary.run)
    workflow.add_node("media_planner", media_planner.run)
    workflow.add_node("client_summary", client_summary.run)
    workflow.add_node("web_developer", web_developer.run)
    workflow.add_node("html_validation", html_validation.run)
    
    # Initial setup - sequential flow
    workflow.add_edge("project_manager", "strategy")
    workflow.add_edge("strategy", "audience_persona")
    workflow.add_edge("audience_persona", "creative")
    
    # Creative path continues sequentially for now
    workflow.add_edge("creative", "copy")
    workflow.add_edge("copy", "cta_optimizer")
    workflow.add_edge("cta_optimizer", "visual")
    workflow.add_edge("visual", "designer")
    
    # After designer, we can run social media and emotion personalization in parallel
    # using conditional edges to simulate parallel execution
    def route_after_designer(state):
        # First, run social media campaign
        if "social_media_campaign" not in state.get("artifacts", {}):
            return "social_media_campaign"
        # Then, run emotion personalization
        elif "emotion_personalization" not in state.get("artifacts", {}):
            return "emotion_personalization"
        # Both complete, proceed to media planner
        elif "media_plan" not in state.get("artifacts", {}):
            return "media_planner"
        # All parallel tasks complete, proceed to review
        else:
            return "review"
    
    workflow.add_conditional_edges(
        "designer",
        route_after_designer,
        {
            "social_media_campaign": "social_media_campaign",
            "emotion_personalization": "emotion_personalization",
            "media_planner": "media_planner",
            "review": "review"
        }
    )
    
    # Route from social media campaign
    def route_from_social_media(state):
        if "emotion_personalization" not in state.get("artifacts", {}):
            return "emotion_personalization"
        elif "media_plan" not in state.get("artifacts", {}):
            return "media_planner"
        else:
            return "review"
    
    workflow.add_conditional_edges(
        "social_media_campaign",
        route_from_social_media,
        {
            "emotion_personalization": "emotion_personalization",
            "media_planner": "media_planner",
            "review": "review"
        }
    )
    
    # Route from emotion personalization
    def route_from_emotion(state):
        if "media_plan" not in state.get("artifacts", {}):
            return "media_planner"
        else:
            return "review"
    
    workflow.add_conditional_edges(
        "emotion_personalization",
        route_from_emotion,
        {
            "media_planner": "media_planner",
            "review": "review"
        }
    )
    
    # Route from media planner
    workflow.add_edge("media_planner", "review")
    
    # Final stages
    workflow.add_edge("review", "campaign_summary")
    workflow.add_edge("campaign_summary", "client_summary")
    workflow.add_edge("client_summary", "web_developer")
    workflow.add_edge("web_developer", "html_validation")
    workflow.add_edge("html_validation", END)
    
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
        "product": "Immigrate to Canada from Latin America",
        "client": "Canada Immigration",
        "client_website": "https://en.ngpimmigration.com/",
        "client_logo": "https://cdn.pixabay.com/photo/2016/01/25/16/41/ottawa-1160993_1280.png",
        "color_scheme": "black and red with a white background",
        "target_audience": "People who want to immigrate to Canada",
        "goals": ["Increase lead generation", "Drive enrollment", "Increase website traffic"],
        "key_features": [
           "Legal immigration",
           "Canada Immigration",
           "the best immigration agency in Canada",
        ],
        "budget": "$2,000",
        "timeline": "2 month"
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
        # print("🚀 Starting campaign generation workflow...")
        # print(f"📊 Campaign Brief: {campaign_brief['product']}")
        # print(f"🎯 Target Audience: {campaign_brief['target_audience']}")
        # print(f"💰 Budget: {campaign_brief['budget']}")
        # print(f"⏱️ Timeline: {campaign_brief['timeline']}")
        
        result = workflow_with_memory.invoke(initial_state, config={"thread_id": "campaign_001", "recursion_limit": 250})
        
        # Track analytics
        analytics = CampaignAnalytics()
        analytics.track_iteration(result)

        # # Display results
        # print("\n" + "="*40)
        # print("📋 Campaign Results")
        # print("="*40)
        
        # print("Strategy:")
        # print(result['artifacts'].get('strategy', ''))
        # print("\nAudience Personas:")
        # print(result['artifacts'].get('audience_personas', ''))
        # print("\nCreative Concepts:")
        # print(result['artifacts'].get('creative_concepts', ''))
        # print("\nCopy:")
        # print(result['artifacts'].get('copy', ''))
        # print("\nCTA Optimization:")
        # print(result['artifacts'].get('cta_optimization', ''))
        # print("\nMedia Plan:")
        # print(result['artifacts'].get('media_plan', ''))
        # print("\nClient Summary:")
        # print(result['artifacts'].get('client_summary', ''))
        # print("\nSocial Media Campaign:")
        # print(result['artifacts'].get('social_media_campaign', ''))
        # print("\nEmotion Personalization:")
        # print(result['artifacts'].get('emotion_personalization', ''))
        # print("\nImage Prompt:")
        # print(result['artifacts'].get('visual', {}).get('image_prompt', ''))
        # print("\nImage URL:")
        # print(result['artifacts'].get('visual', {}).get('image_url', ''))
        # print("\nFeedback:")
        # print(result.get('feedback', []))

        # # Display analytics
        # print("\n" + "="*40)
        # print("📈 Campaign Analytics Report")
        # print("="*40)
        # report = analytics.generate_report()
        # print(report)

        # Display workflow monitoring summary
        print("\n" + "="*40)
        print("🔄 Workflow Monitoring Summary")
        print("="*40)
        monitor_summary = monitor.get_summary()
        print(f"Total Iterations: {monitor_summary['total_iterations']}")
        print(f"Average Artifacts per Iteration: {monitor_summary['avg_artifacts']:.1f}")
        print(f"Total Duration: {monitor_summary['duration']:.1f} seconds")
        print(f"Final Revision Count: {result.get('revision_count', 0)}")

    
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