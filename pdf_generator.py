from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from io import BytesIO
import requests

def generate_campaign_pdf(state, filename="campaign_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    x_margin = 40
    y = height - 50

    artifacts = state.get("artifacts", {})
    feedback = state.get("feedback", [])
    pdf_report = artifacts.get("pdf_report", {})
    formatted_content = pdf_report.get("formatted_content", "")

    def draw_text_block(title, text, size=12):
        nonlocal y
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_margin, y, title)
        y -= 18
        c.setFont("Helvetica", size)
        for line in text.split('\n'):
            for chunk in [line[i:i+100] for i in range(0, len(line), 100)]:
                c.drawString(x_margin, y, chunk)
                y -= 14
                if y < 100:
                    c.showPage()
                    y = height - 50

    # Draw header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(x_margin, height - 40, "Campaign Report")
    y = height - 80

    # Section 0: PDF Generator Team's Formatted Content
    if formatted_content:
        draw_text_block("📋 Executive Summary", formatted_content)
        c.showPage()
        y = height - 50

    # Section 1: Content blocks
    draw_text_block("📊 Campaign Strategy", artifacts.get("strategy", "N/A"))
    draw_text_block("👥 Audience Personas", artifacts.get("audience_personas", "N/A"))
    draw_text_block("🎨 Creative Concepts", artifacts.get("creative_concepts", "N/A"))
    draw_text_block("📝 Copy", artifacts.get("copy", "N/A"))
    draw_text_block("🎯 CTA Optimization", artifacts.get("cta_optimization", "N/A"))
    draw_text_block("📱 Media Plan", artifacts.get("media_plan", "N/A"))
    draw_text_block("💼 Client Summary", artifacts.get("client_summary", "N/A"))
    
    # Handle feedback properly - convert messages to strings
    feedback_text = ""
    if feedback:
        feedback_strings = []
        for fb in feedback:
            if hasattr(fb, 'content'):
                feedback_strings.append(fb.content)
            elif isinstance(fb, str):
                feedback_strings.append(fb)
            else:
                feedback_strings.append(str(fb))
        feedback_text = "\n".join(feedback_strings)
    else:
        feedback_text = "No feedback"
    
    draw_text_block("🧠 Review Feedback", feedback_text)

    # Section 2: Embed Image if available
    image_url = artifacts.get("visual", {}).get("image_url")
    image_prompt = artifacts.get("visual", {}).get("image_prompt", "")
    
    if image_url:
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                y -= 30
                c.setFont("Helvetica-Bold", 16)
                c.drawString(x_margin, y, "🎨 Visual Concepts & Creative Assets")
                y -= 20
                c.setFont("Helvetica", 12)
                c.drawString(x_margin, y, f"Image Description: {image_prompt}")
                y -= 310
                c.drawImage(img_data, x_margin, y, width=400, height=300, preserveAspectRatio=True)
                y -= 20
                c.drawString(x_margin, y, f"Image URL: {image_url}")
                print("✅ Visual concepts image embedded successfully in PDF")
            else:
                draw_text_block("⚠️ Failed to load image", f"HTTP {response.status_code}")
        except Exception as e:
            draw_text_block("⚠️ Failed to load image", str(e))
            # Still include the image description even if image fails to load
            if image_prompt:
                draw_text_block("📝 Visual Concept Description", image_prompt)
    else:
        # Include image description even if no URL
        if image_prompt:
            draw_text_block("📝 Visual Concept Description", image_prompt)

    # Section 3: Web Developer Output
    web_dev = artifacts.get("web_developer", {})
    if web_dev:
        c.showPage()
        y = height - 50
        draw_text_block("💻 Landing Page Code", web_dev.get("landing_page", "N/A"))

    # Section 4: Analytics
    c.showPage()
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, y, "📈 Analytics Report")
    y -= 30
    c.setFont("Helvetica", 12)

    def draw_kv(key, value):
        nonlocal y
        c.drawString(x_margin, y, f"{key}: {value}")
        y -= 18
        if y < 100:
            c.showPage()
            y = height - 50

    draw_kv("Number of Revisions", str(state.get("revision_count", "Unknown")))
    activated_teams = [k for k in artifacts if k in ["strategy", "creative_concepts", "copy", "visual", "web_developer", "pdf_report", "audience_personas", "cta_optimization", "media_plan", "client_summary"]]
    draw_kv("Activated Teams", ", ".join(activated_teams))

    draw_kv("Feedback Topics", "")
    # Handle feedback properly in analytics section
    if feedback:
        for fb in feedback:
            if hasattr(fb, 'content'):
                draw_kv("   •", fb.content)
            elif isinstance(fb, str):
                draw_kv("   •", fb)
            else:
                draw_kv("   •", str(fb))
    else:
        draw_kv("   •", "No feedback provided")

    # Campaign Summary
    if "campaign_summary" in artifacts:
        c.showPage()
        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x_margin, y, "📑 Campaign Summary")
        y -= 30
        draw_text_block("", artifacts["campaign_summary"])

    c.save()
    print(f"✅ PDF saved as {filename}")