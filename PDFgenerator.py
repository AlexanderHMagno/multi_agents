from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import requests

def generate_campaign_pdf(state, filename="campaign_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    x_margin = 40
    y = height - 50

    artifacts = state.get("artifacts", {})
    feedback = state.get("feedback", [])

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

    # Section 1: Content blocks
    draw_text_block("📊 Campaign Strategy", artifacts.get("strategy", "N/A"))
    draw_text_block("🎨 Creative Concepts", artifacts.get("creative_concepts", "N/A"))
    draw_text_block("📝 Copy", artifacts.get("copy", "N/A"))
    draw_text_block("🧠 Review Feedback", "\n".join(feedback) if feedback else "No feedback")

    # Section 2: Embed Image if available
    image_url = artifacts.get("visual", {}).get("image_url")
    if image_url:
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                y -= 30
                c.setFont("Helvetica-Bold", 14)
                c.drawString(x_margin, y, "🖼️ Generated Visual")
                y -= 310
                c.drawImage(img_data, x_margin, y, width=400, height=300, preserveAspectRatio=True)
        except Exception as e:
            draw_text_block("⚠️ Failed to load image", str(e))

    # Section 3: Analytics
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
    activated_teams = [k for k in artifacts if k in ["strategy", "creative_concepts", "copy", "visual"]]
    draw_kv("Activated Teams", ", ".join(activated_teams))

    draw_kv("Feedback Topics", "")
    for fb in feedback:
        draw_kv("   •", fb)

    draw_kv("Summary", "Campaign was generated using a multi-agent workflow. Each team contributed to a specific component, and the system handled iteration with feedback control.")

    c.save()
    print(f"✅ PDF saved as {filename}")
