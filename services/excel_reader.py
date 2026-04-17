import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FOLDER = os.path.join(BASE_DIR, "..", "data")


def najdi_data_podla_objednavky(cislo_objednavky):
    vysledky = []

    # normalize input
    cislo_objednavky = str(cislo_objednavky).strip()

    if not os.path.exists(EXCEL_FOLDER):
        print("❌ Neexistuje priečinok data:", EXCEL_FOLDER)
        return vysledky

    for subor in os.listdir(EXCEL_FOLDER):
        if subor.endswith(".xlsx"):
            cesta = os.path.join(EXCEL_FOLDER, subor)

            try:
                df = pd.read_excel(cesta)
            except Exception as e:
                print(f"❌ Chyba pri čítaní {subor}: {e}")
                continue

            for _, row in df.iterrows():
                excel_obj = str(row.get("cislo_objednavky")).strip()

                if excel_obj == cislo_objednavky:
                    vysledky.append({
                        "certifikat": row.get("certifikat"),
                        "cena": float(row.get("cena")) if row.get("cena") else 0
                    })

    print("🔍 Nájdené v Exceli:", vysledky)

    return vysledky