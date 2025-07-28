# Intelligent Ad Generation System

A personalized advertising copy generation system based on OpenRouter LLM, supporting multiple tone styles and user profile adaptation.

## Features

### Multiple Tone Styles
- **Professional** - Authoritative and reliable
- **Playful** - Light and humorous
- **Minimalist** - Concise and direct
- **Emotional** - Emotionally touching
- **Urgent** - Time-sensitive
- **Luxury** - High-end and prestigious

### User Profile Adaptation
- **Emotional States** - Happy, Excited, Calm, Anxious, Confident, Curious
- **Interest Tags** - Personalized interest matching
- **Budget Consciousness** - Value-oriented approach

### Agent-like Behavior
- Automatically select optimal tone based on user profile
- Dynamic parameter adjustment
- Intelligent prompt engineering

## Quick Start

### 1. Environment Setup

Ensure Python version is 3.11 or higher:
```bash
python --version
```

### 2. Install Dependencies

```bash
pip install -r requirement.txt
```

### 3. Configure API Keys

Copy the environment variables file and configure API keys:
```bash
cp .env_example .env
```

Edit the `.env` file and set the following variables:
```env
OPENROUTER_API_KEY="your-openrouter-api-key"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
```

### 4. Launch the System

```bash
python main.py
```

Then visit in your browser: `http://localhost:7860`

## Usage Guide

### Web Interface Usage

1. **Fill in Product Information**:
   - Product Name
   - Product Description
   - Target Audience

2. **Set User Profile**:
   - Select Emotional State
   - Choose Tone Style
   - Input Interest Tags
   - Set Budget Consciousness

3. **Adjust Generation Parameters**:
   - Temperature (Creativity)
   - Maximum Length

4. **Click Generate**: Get personalized ad copy

### Programming Interface Usage

```python
from src.react_agent.ad_generation import AdAgent

# Create ad agent
ad_agent = AdAgent()

# Define user input
user_input = {
    "product_name": "Smart Watch",
    "product_description": "Health monitoring, fitness tracking, smart notifications",
    "target_audience": "Young professionals",
    "emotion": "excited",
    "interests": ["technology", "fitness", "fashion"],
    "budget_conscious": False,
    "tone_style": "playful",
    "temperature": 0.7,
    "max_length": 100
}

The system defaults to using OpenRouter's Llama 3.1 8B model, which can be modified in the `AdGenerator` class:

```python
generator = AdGenerator(model_name="meta-llama/llama-3.1-8b-instruct")
```

### Generation Parameters

- **Temperature** (0.1-1.0) - Controls creativity
- **Max Length** - Maximum word count for ad copy

## Project Structure

```
├── src/
│   └── react_agent/
│       ├── ad_generation.py    # Core ad generation logic
│       ├── graph.py            # LangGraph workflow
│       ├── tools.py            # Tool functions
│       ├── utils.py            # Utility functions
│       └── configuration.py    # Configuration
├── webui.py                      # Gradio web interface
├── main.py                      # Launch script
├── requirements.txt            # Python dependencies
├── .env_example               # Environment variables template
└── README.md                  # This file
```

## Key Features

### Dynamic Prompt Generation
The system generates personalized prompts based on:
- User emotional state
- Selected tone style
- User interests
- Budget consciousness
- Product information

### Agent-like Behavior
- **Profile Analysis**: Analyzes user input to build user profile
- **Tone Selection**: Automatically selects optimal tone based on profile and product
- **Dynamic Adjustment**: Adjusts generation parameters based on context

**Enjoy creating personalized advertisements!** 