from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class ToneStyle(Enum):
    PROFESSIONAL = "professional"
    PLAYFUL = "playful"
    MINIMALIST = "minimalist"
    EMOTIONAL = "emotional"
    URGENT = "urgent"
    LUXURY = "luxury"


class EmotionType(Enum):
    HAPPY = "happy"
    EXCITED = "excited"
    CALM = "calm"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    CURIOUS = "curious"


@dataclass
class UserProfile:
    emotion: EmotionType
    interests: List[str]
    budget_conscious: bool = False
    age_group: Optional[str] = None


@dataclass
class AdRequest:
    product_name: str
    product_description: str
    target_audience: str
    user_profile: UserProfile
    tone_style: ToneStyle
    max_length: int = 100
    temperature: float = 0.7


class AdPromptGenerator:

    @staticmethod
    def get_tone_prompt(tone: ToneStyle) -> str:
        tone_prompts = {
            ToneStyle.PROFESSIONAL: "Use a professional, authoritative tone to highlight the reliability and quality of the product.",
            ToneStyle.PLAYFUL: "Use a light, fun tone with elements of humor and creative expression.",
            ToneStyle.MINIMALIST: "Use concise, direct expressions, avoid redundant vocabulary, and highlight core selling points.",
            ToneStyle.EMOTIONAL: "Use emotional expressions that touch the emotional resonance of the user.",
            ToneStyle.URGENT: "Create a sense of urgency, emphasizing time-bound opportunities and the need for immediate action.",
            ToneStyle.LUXURY: "Use high-end, luxurious expressions to highlight the uniqueness and dignity of the product."
        }
        return tone_prompts.get(tone, tone_prompts[ToneStyle.PROFESSIONAL])

    @staticmethod
    def get_emotion_prompt(emotion: EmotionType) -> str:
        emotion_prompts = {
            EmotionType.HAPPY: "The target user is in a happy mood and uses positive expressions.",
            EmotionType.EXCITED: "The target users are expectant and use exciting expressions.",
            EmotionType.CALM: "The target user is calm and uses gentle, soothing expressions.",
            EmotionType.ANXIOUS: "The target user has anxiety and uses soothing, solution-oriented expressions.",
            EmotionType.CONFIDENT: "The target user is confident and uses affirming, motivating expressions.",
            EmotionType.CURIOUS: "The target user is curious and uses expressions of exploration and discovery."
        }
        return emotion_prompts.get(emotion, emotion_prompts[EmotionType.CALM])

    @staticmethod
    def generate_dynamic_prompt(request: AdRequest) -> str:
        tone_prompt = AdPromptGenerator.get_tone_prompt(request.tone_style)
        emotion_prompt = AdPromptGenerator.get_emotion_prompt(request.user_profile.emotion)

        budget_hint = "Users focus on value for money, emphasizing value over price." if request.user_profile.budget_conscious else ""
        interests_hint = f"User interest：{', '.join(request.user_profile.interests)}。" if request.user_profile.interests else ""

        return f"""You are a professional advertising copywriter.

{tone_prompt}
{emotion_prompt}
{budget_hint}
{interests_hint}

Product Information:
- Product Name：{request.product_name}
- Product Description：{request.product_description}
- Target Audience：{request.target_audience}

Create a short, engaging piece of advertising copy that is no longer than{request.max_length}word.
Copywriting should:
1. Highlight the core value of the product 
2. Meet the characteristics of the target audience
3. use a specified tone of voice
4. Contains a call to action (CTA)
5. be concise, powerful and easy to remember

Please output the ad copy directly without additional instructions."""


class AdGenerator:

    def __init__(self, model_name: str = "meta-llama/llama-3.1-8b-instruct"):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
            model_name=model_name,
            temperature=0.7,
            max_tokens=200,
        )

    def generate_ad(self, request: AdRequest) -> str:
        self.llm.temperature = request.temperature
        prompt = AdPromptGenerator.generate_dynamic_prompt(request)

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Please make a request for the product'{request.product_name}'Generate ad copy.")
        ]

        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Error when generating ads：{str(e)}"


class AdAgent:

    def __init__(self):
        self.generator = AdGenerator()

    def analyze_user_profile(self, user_input: Dict[str, Any]) -> UserProfile:
        emotion = EmotionType(user_input.get("emotion", "calm"))
        interests = user_input.get("interests", [])
        budget_conscious = user_input.get("budget_conscious", False)
        age_group = user_input.get("age_group")

        return UserProfile(
            emotion=emotion,
            interests=interests,
            budget_conscious=budget_conscious,
            age_group=age_group
        )

    def select_optimal_tone(self, user_profile: UserProfile, product_type: str) -> ToneStyle:
        if user_profile.budget_conscious:
            return ToneStyle.MINIMALIST
        elif user_profile.emotion in [EmotionType.EXCITED, EmotionType.HAPPY]:
            return ToneStyle.PLAYFUL
        elif "luxury" in product_type.lower() or "premium" in product_type.lower():
            return ToneStyle.LUXURY
        else:
            return ToneStyle.PROFESSIONAL

    def generate_personalized_ad(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        user_profile = self.analyze_user_profile(user_input)

        request = AdRequest(
            product_name=user_input["product_name"],
            product_description=user_input.get("product_description", ""),
            target_audience=user_input.get("target_audience", "一般用户"),
            user_profile=user_profile,
            tone_style=user_input.get("tone_style") or self.select_optimal_tone(user_profile, user_input["product_name"]),
            temperature=user_input.get("temperature", 0.7),
            max_length=user_input.get("max_length", 100)
        )

        ad_text = self.generator.generate_ad(request)

        return {
            "ad_text": ad_text,
            "user_profile": user_profile,
            "selected_tone": request.tone_style,
            "generation_params": {
                "temperature": request.temperature,
                "max_length": request.max_length
            }
        }
