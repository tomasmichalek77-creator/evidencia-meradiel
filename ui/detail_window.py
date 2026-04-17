from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel


class DetailWindow(QDialog):
    def __init__(self, data):
        super().__init__()

        self.setWindowTitle("Detail zákazky")

        layout = QVBoxLayout()

        for name, value in data:
            label = QLabel(f"{name}: {value}")
            layout.addWidget(label)

        self.setLayout(layout)