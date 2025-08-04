from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import traceback
import os
from src.ad_generation import AdAgent, ToneStyle
from agentic_ad_generation import create_workflow, CampaignAnalytics, download_image, client
from PDFgenerator import generate_campaign_pdf
from langgraph.checkpoint.memory import MemorySaver

app = Flask(__name__)
CORS(app)
load_dotenv()

ad_agent = AdAgent()

@app.route("/generate", methods=["POST"])
def generate_ad():
    try:
        data = request.json
        raw_text = data.get("raw_text")
        tone_style = data.get("tone_style")
        temperature = float(data.get("temperature", 0.7))
        max_length = int(data.get("max_length", 1000))

        tone_enum = ToneStyle(tone_style) if tone_style else None

        result = ad_agent.generate_ad_from_raw_text(
            raw_text, tone_enum, temperature=temperature, max_length=max_length
        )

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/run_campaign", methods=["POST"])
def run_campaign():
    try:
        data = request.json
        campaign_brief = data.get("campaign_brief")

        if not campaign_brief:
            return jsonify({"error": "Missing 'campaign_brief' in request"}), 400

        initial_state = {
            "messages": [],
            "campaign_brief": campaign_brief,
            "artifacts": {},
            "feedback": [],
            "revision_count": 0
        }

        memory = MemorySaver()
        workflow = create_workflow()
        workflow_with_memory = workflow.compile(checkpointer=memory)

        result = workflow_with_memory.invoke(initial_state, config={"thread_id": "campaign_001", "recursion_limit": 100})

        # 图像生成
        visual_prompt = result["artifacts"].get("visual", {}).get("image_prompt", "")
        if visual_prompt:
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
                download_image(image_url)
            except Exception as e:
                result["artifacts"]["visual"] = {
                    "image_prompt": visual_prompt,
                    "image_url": None,
                    "error": str(e)
                }

        analytics = CampaignAnalytics()
        analytics.track_iteration(result)
        report = analytics.generate_report()
        result["analytics_report"] = report

        result["artifacts"]["revision_count"] = result.get("revision_count", 0)
        generate_campaign_pdf(result, "final_campaign.pdf")

        return jsonify({
            "message": "Campaign generated successfully",
            "strategy": result['artifacts'].get("strategy"),
            "creative_concepts": result['artifacts'].get("creative_concepts"),
            "copy": result['artifacts'].get("copy"),
            "image_url": result['artifacts'].get("visual", {}).get("image_url"),
            "analytics_report": report
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# 启动服务
if __name__ == "__main__":
    app.run(debug=True)
