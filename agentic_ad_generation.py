#!/usr/bin/env python3

import os
import requests
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
from pdf_generator import generate_formatted_pdf



# Load environment variables
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_API_KEY = os.getenv("DALLE_API_KEY")
# RATIONAL_MODEL = os.getenv("RATIONAL_MODEL")
RATIONAL_MODEL = "google/gemini-2.5-flash-lite"
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
client = OpenAI(api_key=DALLE_API_KEY)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")

# Verify API keys are loaded
if not OPENAI_API_KEY or not DALLE_API_KEY or not RATIONAL_MODEL or not IMAGE_MODEL:
    raise ValueError("Please ensure both OPENAI_API_KEY and DALLE_API_KEY are set in your .env file")

print(f"RATIONAL_MODEL: {RATIONAL_MODEL}")

# # Initialize LLM
# llm = ChatOpenAI(
#     openai_api_key=OPENAI_API_KEY,
#     model_name=RATIONAL_MODEL,
#     temperature=0.7
# )

#Open router for LLM


llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    model_name=RATIONAL_MODEL,
    temperature=0.7
)

# Define state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]
    campaign_brief: dict
    artifacts: Annotated[dict, {}]
    feedback: Annotated[list, add_messages]
    revision_count: int

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
                **(new_artifacts or {})  # merge only if new_artifacts is provided
            },
            "feedback": [*state.get("feedback", []), *(feedback or [])],
            "revision_count": state.get("revision_count", 0),
            "campaign_brief": state["campaign_brief"],
        }

# Project Manager Agent
class ProjectManager(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a project manager coordinating an ad campaign creation.
            Your role is to oversee the entire workflow and ensure all teams are aligned.
            Analyze the current state and decide on next actions."""
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
        self.client = openai_client

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
            system_prompt="""You are the web developer responsible for creating the ad landing page.
            Create a landing page for the ad that is responsive and mobile-friendly.
            Using HTML, CSS, and JavaScript, create a landing page for the ad that is responsive and mobile-friendly."""
        )
    
    def run(self, state: State) -> dict:
        visual_data = state['artifacts'].get("visual", {})
        visual_prompt = visual_data.get("image_prompt", "")
        image_url = visual_data.get("image_url", "")
        campaign_summary = state['artifacts'].get('campaign_summary', '')
        messages = self.get_messages(f"Create a landing page for the ad with this campaign summary: {campaign_summary} as the content. The ad image is {image_url}.")
        response = self.llm.invoke(messages)
        print(f"Landing page: {response.content}")
        return self.return_state(state, response, {"web_developer": {"landing_page": response.content}})

class PDFGeneratorTeam(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a PDF generation assistant. Based on the full campaign summary, generate a polished, professional summary suitable for sharing with stakeholders. Format the content cleanly and prepare it for layout."""
        )

    def run(self, state: State) -> dict:
        summary = state['artifacts'].get('campaign_summary', '')
        image_url = state['artifacts'].get('visual', {}).get('image_url', '')
        messages = self.get_messages(f"Generate a PDF-ready report from this campaign summary:\n\n{summary}. The ad image is src {image_url}. generate the pdf using reportlab python library syntax")
        response = self.llm.invoke(messages)    

        # Save formatted content or HTML as artifact for rendering
        return self.return_state(state, response, {
            "pdf_report": {
                "formatted_content": response.content
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
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(landing_page_content)
            print(f"✅ Landing page saved as {filename}")
        except Exception as e:
            print(f"❌ Failed to save landing page: {e}")
    else:
        print("❌ No landing page content found in artifacts")




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
    
    # Create graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_edge(START, "project_manager")
    workflow.add_node("project_manager", pm.run)
    workflow.add_node("strategy", strategy.run)
    workflow.add_node("creative", creative.run)
    workflow.add_node("copy", copy.run)
    workflow.add_node("visual", visual.run)
    workflow.add_node("review", review.run)
    workflow.add_node("web_developer", web_developer.run)
    workflow.add_node("designer", designer.run)
    workflow.add_node("campaign_summary", campaign_summary.run)
    workflow.add_node("pdf_generator", pdf_generator.run)
    # Define edges
    workflow.add_edge("project_manager", "strategy")
    workflow.add_edge("strategy", "creative")
    workflow.add_edge("creative", "copy")
    workflow.add_edge("copy", "visual")
    workflow.add_edge("visual", "designer")
    workflow.add_edge("designer", "campaign_summary")
    workflow.add_edge("campaign_summary", "web_developer")
    workflow.add_edge("web_developer", "pdf_generator")
    workflow.add_edge("pdf_generator", END)
    # workflow.add_edge("review", "project_manager")
    
    # # Add conditional edges for feedback loops
    # def needs_revision(state):
    #     feedback = state.get("feedback", [])
    #     revision_count = state.get("revision_count", 0)

    #     if revision_count >= 3:
    #         print("⚠️ Max revisions reached. Completing workflow.")
    #         return "complete"

    #     if feedback:
    #         last = feedback[-1].lower()

    #         if "copy" in last:
    #             return "copy"
    #         elif "visual" in last:
    #             return "visual"
    #         elif "strategy" in last or "revise" in last:
    #             return "strategy"

    #     return "complete"
    
    # workflow.add_conditional_edges(
    #     "project_manager",
    #     needs_revision,
    #     {
    #         "strategy": "strategy",
    #         "copy": "copy",
    #         "visual": "visual",
    #         "complete": END
    #     }
    # )

    return workflow

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

    # Initialize state
    initial_state = {
        "messages": [],
        "campaign_brief": campaign_brief,
        "artifacts": {},
        "feedback": [],
        "revision_count": 0
    }

    # Create workflow with memory
    memory = MemorySaver()
    workflow = create_workflow()
    workflow_with_memory = workflow.compile(checkpointer=memory)

    # Run workflow
    config = {"configurable": {"thread_id": "forklift-campaign"}}
    try:
  
        result = workflow_with_memory.invoke(initial_state, config={"thread_id": "campaign_001", "recursion_limit": 100})
        
  
        # Track analytics
        analytics = CampaignAnalytics()
        analytics.track_iteration(result)

        # Display results
        print("Campaign Results:\n")
        print("Strategy:")
        print(result['artifacts'].get('strategy', ''))
        print("\nCreative Concepts:")
        print(result['artifacts'].get('creative_concepts', ''))
        print("\nCopy:")
        print(result['artifacts'].get('copy', ''))
        print("\nImage Prompt:")
        print(result['artifacts'].get('visual', {}).get('image_prompt', ''))
        print("\nImage URL:")
        print(result['artifacts'].get('visual', {}).get('image_url', ''))
        print("\nFeedback:")
        print(result.get('feedback', []))

        # Display analytics
        print("="*40)
        print("📈 Campaign Analytics Report")
        print("="*40)
        report = analytics.generate_report()
        print(report)

        #download image
        # download_image(result['artifacts'].get('visual', {}).get('image_url', ''))

        # Include revision_count in artifacts for PDF
        generate_formatted_pdf(result, "final_campaign.pdf")

        # Generate landing page
        create_landing_page(result)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 