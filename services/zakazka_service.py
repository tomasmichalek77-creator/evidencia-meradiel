from database.db import get_connection


def pridaj_zakazku(zakazka):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO zakazky (
        poradove_cislo,
        datum_prijmu,
        objednavatel,
        adresa,
        druh_meradla,
        pocet_kusov,
        stav_pri_prevzati,
        cislo_objednavky,
        cislo_zakazky,
        poznamka
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        zakazka.poradove_cislo,
        zakazka.datum_prijmu,
        zakazka.objednavatel,
        zakazka.adresa,
        zakazka.druh_meradla,
        zakazka.pocet_kusov,
        zakazka.stav_pri_prevzati,
        zakazka.cislo_objednavky,
        zakazka.cislo_zakazky,
        zakazka.poznamka
    ))

    conn.commit()
    conn.close()


def ziskaj_vsetky_zakazky():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM zakazky")
    rows = cursor.fetchall()

    conn.close()
    return rows

from services.excel_reader import najdi_data_podla_objednavky


def uzavri_zakazku(zakazka_id, cislo_objednavky):
    data = najdi_data_podla_objednavky(cislo_objednavky)

    if not data:
        print("Nič sa nenašlo v Exceli")
        return

    certifikaty = []
    cena_spolu = 0

    for item in data:
        if item["certifikat"]:
            certifikaty.append(str(item["certifikat"]))

        if item["cena"]:
            cena_spolu += float(item["cena"])

    certifikaty_text = ", ".join(certifikaty)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE zakazky
    SET certifikaty = ?, cena_spolu = ?, uzavreta = 1
    WHERE id = ?
    """, (certifikaty_text, cena_spolu, zakazka_id))

    conn.commit()
    conn.close()

    print("Zákazka uzavretá ✅")