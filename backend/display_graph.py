#!/usr/bin/env python3
"""
Workflow Graph Visualization

This script generates a visual representation of the multi-agent workflow
as a Mermaid diagram and saves it as a PNG file.

Usage:
    python display_graph.py
"""

from src.utils.config import load_configuration
from src.workflows.campaign_workflow import create_workflow

def main():
    """Generate and save the workflow graph visualization"""
    try:
        # Load configuration
        config = load_configuration()
        llm = config["llm"]
        openai_client = config["openai_client"]
        
        # Create workflow
        print("🔧 Creating workflow graph...")
        graph, _ = create_workflow(llm, openai_client)
        workflow_with_memory = graph.compile()
        
        # Generate and save the Mermaid PNG
        print("📊 Generating workflow visualization...")
        png_bytes = workflow_with_memory.get_graph().draw_mermaid_png()
        output_path = "workflow_graph.png"

        # Write PNG file to disk
        with open(output_path, "wb") as f:
            f.write(png_bytes)

        print(f"✅ Workflow graph saved: {output_path}")
        
    except ImportError as e:
        print(f"⚠️ Missing optional dependencies for graph visualization: {e}")
        print("💡 Install with: pip install graphviz pygraphviz")
        
    except Exception as e:
        print(f"❌ Error generating workflow graph: {e}")
        print("💡 This feature requires additional dependencies and is optional")

if __name__ == "__main__":
    main()