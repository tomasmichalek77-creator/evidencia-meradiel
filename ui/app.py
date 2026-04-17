from ui.detail_window import DetailWindow
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem
)
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtGui import QColor
import sys

from services.zakazka_service import (
    ziskaj_vsetky_zakazky,
    uzavri_zakazku as uzavri_zakazka_service
)
from services.generator_faktury import generuj_fakturu
from services.generator_protokolu import generuj_protokol

from database.db import create_tables
from ui.form_pridaj import FormPridaj


class App(QWidget):
    def __init__(self):
        super().__init__()

        create_tables()

        self.setWindowTitle("Evidencia meradiel")
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()

        # 📊 TABUĽKA
        self.table = QTableWidget()
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        self.table.cellDoubleClicked.connect(self.open_detail)

        # 🔘 TLAČIDLÁ
        btn_refresh = QPushButton("Načítať zákazky")
        btn_refresh.clicked.connect(self.nacitaj_data)
        layout.addWidget(btn_refresh)

        btn_add = QPushButton("Pridať zákazku")
        btn_add.clicked.connect(self.otvor_form)
        layout.addWidget(btn_add)

        btn_close = QPushButton("Uzavrieť zákazku")
        btn_close.clicked.connect(self.uzavri_zakazku)
        layout.addWidget(btn_close)

        self.setLayout(layout)

        # nastavenia tabuľky
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)

        # hlavičky (uložíme si ich aj do self)
        self.headers = [
            "ID", "Por. číslo", "Dátum", "Objednávateľ", "Adresa",
            "Druh", "Počet", "Stav",
            "Objednávka", "Zákazka",
            "Faktúra", "Cena", "Certifikáty",
            "Dátum prevzatia", "Prevzal",
            "Poznámka", "Uzavretá"
        ]

        # načítanie dát
        self.nacitaj_data()

    # 🪟 DETAIL OKNO
    def show_detail_window(self, data):
        self.detail_window = DetailWindow(data)
        self.detail_window.exec()

    # 🖱️ DVOJKLIK
    def open_detail(self, row, column):
        self.table.selectRow(row)

        data = []

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            data.append(item.text() if item else "")

        # spojenie názov + hodnota
        detail_data = list(zip(self.headers, data))

        print("Kliknutý riadok:", detail_data)

        self.show_detail_window(detail_data)

    # ➕ FORM
    def otvor_form(self):
        dialog = FormPridaj()
        dialog.exec()
        self.nacitaj_data()

    # 🔒 UZAVRETIE
    def uzavri_zakazku(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:
            print("❌ Nevybral si riadok")
            return

        item_id = self.table.item(selected_row, 0)
        if not item_id:
            return

        zakazka_id = int(item_id.text())
        cislo_obj = self.table.item(selected_row, 8).text()
        uzavreta = self.table.item(selected_row, 16).text()

        if uzavreta == "1":
            print("⚠️ Zákazka je už uzavretá")
            return

        print(f"Uzavieram ID {zakazka_id}")

        uzavri_zakazka_service(zakazka_id, cislo_obj)

        data = ziskaj_vsetky_zakazky()
        aktualna = [z for z in data if z[0] == zakazka_id][0]

        generuj_fakturu(aktualna)
        generuj_protokol(aktualna)

        self.nacitaj_data()

    # 📊 TABUĽKA
    def nacitaj_data(self):
        data = ziskaj_vsetky_zakazky()

        if not data:
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))
        self.table.setHorizontalHeaderLabels(self.headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                text = "" if value is None else str(value)
                item = QTableWidgetItem(text)
                self.table.setItem(row_idx, col_idx, item)

            # 🎨 FARBY
            uzavreta = row_data[16]

            if uzavreta == 1:
                color = QColor(220, 255, 220)
            else:
                color = QColor(255, 220, 220)

            for col_idx in range(len(row_data)):
                self.table.item(row_idx, col_idx).setBackground(color)

        self.table.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())