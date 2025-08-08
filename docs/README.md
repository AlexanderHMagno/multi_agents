# 📚 Technical Documentation

## Architecture Overview

The Multi-Agent Marketing Campaign Generation System is built using a modular architecture with clear separation of concerns:

### Core Components

#### 1. Agent Layer (`src/agents/`)
- **Base Agent**: Foundation class with error handling and retry logic
- **Content Agents**: Strategy, Creative, Copy generation
- **Design Agents**: Visual assets and HTML validation
- **Analysis Agents**: Review, optimization, and persona analysis
- **Output Agents**: Website and PDF generation
- **Specialized Agents**: Social media and emotion personalization

#### 2. Workflow Engine (`src/workflows/`)
- **LangGraph Integration**: State-based workflow orchestration
- **Conditional Routing**: Smart decision-making for parallel execution
- **Quality Gates**: Automated quality assessment and revision control
- **Circuit Breaker**: Fault tolerance and graceful degradation

#### 3. Utilities (`src/utils/`)
- **State Management**: Centralized workflow state handling
- **Configuration**: Environment variable and API client management
- **Monitoring**: Performance tracking and analytics
- **File Handlers**: Output generation and file management

## Error Handling Strategy

### Circuit Breaker Pattern
```python
class WorkflowErrorTracker:
    def __init__(self, max_failures=5):
        self.failures = 0
        self.max_failures = max_failures
        self.circuit_open = False
```

### Retry Logic with Exponential Backoff
- **3 retry attempts** per API call
- **Exponential backoff**: 2s, 4s, 8s delays
- **Context-aware fallbacks**: Agent-specific placeholder content

### Fallback Response System
When APIs fail, agents generate contextual fallback responses to ensure workflow completion.

## Workflow Orchestration

### Sequential Processing
1. Project Management → Strategy → Audience Analysis
2. Creative Development → Copy Generation → CTA Optimization
3. Visual Design → Image Generation

### Parallel Processing
After image generation, three agents run in parallel:
- Social Media Campaign Development
- Emotion Personalization
- Media Planning

### Quality Control
- Automated review and feedback integration
- Revision management with configurable limits
- Quality scoring and threshold enforcement

## Agent Specializations

### Content Generation Agents
- **Strategy Team**: Market analysis and positioning
- **Creative Team**: Concept development and ideation
- **Copy Team**: Persuasive content creation

### Technical Agents
- **Web Developer**: Modern HTML/CSS/JS generation
- **HTML Validation**: Code quality and accessibility
- **PDF Generator**: Professional report creation

### Marketing Specialists
- **Social Media Campaign**: TikTok/Instagram strategies
- **Emotion Personalization**: 13 emotion-type targeting
- **Media Planner**: Multi-platform distribution

## Output Specifications

### Campaign Websites
- **Responsive Design**: Mobile-first CSS Grid/Flexbox
- **SEO Optimized**: Meta tags, semantic HTML, performance
- **Accessibility**: ARIA attributes, keyboard navigation
- **Modern UI**: Animations, gradients, interactive elements

### PDF Reports
- **Executive Summary**: Business impact and ROI analysis
- **Comprehensive Sections**: Strategy, audience, creative breakdown
- **Visual Integration**: Embedded images and charts
- **Professional Formatting**: Client-ready presentation

### Social Media Content
- **Platform-Specific**: TikTok vs Instagram optimization
- **Trending Elements**: Hashtags, keywords, formats
- **Engagement Strategy**: Community building and viral tactics

### Emotion-Based Personalization
Targeted messaging for 13 distinct emotional states:
- **Positive**: HAPPY, EXCITED, CONFIDENT, LOVED
- **Neutral**: CALM, CURIOUS, SURPRISED
- **Negative**: ANXIOUS, SAD, ANGRY, SCARED, DISGUSTED, JEALOUS

## Performance Monitoring

### Workflow Metrics
- **Execution Time**: Total and per-agent timing
- **Iteration Count**: Revision cycles and convergence
- **Quality Scores**: Automated assessment metrics
- **Error Rates**: API failures and recovery statistics

### Quality Assessment
```python
def assess_quality(state):
    quality_score = 0
    if artifacts.get("strategy"): quality_score += 20
    if artifacts.get("creative_concepts"): quality_score += 20
    if artifacts.get("copy"): quality_score += 20
    if artifacts.get("visual"): quality_score += 20
    # Additional quality checks...
    return quality_score
```

## API Integration

### OpenRouter LLM API
- **Model**: Configurable (default: google/gemini-2.5-flash-lite)
- **Error Handling**: JSONDecodeError recovery and fallbacks
- **Rate Limiting**: Built-in exponential backoff

### OpenAI DALL-E API
- **Image Generation**: High-quality marketing visuals
- **Prompt Optimization**: Automatic length and content adjustments
- **Fallback Handling**: Placeholder images when generation fails

## Security Considerations

### API Key Management
- **Environment Variables**: Secure storage in `.env`
- **Validation**: Startup checks for required keys
- **Rotation**: Easy key updates without code changes

### Input Sanitization
- **Campaign Brief Validation**: Type checking and format validation
- **Output Sanitization**: XSS prevention in generated HTML
- **Error Message Filtering**: Sensitive information protection

## Development Guidelines

### Code Organization
- **Modular Design**: Clear separation of concerns
- **Type Hints**: Full Python typing support
- **Documentation**: Comprehensive docstrings and comments

### Testing Strategy
- **Unit Tests**: Individual agent testing
- **Integration Tests**: Full workflow validation
- **Error Simulation**: Failure scenario testing

### Performance Optimization
- **Parallel Execution**: Concurrent agent processing where possible
- **Caching**: State persistence and artifact reuse
- **Resource Management**: Memory and connection pooling

## Extension Points

### Adding New Agents
1. Inherit from `BaseAgent`
2. Implement the `run()` method
3. Add to workflow graph
4. Update state artifacts

### Custom Output Formats
1. Create new output agent
2. Define artifact structure
3. Implement file generation logic
4. Add to workflow pipeline

### Integration Hooks
- **Webhook Support**: External system notifications
- **Database Integration**: Campaign storage and retrieval
- **Analytics Platforms**: Performance data export 