# 🎨 Agentic Ad Generation System

This project implements a sophisticated multi-agent system for generating advertising content with integrated image generation capabilities using LangChain and LangGraph.

## 🚀 Setup

1. Clone this repository
2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install python-dotenv langchain langgraph openai langchain_openai
```

4. Create a `.env` file in the root directory with the following content:
```
# OpenAI API Key for GPT-4 and general LLM usage
OPENAI_API_KEY=your_openai_api_key_here

# OpenAI API Key for DALL-E image generation
DALLE_API_KEY=your_dalle_api_key_here
```

Replace `your_openai_api_key_here` and `your_dalle_api_key_here` with your actual API keys.

## 📚 Project Structure

- `agentic_ad_generation.ipynb`: Main Jupyter notebook implementing the system
- `README.md`: This documentation file
- `.env`: Environment variables file (you need to create this)

## 🤖 Features

The system includes several specialized agent teams:

- **Project Manager**: Coordinates the overall workflow
- **Strategy Team**: Analyzes campaign requirements
- **Creative Team**: Generates innovative concepts
- **Copy Team**: Creates compelling ad copy
- **Visual Team**: Generates image prompts and visuals
- **Review Team**: Evaluates and provides feedback

## 🔄 Workflow

1. Input a campaign brief
2. Strategy team analyzes and provides recommendations
3. Creative team generates concepts
4. Copy team creates ad copy
5. Visual team generates matching imagery
6. Review team evaluates and provides feedback
7. Process iterates if revisions are needed

## 📊 Analytics

The system includes built-in analytics tracking:
- Number of iterations
- Team performance metrics
- Quality scores
- Timing information

## 🛠️ Usage

1. Open `agentic_ad_generation.ipynb` in Jupyter
2. Follow the notebook cells to:
   - Set up environment
   - Initialize agent teams
   - Create workflow
   - Run campaign generation
   - View analytics

## 🔐 Security Notes

- Never commit your `.env` file
- Keep your API keys secure
- Monitor API usage to control costs

## 📝 License

MIT License - feel free to use and modify for your needs.