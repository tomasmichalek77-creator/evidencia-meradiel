from database.db import create_tables
from models.zakazka import Zakazka
from services.zakazka_service import (
    pridaj_zakazku,
    ziskaj_vsetky_zakazky,
    uzavri_zakazku
)
from services.generator_faktury import generuj_fakturu
from services.generator_protokolu import generuj_protokol


# vytvorenie DB
create_tables()

# vytvorenie zákazky
z = Zakazka(
    poradove_cislo=1,
    datum_prijmu="2026-01-12",
    objednavatel="LBK PERLIT, s.r.o.",
    adresa="966 01 Lehôtka pod Brehmi",
    druh_meradla="Skúšobné sitá",
    pocet_kusov=13,
    stav_pri_prevzati="bez závad",
    cislo_objednavky="4500358647-SKG",
    cislo_zakazky="ZK2026001",
    poznamka="Test zápis"
)

# uloženie
pridaj_zakazku(z)

# načítanie
zakazky = ziskaj_vsetky_zakazky()
posledna = zakazky[-1]
posledne_id = posledna[0]

# uzavretie
uzavri_zakazku(posledne_id, "4500358647-SKG")

# refresh
zakazky = ziskaj_vsetky_zakazky()
posledna = zakazky[-1]

# dokumenty
generuj_fakturu(posledna)
generuj_protokol(posledna)

# výpis
for zak in zakazky:
    print(zak)