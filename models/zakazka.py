class Zakazka:
    def __init__(
        self,
        poradove_cislo,
        datum_prijmu,
        objednavatel,
        adresa,
        druh_meradla,
        pocet_kusov,
        stav_pri_prevzati,
        cislo_objednavky=None,
        cislo_zakazky=None,
        poznamka=None
    ):
        self.poradove_cislo = poradove_cislo
        self.datum_prijmu = datum_prijmu
        self.objednavatel = objednavatel
        self.adresa = adresa
        self.druh_meradla = druh_meradla
        self.pocet_kusov = pocet_kusov
        self.stav_pri_prevzati = stav_pri_prevzati

        self.cislo_objednavky = cislo_objednavky
        self.cislo_zakazky = cislo_zakazky

        self.cislo_faktury = None
        self.cena_spolu = None
        self.certifikaty = None

        self.datum_prevzatia = None
        self.prevzal_meno = None

        self.poznamka = poznamka
        self.uzavreta = 0