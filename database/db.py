import sqlite3

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "..", "evidencia.db")


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS zakazky (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poradove_cislo INTEGER,
        datum_prijmu TEXT,

        objednavatel TEXT,
        adresa TEXT,

        druh_meradla TEXT,
        pocet_kusov INTEGER,
        stav_pri_prevzati TEXT,

        cislo_objednavky TEXT,
        cislo_zakazky TEXT,

        cislo_faktury TEXT,
        cena_spolu REAL,

        certifikaty TEXT,

        datum_prevzatia TEXT,
        prevzal_meno TEXT,

        poznamka TEXT,
        uzavreta INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()