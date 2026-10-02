from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def build_pdf(title: str, lines: list[str]) -> bytes:
    out = BytesIO(); pdf = canvas.Canvas(out, pagesize=A4); width, height = A4
    pdf.setTitle(title); y = height - 48; pdf.setFont("Helvetica-Bold", 16); pdf.drawString(48, y, title); y -= 28
    pdf.setFont("Helvetica", 9)
    for line in lines:
        for chunk in [line[i:i+110] for i in range(0, len(line), 110)] or [""]:
            if y < 48: pdf.showPage(); pdf.setFont("Helvetica", 9); y = height - 48
            pdf.drawString(48, y, chunk); y -= 14
    pdf.save(); return out.getvalue()
