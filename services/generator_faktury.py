from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


def generuj_fakturu(zakazka):
    os.makedirs("exports/faktury", exist_ok=True)

    filename = f"exports/faktury/faktura_{zakazka[0]}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)

    c.drawString(100, 800, "FAKTÚRA")
    c.drawString(100, 770, f"Objednávateľ: {zakazka[3]}")
    c.drawString(100, 750, f"Adresa: {zakazka[4]}")
    c.drawString(100, 730, f"Číslo zákazky: {zakazka[9]}")
    c.drawString(100, 710, f"Certifikáty: {zakazka[12]}")
    c.drawString(100, 690, f"Cena spolu: {zakazka[11]} €")

    c.save()

    print(f"Faktúra vytvorená: {filename}")