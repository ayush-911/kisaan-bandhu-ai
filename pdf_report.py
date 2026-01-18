from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def generate_pdf(report_data):
    """
    Generates a PDF report and returns filename
    """
    os.makedirs("reports", exist_ok=True)

    filename = f"reports/kisan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Kisan SuperAI - Crop Advisory Report")

    y -= 30
    c.setFont("Helvetica", 11)
    for line in report_data:
        if y < 80:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)
        c.drawString(50, y, line)
        y -= 18

    c.save()
    return filename
