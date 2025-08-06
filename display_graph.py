from agentic_ad_generation import create_workflow
from IPython.display import Image, display

try:
    graph, _ = create_workflow()
    workflow_with_memory = graph.compile()
    # Generate and save the Mermaid PNG
    png_bytes = workflow_with_memory.get_graph().draw_mermaid_png()
    output_path = "workflow_graph.png"

    # Write PNG file to disk
    with open(output_path, "wb") as f:
        f.write(png_bytes)

    print(f"✅ Saved: {output_path}")
except Exception:
    # This requires some extra dependencies and is optional
    pass