import gradio as gr
import os
from dotenv import load_dotenv
from typing import Optional

from src.react_agent.ad_generation import (
    AdAgent, ToneStyle
)

load_dotenv()

ad_agent = AdAgent()

# Natural language input callback functions
def generate_from_raw(raw_text: str,
                      tone_style: Optional[str],
                      temperature: float,
                      max_length: int) -> str:
    try:
        tone_enum = ToneStyle(tone_style) if tone_style else None
        result = ad_agent.generate_ad_from_raw_text(
            raw_text, tone_enum, temperature=temperature, max_length=max_length
        )

        if "error" in result:
            return f"ERROR：{result['error']}"

        extracted = result["extracted_info"]

        output = f"## advertising copywriter\n\n"
        output += f"**{result['ad_text']}**\n\n"

        output += "## retrieve information\n"
        output += f"- **product name：** {extracted.get('product_name')}\n"
        output += f"- **product_description：** {extracted.get('product_description')}\n"
        output += f"- **emotion：** {extracted.get('emotion')}\n"
        output += f"- **interest：** {', '.join(extracted.get('interests', []))}\n"
        output += f"- **budget_conscious：** {'Yes' if extracted.get('budget_conscious') else 'No'}\n"
        output += f"- **age groups：** {extracted.get('age_group')}\n"
        output += f"- **selected_tone：** {result['selected_tone'].value}\n"
        output += f"- **temperature：** {temperature}\n"
        output += f"- **max_length：** {max_length}\n"
        return output
    except Exception as e:
        return f"ERROR：{str(e)}"

# 构建 Gradio 页面
with gr.Blocks(title="Intelligent Ad Generation System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Intelligent Ad Generation System")
    gr.Markdown("Enter a user comment or conversation and the system will automatically extract the information and generate ad copy.")

    with gr.Row():
        with gr.Column(scale=1):
            raw_input = gr.Textbox(
                label="user review / dialog",
                placeholder="For example, I recently bought a FitX smart bracelet that measures heart rate and synchronizes with WeChat alerts, and it would be nice if the price was a little cheaper.",
                lines=5
            )

            tone_style = gr.Dropdown(
                label="Advertising tone style (optional)",
                choices=[t.value for t in ToneStyle],
                value=None,
                allow_custom_value=True
            )

            temperature = gr.Slider(
                label="temperature", minimum=0.0, maximum=1.0, step=0.1, value=0.7
            )

            max_length = gr.Number(
                label="max tokens", value=1000, precision=0
            )

            generate_btn = gr.Button("Generate ad copy")

        with gr.Column(scale=1):
            output = gr.Markdown(label="Generate results")

    generate_btn.click(
        fn=generate_from_raw,
        inputs=[raw_input, tone_style, temperature, max_length],
        outputs=output
    )