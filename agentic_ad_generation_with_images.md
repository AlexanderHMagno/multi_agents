
# 🧠 Agentic Ad Generation with Image Support using LangChain + LangGraph

This guide demonstrates building an advanced **multi-agent ad generation system** with sophisticated collaboration patterns and feedback loops using **LangChain** and **LangGraph**.

---

## 🚀 Overview

The system implements a collaborative multi-agent workflow that:

1. Analyzes campaign requirements (Strategy Agent)
2. Brainstorms creative concepts (Creative Team)
3. Generates and refines copy (Copy Team)
4. Creates matching visuals (Visual Team)
5. Evaluates and iterates on results (Review Team)
6. Coordinates all activities (Project Manager Agent)

---

## 📦 Requirements

```bash
pip install langchain langgraph openai python-dotenv
```

Required environment variables:
```bash
OPENAI_API_KEY=your_key_here
DALLE_API_KEY=your_key_here  # If using DALL-E
```

---

## 🧱 Step 1: Define Your Agent Teams

### 1. Project Manager Agent

Coordinates the entire workflow and maintains project state.

```python
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate

pm_prompt = PromptTemplate.from_template("""
You are the project manager coordinating an ad campaign creation.
Current project state: {project_state}
Next steps needed: {next_steps}
Team feedback: {feedback}

Decide on the next action:
1. Assign new tasks
2. Request revisions
3. Move to next phase
4. Complete project

Response format:
{
    "action": "selected_action",
    "assignments": {},
    "feedback": ""
}
""")

pm_agent = AgentExecutor.from_agent_and_tools(
    agent=create_agent(pm_prompt),
    tools=[assign_task, request_revision, advance_phase]
)
```

### 2. Strategy Team

Analyzes campaign goals, target audience, and market context.

```python
strategy_prompt = PromptTemplate.from_template("""
Analyze the campaign requirements:
Campaign brief: {brief}
Market data: {market_data}
Previous campaigns: {history}

Provide strategic recommendations for:
1. Target audience segments
2. Key messaging points
3. Brand positioning
4. Success metrics

Response format:
{
    "strategy": {},
    "recommendations": [],
    "risks": []
}
""")

strategy_agent = AgentExecutor.from_agent_and_tools(
    agent=create_agent(strategy_prompt),
    tools=[analyze_market, get_campaign_history]
)
```

### 3. Creative Team

Collaborative agents for ideation and concept development.

```python
from langchain.agents import Tool
from typing import List

class CreativeTeam:
    def __init__(self):
        self.brainstormer = self._create_brainstormer()
        self.concept_developer = self._create_concept_developer()
        self.critic = self._create_critic()
    
    def collaborate(self, brief: dict) -> List[dict]:
        ideas = self.brainstormer.run(brief)
        concepts = self.concept_developer.run(ideas)
        feedback = self.critic.run(concepts)
        return self._refine_concepts(concepts, feedback)
```

### 4. Copy Team

Multiple agents working on different copy elements with peer review.

```python
copy_system = """
You are part of a copywriting team. Each member specializes in different aspects:
- Headlines
- Body copy
- Call-to-action
- SEO optimization

Work together to create compelling copy that aligns with the creative concept.
"""

class CopyTeam:
    def __init__(self):
        self.specialists = {
            "headline": create_copy_specialist("headline"),
            "body": create_copy_specialist("body"),
            "cta": create_copy_specialist("cta"),
            "seo": create_copy_specialist("seo")
        }
        self.reviewer = create_copy_reviewer()
    
    def generate_copy(self, concept: dict) -> dict:
        versions = self._create_initial_versions(concept)
        feedback = self._peer_review(versions)
        return self._finalize_copy(versions, feedback)
```

### 5. Visual Team

Coordinated image generation and optimization.

```python
from langchain_community.utilities import DallEAPIWrapper

class VisualTeam:
    def __init__(self):
        self.prompt_engineer = self._create_prompt_engineer()
        self.image_generator = DallEAPIWrapper()
        self.image_optimizer = self._create_image_optimizer()
    
    def create_visuals(self, concept: dict, copy: dict) -> dict:
        prompt = self.prompt_engineer.generate_prompt(concept, copy)
        raw_image = self.image_generator.run(prompt)
        return self.image_optimizer.optimize(raw_image)
```

