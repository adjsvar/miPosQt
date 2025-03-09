# ui/footer.py
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class Footer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Agregar padding de 10px en todos los lados
        self.setLayout(layout)

        # Label dinámico para mostrar shortcuts
        self.label = QLabel("Atajos disponibles:")
        self.label.setStyleSheet("""
            color: white; 
            font-weight: bold; 
            background-color: #2c3e50; 
            padding: 5px;  /* Opcional: padding interno del label */
            border-radius: 5px;  /* Opcional: bordes redondeados */
        """)
        self.label.setFont(QFont("Arial", 14))  # Reducir tamaño de fuente si es necesario
        self.label.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(50)  # Ajustar la altura para acomodar el padding
        layout.addWidget(self.label)

    def update_shortcuts(self, shortcuts):
        """Actualiza el texto del footer con los atajos correspondientes."""
        if shortcuts:
            shortcuts_text = " | ".join(f"{key}: {desc}" for key, desc in shortcuts.items())
            self.label.setText(f"Atajos disponibles: {shortcuts_text}")
        else:
            self.label.setText("Atajos disponibles: Ninguno")
