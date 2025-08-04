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
from PDFgenerator import generate_campaign_pdf

# Load environment variables
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_API_KEY = os.getenv("DALLE_API_KEY")
RATIONAL_MODEL = os.getenv("RATIONAL_MODEL")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
client = OpenAI(api_key=DALLE_API_KEY)

# Verify API keys are loaded
if not OPENAI_API_KEY or not DALLE_API_KEY or not RATIONAL_MODEL or not IMAGE_MODEL:
    raise ValueError("Please ensure both OPENAI_API_KEY and DALLE_API_KEY are set in your .env file")

print(f"RATIONAL_MODEL: {RATIONAL_MODEL}")

# Initialize LLM
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
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
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Image saved to {filename}")
    else:
        print("❌ Failed to download image")

def create_workflow():
    # Initialize teams
    pm = ProjectManager()
    strategy = StrategyTeam()
    creative = CreativeTeam()
    copy = CopyTeam()
    visual = VisualTeam()
    review = ReviewTeam()
    
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
    
    # Define edges
    workflow.add_edge("project_manager", "strategy")
    workflow.add_edge("strategy", "creative")
    workflow.add_edge("creative", "copy")
    workflow.add_edge("copy", "visual")
    workflow.add_edge("visual", END)
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
        "product": "Eco-friendly Water Bottle",
        "target_audience": "Environmentally conscious millennials",
        "goals": ["Increase brand awareness", "Drive online sales"],
        "key_features": [
            "Made from recycled materials",
            "Keeps drinks cold for 24 hours",
            "Portion of profits goes to ocean cleanup"
        ],
        "budget": "$50,000",
        "timeline": "4 weeks"
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
    config = {"configurable": {"thread_id": "eco-bottle-campaign"}}
    try:
  
        result = workflow_with_memory.invoke(initial_state, config={"thread_id": "campaign_001", "recursion_limit": 100})
        
        # ⬇️ At the end, after review is done
        visual_prompt = result["artifacts"].get("visual", {}).get("image_prompt", "")
   
        if visual_prompt:
            print("[🎨] Generating image from visual prompt...")
            if len(visual_prompt) > 3800:
                visual_prompt = visual_prompt[:3800] + "..."

            try:
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=visual_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = image_response.data[0].url
                result["artifacts"]["visual"] = {
                    "image_prompt": visual_prompt,
                    "image_url": image_url
                }
                download_image(image_url)  # Optional
                print("[✅] Image generated successfully.")
            except Exception as e:
                result["artifacts"]["visual"] = {
                    "image_prompt": visual_prompt,
                    "image_url": None
                }
                print(f"[❌ Visual] Failed to generate image: {e}")

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

        # Include revision_count in artifacts for PDF
        result['artifacts']['revision_count'] = result.get('revision_count', 0)
        generate_campaign_pdf(result , "final_campaign.pdf")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 