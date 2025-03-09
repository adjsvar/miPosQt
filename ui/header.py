# ui/header.py
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QDateTime

class Header(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar el layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Margen interno
        self.setLayout(layout)

        # Estilo del Header
        self.setStyleSheet("""
            background-color: #2c3e50;
        """)

        # Etiqueta para mostrar el mensaje
        self.label = QLabel()
        self.label.setStyleSheet("color: white; font-weight: bold; padding: 15px;")
        self.label.setFont(QFont("Arial", 20))
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self.label)

        # Configurar el temporizador para actualizar la hora
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        """Actualiza el mensaje con la fecha y hora actual."""
        current_datetime = QDateTime.currentDateTime()
        formatted_date = current_datetime.toString("dddd, d MMMM yyyy")
        formatted_time = current_datetime.toString("hh:mm:ss AP")
        self.label.setText(f"Hola, hoy es {formatted_date} y son las {formatted_time}")
