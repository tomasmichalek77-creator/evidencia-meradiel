from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QDateEdit
)
from PySide6.QtCore import QDate

from models.zakazka import Zakazka
from services.zakazka_service import pridaj_zakazku


class FormPridaj(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pridať zákazku")
        self.setGeometry(200, 200, 350, 500)

        layout = QVBoxLayout()

        # 📦 MERADLÁ
        self.meradla = [
            ("101", "Skúšobné sitá"),
            ("101", "Skúšobné sitá harfové"),
            ("102", "Silomerný stroj"),
            ("103", "Napínacie zariadenie"),
            ("104", "Tvrdomer"),
            ("104", "Tvrdomer SilverSchmidt"),
            ("105", "Oceľové meračské pásmo"),
            ("106", "Posuvné meradlo"),
            ("107", "Číselníkový odchýlkomer"),
            ("108", "Elektrický snímač dĺžky"),
            ("108", "Extenzometer"),
            ("110", "Snímač sily"),
            ("111", "Prístroj na meranie obsahu vzduchu v betóne"),
            ("112", "Ručný laserový dĺžkomer"),
            ("113", "Ľahká dynamická doska"),
        ]

        # 📅 dátum
        self.datum = QDateEdit()
        self.datum.setCalendarPopup(True)
        self.datum.setDate(QDate.currentDate())
        self.datum.setDisplayFormat("dd.MM.yyyy")

        # 🧾 vstupy
        self.objednavatel = QLineEdit()
        self.objednavatel.setPlaceholderText("Objednávateľ")

        self.adresa = QLineEdit()
        self.adresa.setPlaceholderText("Adresa")

        # 📊 COMBOBOX
        self.druh = QComboBox()
        for kod, nazov in self.meradla:
            self.druh.addItem(f"{kod} - {nazov}", kod)

        self.pocet = QLineEdit()
        self.pocet.setPlaceholderText("Počet kusov")

        self.objednavka = QLineEdit()
        self.objednavka.setPlaceholderText("Číslo objednávky")

        # 🛠️ STAV (default "bez závad", ale editovateľné)
        self.stav = QLineEdit()
        self.stav.setText("bez závad")

        # 🔘 tlačidlo
        btn_save = QPushButton("Uložiť")
        btn_save.clicked.connect(self.uloz)

        # 📐 layout
        layout.addWidget(QLabel("Dátum prijatia"))
        layout.addWidget(self.datum)

        layout.addWidget(QLabel("Objednávateľ"))
        layout.addWidget(self.objednavatel)

        layout.addWidget(QLabel("Adresa"))
        layout.addWidget(self.adresa)

        layout.addWidget(QLabel("Druh meradla"))
        layout.addWidget(self.druh)

        layout.addWidget(QLabel("Počet"))
        layout.addWidget(self.pocet)

        layout.addWidget(QLabel("Stav pri prevzatí"))
        layout.addWidget(self.stav)

        layout.addWidget(QLabel("Číslo objednávky"))
        layout.addWidget(self.objednavka)

        layout.addWidget(btn_save)

        self.setLayout(layout)

    # 💾 ULOŽENIE
    def uloz(self):
        try:
            pocet = int(self.pocet.text())
        except ValueError:
            print("❌ Počet musí byť číslo")
            return

        kod = self.druh.currentData()

        z = Zakazka(
            poradove_cislo=1,
            datum_prijmu=self.datum.date().toString("yyyy-MM-dd"),
            objednavatel=self.objednavatel.text(),
            adresa=self.adresa.text(),
            druh_meradla=kod,
            pocet_kusov=pocet,
            stav_pri_prevzati=self.stav.text(),
            cislo_objednavky=self.objednavka.text(),
            cislo_zakazky="AUTO",
            poznamka=""
        )

        pridaj_zakazku(z)

        print("✅ Zákazka uložená")

        self.close()