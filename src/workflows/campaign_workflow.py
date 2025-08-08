"""
Campaign Workflow Definition

This module defines the main campaign generation workflow using LangGraph,
including agent orchestration, conditional routing, and quality control.
"""

from langgraph.graph import StateGraph, END, START
from ..agents import *
from ..utils.state import State
from ..utils.monitoring import WorkflowMonitor, QualityChecker


def smart_revision_router(state, monitor: WorkflowMonitor):
    """
    Comprehensive revision router with multiple safeguards to prevent infinite loops
    
    Args:
        state: Current workflow state
        monitor: WorkflowMonitor instance for timeout checking
        
    Returns:
        str: Next node to route to or "complete" to end workflow
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
        last_feedback = str(feedback[-1]).lower()
        
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


def create_workflow(llm, openai_client):
    """
    Create the main campaign generation workflow with all agents and routing logic.
    
    Args:
        llm: ChatOpenAI instance for LLM interactions
        openai_client: OpenAI client for DALL-E image generation
        
    Returns:
        tuple: (StateGraph workflow, WorkflowMonitor instance)
    """
    
    # Initialize all agents
    project_manager = ProjectManager(llm)
    strategy = StrategyTeam(llm)
    audience_persona = AudiencePersonaAgent(llm)
    creative = CreativeTeam(llm)
    copy = CopyTeam(llm)
    cta_optimizer = CTAOptimizer(llm)
    visual = VisualTeam(llm)
    designer = DesignerTeam(llm, openai_client)
    social_media_campaign = SocialMediaCampaignAgent(llm)
    emotion_personalization = EmotionPersonalizationAgent(llm)
    media_planner = MediaPlanner(llm)
    review = ReviewTeam(llm)
    campaign_summary = CampaignSummaryAgent(llm)
    client_summary = ClientSummaryGenerator(llm)
    web_developer = WebDeveloper(llm)
    pdf_generator = PDFGeneratorTeam(llm)
    html_validation = HTMLValidationAgent(llm)
    
    # Create workflow graph
    workflow = StateGraph(State)
    
    # Add all nodes
    workflow.add_edge(START, "project_manager")
    workflow.add_node("project_manager", project_manager.run)
    workflow.add_node("strategy", strategy.run)
    workflow.add_node("audience_persona", audience_persona.run)
    workflow.add_node("creative", creative.run)
    workflow.add_node("copy", copy.run)
    workflow.add_node("cta_optimizer", cta_optimizer.run)
    workflow.add_node("visual", visual.run)
    workflow.add_node("designer", designer.run)
    workflow.add_node("social_media_campaign", social_media_campaign.run)
    workflow.add_node("emotion_personalization", emotion_personalization.run)
    workflow.add_node("media_planner", media_planner.run)
    workflow.add_node("review", review.run)
    workflow.add_node("campaign_summary", campaign_summary.run)
    workflow.add_node("client_summary", client_summary.run)
    workflow.add_node("web_developer", web_developer.run)
    workflow.add_node("html_validation", html_validation.run)
    # workflow.add_node("pdf_generator", pdf_generator.run)  # Commented out as per user's edit
    
    # Sequential workflow path
    workflow.add_edge("project_manager", "strategy")
    workflow.add_edge("strategy", "audience_persona")
    workflow.add_edge("audience_persona", "creative")
    workflow.add_edge("creative", "copy")
    workflow.add_edge("copy", "cta_optimizer")
    workflow.add_edge("cta_optimizer", "visual")
    workflow.add_edge("visual", "designer")
    
    # Parallel execution simulation after designer
    def route_after_designer(state):
        """Route to parallel tasks after designer completion"""
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
        """Route from social media campaign to remaining parallel tasks"""
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
        """Route from emotion personalization to remaining parallel tasks"""
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
    
    # Route from media planner to review
    workflow.add_edge("media_planner", "review")
    
    # Final sequential stages
    workflow.add_edge("review", "campaign_summary")
    workflow.add_edge("campaign_summary", "client_summary")
    workflow.add_edge("client_summary", "web_developer")
    workflow.add_edge("web_developer", END)
    # workflow.add_edge("html_validation", END)
    # workflow.add_edge("html_validation", "pdf_generator")  # Commented out
    # workflow.add_edge("pdf_generator", END)  # Commented out
    
    # Initialize workflow monitor
    monitor = WorkflowMonitor(max_duration=300)  # 5 minutes
    
    # Add conditional edges for feedback loops with smart routing
    def create_smart_router(monitor):
        """Create a smart router function with monitor closure"""
        return lambda state: smart_revision_router(state, monitor)
    
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