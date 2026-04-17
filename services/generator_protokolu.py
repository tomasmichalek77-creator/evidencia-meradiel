from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


def generuj_protokol(zakazka):
    os.makedirs("exports/protokoly", exist_ok=True)

    filename = f"exports/protokoly/protokol_{zakazka[0]}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)

    c.drawString(100, 800, "PREBERACÍ PROTOKOL")

    c.drawString(100, 770, f"Objednávateľ: {zakazka[3]}")
    c.drawString(100, 750, f"Adresa: {zakazka[4]}")

    c.drawString(100, 720, f"Druh meradla: {zakazka[5]}")
    c.drawString(100, 700, f"Počet kusov: {zakazka[6]}")

    c.drawString(100, 670, f"Certifikáty: {zakazka[12]}")

    c.drawString(100, 630, "Dátum prevzatia: ____________________")
    c.drawString(100, 600, "Meno: ____________________")
    c.drawString(100, 570, "Podpis: ____________________")

    c.save()

    print(f"Protokol vytvorený: {filename}")