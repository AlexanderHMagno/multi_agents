import gradio as gr
import os
from typing import Dict, Any
from src.react_agent.ad_generation import (
    AdAgent, ToneStyle, EmotionType
)
from dotenv import load_dotenv

load_dotenv()

# Initialization of the advertising agency
ad_agent = AdAgent()


def generate_ad(
        product_name: str,
        product_description: str,
        target_audience: str,
        emotion: str,
        tone_style: str,
        interests: str,
        budget_conscious: bool,
        temperature: float,
        max_length: int
) -> str:
    """Generate ad copy"""

    from src.react_agent.ad_generation import ToneStyle, EmotionType

    # String → Enum Mapping
    if isinstance(emotion, str):
        emotion = EmotionType(emotion)

    if isinstance(tone_style, str):
        tone_style = ToneStyle(tone_style)

    interest_list = [interest.strip() for interest in interests.split(',') if interest.strip()]

    user_input = {
        "product_name": product_name,
        "product_description": product_description,
        "target_audience": target_audience,
        "emotion": emotion,
        "interests": interest_list,
        "budget_conscious": budget_conscious,
        "tone_style": tone_style,
        "temperature": temperature,
        "max_length": max_length
    }

    try:
        result = ad_agent.generate_personalized_ad(user_input)

        output = f"## Generated ad copy\n\n"
        output += f"**{result['ad_text']}**\n\n"

        output += "## Generating Information\n\n"
        output += f"- **Intonation style：** {result['selected_tone'].value}\n"
        output += f"- **Emotional state：** {result['user_profile'].emotion.value}\n"
        output += f"- **Interest Tags：** {', '.join(result['user_profile'].interests) if result['user_profile'].interests else 'Not'}\n"
        output += f"- **Budget awareness：** {'Yes' if result['user_profile'].budget_conscious else 'No'}\n"
        output += f"- **Temperature：** {result['generation_params']['temperature']}\n"
        output += f"- ** Maximum length：** {result['generation_params']['max_length']} Word\n"

        return output

    except Exception as e:
        return f"Error when generating ads：{str(e)}"


# Creating the Gradio Interface
with gr.Blocks(title="Intelligent Ad Generation System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Intelligent Ad Generation System")
    gr.Markdown("Personalized ad copy generation based on user profiles and product information")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("Input parameter")

            product_name = gr.Textbox(
                label="Product Name",
                placeholder="Examples: include smartwatches, coffee makers, skincare...",
                value=""
            )

            product_description = gr.Textbox(
                label="Product Description",
                placeholder="Describe in detail the features and benefits of the product...",
                value="",
                lines=3
            )

            target_audience = gr.Textbox(
                label="target audience",
                placeholder="Example: young white-collar workers, fitness enthusiasts, business people...",
                value=""
            )

            # user profile
            emotion = gr.Dropdown(
                label="user sentiment",
                choices=[e.value for e in EmotionType],
                value="calm"
            )

            tone_style = gr.Dropdown(
                label="Intonation style",
                choices=[t.value for t in ToneStyle],
                value="professional"
            )

            interests = gr.Textbox(
                label="User interests (separated by commas)",
                placeholder="Examples: technology, fitness, travel, food...",
                value=""
            )

            budget_conscious = gr.Checkbox(
                label="Focus on value for money",
                value=False
            )

            # 生成参数
            temperature = gr.Slider(
                label="Temperature（inventive step）",
                minimum=0.1,
                maximum=1.0,
                value=0.7,
                step=0.1
            )

            max_length = gr.Slider(
                label="Maximum length (words)",
                minimum=50,
                maximum=1000,
                value=100,
                step=10
            )

            generate_btn = gr.Button("Generate ads", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("## Generate Results")

            output_text = gr.Markdown(
                label="Generated ad copy",
                value="Click the Generate button to start creating ad copy..."
            )

    gr.Markdown("## Quick Example")

    with gr.Row():
        example1 = gr.Button("Example 1: High-end watches")
        example2 = gr.Button("Example 2: Coffee machine")
        example3 = gr.Button("Example 3: Skin care products")


    # event processing
    def example1_fn():
        return {
            product_name: "Luxury Smartwatch",
            product_description: "Swiss movement, sapphire crystal, 24K gold case, for successful people",
            target_audience: "Successful Businessman",
            emotion: "confident",
            tone_style: "luxury",
            interests: "Luxury, Business, Golf",
            budget_conscious: False,
            temperature: 0.8,
            max_length: 120
        }


    def example2_fn():
        return {
            product_name: "Smart Coffee Maker",
            product_description: "One click to make professional grade coffee, supports a variety of coffee beans, intelligent temperature control system",
            target_audience: "coffee lover",
            emotion: "excited",
            tone_style: "playful",
            interests: "Coffee, Gourmet, Quality of Life",
            budget_conscious: True,
            temperature: 0.7,
            max_length: 100
        }


    def example3_fn():
        return {
            product_name: "Natural Skin Care Set",
            product_description: "Organic plant extracts, no added preservatives, suitable for sensitive skin",
            target_audience: "Skin-conscious women",
            emotion: "calm",
            tone_style: "emotional",
            interests: "Skin Care,Health,Natural",
            budget_conscious: False,
            temperature: 0.6,
            max_length: 90
        }


    # bind an event
    generate_btn.click(
        fn=generate_ad,
        inputs=[
            product_name, product_description, target_audience,
            emotion, tone_style, interests, budget_conscious,
            temperature, max_length
        ],
        outputs=output_text
    )

    example1.click(fn=example1_fn, outputs=[
        product_name, product_description, target_audience,
        emotion, tone_style, interests, budget_conscious,
        temperature, max_length
    ])

    example2.click(fn=example2_fn, outputs=[
        product_name, product_description, target_audience,
        emotion, tone_style, interests, budget_conscious,
        temperature, max_length
    ])

    example3.click(fn=example3_fn, outputs=[
        product_name, product_description, target_audience,
        emotion, tone_style, interests, budget_conscious,
        temperature, max_length
    ])

if __name__ == "__main__":
    # Checking environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Please set your OpenRouter API key in the .env file")

    if not os.getenv("OPENROUTER_BASE_URL"):
        print("Please set the OpenRouter API base URL in the .env file")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )