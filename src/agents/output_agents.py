"""
Output Generation Agents

This module contains agents responsible for generating final campaign deliverables
including websites and PDF reports.
"""

from .base_agent import BaseAgent
from ..utils.state import State


class WebDeveloper(BaseAgent):
    """
    Web Developer Agent - Generates comprehensive campaign presentation websites.
    
    Responsibilities:
    - Modern, responsive HTML/CSS/JS generation
    - Campaign data integration and visualization
    - Interactive element creation
    - SEO and accessibility optimization
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are the web developer responsible for creating a comprehensive campaign presentation website.
            Your role is to create a professional, modern, and beautiful website that presents ALL campaign information
            in an engaging and visually appealing format suitable for client presentations and stakeholder reviews.
            
            Create a complete campaign presentation website with:
            - Modern, responsive design using CSS Grid/Flexbox
            - Professional styling with gradients, shadows, animations, and modern UI elements
            - Multiple sections showcasing different aspects of the campaign
            - Interactive elements, hover effects, and smooth transitions
            - Mobile-first responsive design
            - SEO-optimized structure
            - Professional typography and color schemes
            - Campaign data visualization and charts
            - Executive summary and key insights
            - Detailed breakdown of all campaign components
            - Contact information and call-to-action elements
            - Footer with company information
            
            Structure the website as a comprehensive campaign presentation with sections for:
            - Executive Summary
            - Campaign Strategy
            - Audience Analysis
            - Creative Concepts
            - Copy and Messaging
            - CTA Optimization
            - Media Planning
            - Business Impact
            - Visual Assets
            - Recommendations

            Use all the provided campaign data to create a comprehensive, professional campaign presentation website.""",
            llm=llm
        )
    
    def run(self, state: State) -> dict:
        # Extract all campaign artifacts
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        audience_personas = state['artifacts'].get('audience_personas', '')
        creative_concepts = state['artifacts'].get('creative_concepts', '')
        copy_content = state['artifacts'].get('copy', '')
        cta_optimization = state['artifacts'].get('cta_optimization', '')
        media_plan = state['artifacts'].get('media_plan', '')
        client_summary = state['artifacts'].get('client_summary', '')
        campaign_summary = state['artifacts'].get('campaign_summary', '')
        social_media_campaign = state['artifacts'].get('social_media_campaign', '')
        emotion_personalization = state['artifacts'].get('emotion_personalization', '')
        visual_data = state['artifacts'].get('visual', {})
        image_url = visual_data.get('image_url', '')
        image_prompt = visual_data.get('image_prompt', '')
        
        # Create comprehensive campaign presentation website prompt
        comprehensive_prompt = f"""
        Create a comprehensive, professional campaign presentation website using ALL the following campaign information:

        CAMPAIGN BRIEF:
        {campaign_brief}

        STRATEGY:
        {strategy}

        AUDIENCE PERSONAS:
        {audience_personas}

        CREATIVE CONCEPTS:
        {creative_concepts}

        COPY CONTENT:
        {copy_content}

        CTA OPTIMIZATION:
        {cta_optimization}

        MEDIA PLAN:
        {media_plan}

        CLIENT SUMMARY:
        {client_summary}

        CAMPAIGN SUMMARY:
        {campaign_summary}

        SOCIAL MEDIA CAMPAIGN:
        {social_media_campaign}

        EMOTION PERSONALIZATION:
        {emotion_personalization}

        VISUAL ASSETS:
        Image URL: {image_url}
        Image Description: {image_prompt}
        IMPORTANT: For all images, use https://placehold.co/600x400?text= as placeholder images, where text= is the image description and 600x400 is the size (can be any size as widthxheight)

        WEBSITE REQUIREMENTS:
        1. Create a complete HTML page with embedded CSS and JavaScript
        2. Design as a professional campaign presentation website, not a landing page
        3. Use modern CSS with gradients, shadows, animations, and professional styling
        4. Include all campaign sections: Executive Summary, Strategy, Audience, Creative, Copy, CTA, Media, Social Media, Emotion Personalization, Impact
        5. PROMINENTLY DISPLAY THE GENERATED IMAGE in multiple ways:
           - Hero section with the image as background or featured element
           - Visual concepts section showcasing the image with description
           - Creative assets section highlighting the image
           - Add visual storytelling around the image
           - Create interactive image galleries or carousels
           - Include image analysis and creative insights
        6. Make it mobile-responsive with CSS Grid/Flexbox
        7. Include interactive elements, hover effects, and smooth transitions
        8. Add proper meta tags for SEO
        9. Use professional color schemes and modern typography
        10. Include data visualization elements and progress indicators
        11. Add navigation menu and smooth scrolling
        12. Create a comprehensive footer with contact information
        13. Include campaign metrics and performance indicators
        14. Add professional presentation elements like slides and sections
        15. Use modern UI components like cards, modals, and tooltips
        16. Create a dedicated "Visual Concepts" or "Creative Assets" section
        17. Include image analysis and creative direction insights
        18. Add visual storytelling elements around the campaign image
        19. Create a dedicated "Social Media Campaign" section showcasing TikTok and Instagram strategies
        20. Include a "Hyperpersonalization" section with emotion-based messaging for all emotion types:
            (HAPPY, EXCITED, CALM, ANXIOUS, CONFIDENT, CURIOUS, SAD, ANGRY, SCARED, DISGUSTED, SURPRISED, LOVED, JEALOUS)
        21. Add interactive elements for emotion selection and personalized content display
        22. Include social media previews and platform-specific content examples
        23. Add emotion-based content variations and personalization tools
        24. Include hashtag strategies and trending keywords for social media
        25. Add influencer collaboration opportunities and user-generated content strategies
        26. IMPORTANT: Create a dropdown navigation menu for all sections do not add a menu bar at the top of the page
        27. Include tabs for different emotion message variations

        IMPORTANT: The generated image should be a central visual element throughout the website, not just a small thumbnail. 
        Use it prominently in the hero section, creative concepts section, and as a key visual asset in the presentation.
        Include the image description and creative insights as part of the visual storytelling.
        
        Generate a complete, professional campaign presentation website that showcases the entire campaign comprehensively.
        The website should look like a modern, beautiful presentation suitable for client meetings and stakeholder reviews.
        """
        
        messages = self.get_messages(comprehensive_prompt)
        response = self.invoke_llm_with_retry(messages, "Campaign Website Generation")
        print(f"Comprehensive campaign presentation website generated with all campaign data")
        return self.return_state(state, response, {"web_developer": {"campaign_website": response.content}})


class PDFGeneratorTeam(BaseAgent):
    """
    PDF Generator Team Agent - Creates comprehensive PDF campaign reports.
    
    Responsibilities:
    - Professional PDF report generation
    - Campaign data compilation and formatting
    - Executive summary creation
    - Visual asset integration
    - Business impact analysis
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are a PDF generation specialist responsible for creating comprehensive campaign reports.
            Your role is to create a professional, well-structured PDF report that incorporates ALL campaign information
            including strategy, audience personas, creative concepts, copy, CTAs, media plan, client summary, and analytics.
            
            Create a comprehensive PDF report with:
            - Executive summary and campaign overview
            - Detailed strategy analysis and recommendations
            - Audience personas and targeting insights
            - Creative concepts and visual direction
            - Copy content and messaging strategy
            - CTA optimization and conversion elements
            - Media plan and distribution strategy
            - Client summary and business impact
            - Analytics and performance metrics
            - Visual assets and design elements
            - Recommendations and next steps
            
            Structure the report professionally with proper sections, headers, and formatting.
            Include all campaign data in an organized, easy-to-read format suitable for stakeholders.""",
            llm=llm
        )

    def run(self, state: State) -> dict:
        # Extract all campaign artifacts
        campaign_brief = state['campaign_brief']
        strategy = state['artifacts'].get('strategy', '')
        audience_personas = state['artifacts'].get('audience_personas', '')
        creative_concepts = state['artifacts'].get('creative_concepts', '')
        copy_content = state['artifacts'].get('copy', '')
        cta_optimization = state['artifacts'].get('cta_optimization', '')
        media_plan = state['artifacts'].get('media_plan', '')
        client_summary = state['artifacts'].get('client_summary', '')
        campaign_summary = state['artifacts'].get('campaign_summary', '')
        social_media_campaign = state['artifacts'].get('social_media_campaign', '')
        emotion_personalization = state['artifacts'].get('emotion_personalization', '')
        visual_data = state['artifacts'].get('visual', {})
        image_url = visual_data.get('image_url', '')
        image_prompt = visual_data.get('image_prompt', '')
        revision_count = state.get('revision_count', 0)
        
        # Create comprehensive PDF report prompt
        comprehensive_prompt = f"""
        Create a comprehensive, professional PDF report using ALL the following campaign information:

        CAMPAIGN BRIEF:
        {campaign_brief}

        STRATEGY:
        {strategy}

        AUDIENCE PERSONAS:
        {audience_personas}

        CREATIVE CONCEPTS:
        {creative_concepts}

        COPY CONTENT:
        {copy_content}

        CTA OPTIMIZATION:
        {cta_optimization}

        MEDIA PLAN:
        {media_plan}

        CLIENT SUMMARY:
        {client_summary}

        CAMPAIGN SUMMARY:
        {campaign_summary}

        SOCIAL MEDIA CAMPAIGN:
        {social_media_campaign}

        EMOTION PERSONALIZATION:
        {emotion_personalization}

        VISUAL ASSETS:
        Image URL: {image_url}
        Image Description: {image_prompt}

        WORKFLOW METRICS:
        Revision Count: {revision_count}

        PDF REPORT REQUIREMENTS:
        1. Create a comprehensive report structure with proper sections
        2. Include executive summary at the beginning
        3. Organize content logically: Strategy → Audience → Creative → Copy → Media → Results
        4. Include all campaign data in well-formatted sections
        5. Add visual descriptions and image information
        6. Include workflow metrics and revision history
        7. Provide clear recommendations and next steps
        8. Use professional formatting with headers, subheaders, and bullet points
        9. Include business impact and ROI projections
        10. Add contact information and follow-up actions
        11. Include appendices with detailed data if needed
        12. Create a table of contents structure
        13. Include social media campaign strategies and emotion personalization insights
        14. Add comprehensive visual asset documentation

        Generate a complete, professional PDF report that showcases the entire campaign comprehensively.
        """
        
        messages = self.get_messages(comprehensive_prompt)
        response = self.invoke_llm_with_retry(messages, "PDF Report Generation")
        print(f"Comprehensive PDF report generated with all campaign data")
        return self.return_state(state, response, {
            "pdf_report": {
                "formatted_content": response.content,
                "campaign_data_used": len(state.get('artifacts', {})),
                "revision_count": revision_count
            }
        }) 