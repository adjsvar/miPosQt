# ui/notas.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class NotasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notas de Cierre de Caja")
        self.setModal(True)
        self.setFixedSize(500, 450)  # Tamaño ajustado
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)  # Quitar botón cerrar y ayuda
        self.init_ui()
        self.notas = {}

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Instrucciones
        instrucciones = QLabel("Ingrese las notas correspondientes:")
        instrucciones.setFont(QFont("Arial", 16, QFont.Bold))
        instrucciones.setAlignment(Qt.AlignCenter)
        instrucciones.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(instrucciones)

        # Campos de entrada en un FormLayout
        form_layout = QFormLayout()
        self.inputs = {}
        campos = ["SALDO SUBE", "SALDO LG", "BBVA", "MERCADOPAGO", "EFECTIVO"]

        for campo in campos:
            label = QLabel(f"{campo}:")
            label.setFont(QFont("Arial", 14))
            input_field = QLineEdit()
            input_field.setFont(QFont("Arial", 14))
            input_field.setPlaceholderText(f"Ingrese el monto para {campo}")
            input_field.setFixedHeight(35)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #f8f9fa;
                    color: #2c3e50;
                }
                QLineEdit:focus {
                    border: 1px solid #2980b9;
                    background-color: #ffffff;
                }
            """)
            form_layout.addRow(label, input_field)
            self.inputs[campo] = input_field

        layout.addLayout(form_layout)

        # Botones en un solo layout horizontal
        botones_layout = QHBoxLayout()
        botones_layout.setContentsMargins(0, 20, 0, 0)
        botones_layout.addStretch()

        self.aceptar_button = QPushButton("Aceptar")
        self.aceptar_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.aceptar_button.clicked.connect(self.aceptar)
        self.aceptar_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:focus {
                background-color: #1e8449;
            }
        """)
        botones_layout.addWidget(self.aceptar_button)

        self.cancelar_button = QPushButton("Cancelar")
        self.cancelar_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.cancelar_button.clicked.connect(self.reject)
        self.cancelar_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:focus {
                background-color: #922b21;
            }
        """)
        botones_layout.addWidget(self.cancelar_button)
        botones_layout.addStretch()

        layout.addLayout(botones_layout)

    def navegar(self, campo_actual, direccion):
        """Navega al siguiente o anterior campo o al botón Aceptar."""
        campos = list(self.inputs.keys())
        index = campos.index(campo_actual)

        if direccion == "abajo":
            if index < len(campos) - 1:
                siguiente_campo = campos[index + 1]
                self.inputs[siguiente_campo].setFocus()
            else:
                self.aceptar_button.setFocus()
        elif direccion == "arriba":
            if index > 0:
                anterior_campo = campos[index - 1]
                self.inputs[anterior_campo].setFocus()
            else:
                self.cancelar_button.setFocus()

    def aceptar(self):
        """Recopila las notas ingresadas y las valida."""
        for campo, input_field in self.inputs.items():
            texto = input_field.text().strip()
            if texto:
                try:
                    monto = float(texto)
                    if monto < 0:
                        raise ValueError
                    self.notas[campo] = monto
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"El monto para {campo} es inválido. Por favor, ingrese un número positivo."
                    )
                    input_field.setFocus()
                    return
            else:
                self.notas[campo] = "-no informado-"

        self.accept()

    def keyPressEvent(self, event):
        """Maneja la navegación con teclas Enter y flechas, y el cierre con Esc."""
        if event.key() == Qt.Key_Escape:
            self.reject()
            return

        focus_widget = self.focusWidget()
        if isinstance(focus_widget, QLineEdit):
            for campo, input_field in self.inputs.items():
                if focus_widget == input_field:
                    if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                        self.navegar(campo, "abajo")
                        return
                    elif event.key() == Qt.Key_Up:
                        self.navegar(campo, "arriba")
                        return
                    elif event.key() == Qt.Key_Down:
                        self.navegar(campo, "abajo")
                        return
        elif focus_widget == self.aceptar_button:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.aceptar()
                return
        elif focus_widget == self.cancelar_button:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.reject()
                return
            elif event.key() == Qt.Key_Up:
                last_field = list(self.inputs.keys())[-1]
                self.inputs[last_field].setFocus()
                return

        super().keyPressEvent(event)

    def get_notas(self):
        """Devuelve las notas ingresadas."""
        return self.notas
