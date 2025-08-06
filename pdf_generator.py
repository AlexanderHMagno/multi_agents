from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_formatted_pdf(state, filename="formatted_campaign_report.pdf"):
    content = state.get("artifacts", {}).get("pdf_report", {}).get("formatted_content", "")

    if not content:
        print("❌ No formatted content found in state['artifacts']['pdf_report']")
        return

    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    x_margin = 40
    y = height - 50

    c.setFont("Helvetica", 12)
    for line in content.split("\n"):
        if not line.strip():
            y -= 10  # spacing for empty lines
            continue
        for chunk in [line[i:i+100] for i in range(0, len(line), 100)]:
            c.drawString(x_margin, y, chunk)
            y -= 14
            if y < 100:
                c.showPage()
                y = height - 50

    c.save()
    print(f"✅ Formatted PDF saved as {filename}")