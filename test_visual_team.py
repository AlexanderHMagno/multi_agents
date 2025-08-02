from agentic_ad_generation import VisualTeam  # adjust import if needed
from pprint import pprint

# Sample input state
state = {
    "messages": [],
    "campaign_brief": {
        "goal": "Promote new eco-friendly forklifts",
        "target_audience": "Construction companies in Canada"
    },
    "artifacts": {
        "strategy": "Emphasize durability and eco-savings.",
        "creative_concepts": "A powerful machine on a clean forest background."
    },
    "feedback": [],
    "revision_count": 0
}

# Initialize and run agent
agent = VisualTeam()
result = agent.run(state)

# Print image prompt and URL
pprint(result["artifacts"].get("visual", {}))