### 6. Review Team

Multi-perspective evaluation and feedback system.

```python
class ReviewTeam:
    def __init__(self):
        self.brand_reviewer = self._create_brand_reviewer()
        self.creative_reviewer = self._create_creative_reviewer()
        self.technical_reviewer = self._create_technical_reviewer()
    
    def evaluate(self, campaign: dict) -> dict:
        brand_feedback = self.brand_reviewer.review(campaign)
        creative_feedback = self.creative_reviewer.review(campaign)
        technical_feedback = self.technical_reviewer.review(campaign)
        
        return self._consolidate_feedback(
            brand_feedback,
            creative_feedback,
            technical_feedback
        )
```

---

## 🔁 Step 2: Implement Collaboration Patterns

```python
from langgraph.graph import Graph, Node
from langgraph.prebuilt import SequentialGraph

def create_workflow():
    # Create nodes for each team
    nodes = {
        "pm": Node(pm_agent, name="project_manager"),
        "strategy": Node(strategy_agent, name="strategy"),
        "creative": Node(creative_team.collaborate, name="creative"),
        "copy": Node(copy_team.generate_copy, name="copy"),
        "visual": Node(visual_team.create_visuals, name="visual"),
        "review": Node(review_team.evaluate, name="review")
    }
    
    # Define the workflow graph
    graph = Graph()
    
    # Add basic flow
    graph.add_edge(nodes["pm"], nodes["strategy"])
    graph.add_edge(nodes["strategy"], nodes["creative"])
    graph.add_edge(nodes["creative"], nodes["copy"])
    graph.add_edge(nodes["copy"], nodes["visual"])
    graph.add_edge(nodes["visual"], nodes["review"])
    graph.add_edge(nodes["review"], nodes["pm"])
    
    # Add feedback loops
    graph.add_feedback_edge(
        nodes["review"],
        nodes["creative"],
        condition=lambda x: x["score"] < 0.8
    )
    
    graph.add_feedback_edge(
        nodes["review"],
        nodes["copy"],
        condition=lambda x: x["copy_score"] < 0.8
    )
    
    return graph

# Create the workflow
workflow = create_workflow()
```

---

## 🎯 Running the System

```python
def run_campaign(brief: dict):
    # Initialize the campaign state
    state = {
        "brief": brief,
        "phase": "strategy",
        "iterations": 0,
        "feedback": [],
        "artifacts": {}
    }
    
    # Run the workflow
    result = workflow.run(state)
    
    return {
        "campaign": result["artifacts"],
        "metrics": result["metrics"],
        "history": result["history"]
    }

# Example usage
campaign_brief = {
    "product": "Eco-friendly water bottle",
    "target_audience": "Environmentally conscious millennials",
    "goals": ["Increase brand awareness", "Drive online sales"],
    "budget": "50000",
    "timeline": "4 weeks"
}

result = run_campaign(campaign_brief)
```

---

## 📊 Monitoring and Analytics

```python
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
        self._update_team_metrics(state)
        self._update_quality_scores(state)
        self._update_timing(state)
    
    def generate_report(self) -> dict:
        return {
            "summary": self._generate_summary(),
            "recommendations": self._generate_recommendations(),
            "performance": self.metrics
        }
```

---

## 🔄 Continuous Improvement

The system includes several mechanisms for continuous improvement:

1. **Learning from History**
   - Each campaign's process and results are stored
   - Agents can reference past campaigns for context
   - Performance metrics guide future decisions

2. **Adaptive Workflows**
   - Dynamic routing based on feedback
   - Automatic task prioritization
   - Resource optimization

3. **Quality Control**
   - Multi-level review process
   - Automated quality checks
   - Performance tracking

---

## 🛠 Advanced Features

1. **A/B Testing Integration**
   - Automatic variant generation
   - Performance tracking
   - Statistical analysis

2. **Human-in-the-Loop Options**
   - Review checkpoints
   - Manual override capabilities
   - Feedback incorporation

3. **API Integration**
   - REST API endpoints
   - Webhook support
   - Event streaming

---

## 📚 References

- LangChain Documentation: https://python.langchain.com
- LangGraph GitHub: https://github.com/langchain-ai/langgraph
- OpenAI API: https://platform.openai.com/docs
- DALL-E API: https://platform.openai.com/docs/guides/images
