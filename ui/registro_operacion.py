# ui/registro_operacion.py

import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QComboBox, QFormLayout
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

# Rutas de los archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
OPERACIONES_FILE = os.path.join(DB_DIR, "registro_operaciones.json")
SESSION_FILE = os.path.join(DB_DIR, "session.json")
BALANCE_FILE = os.path.join(DB_DIR, "balance.json")


def cargar_sesion():
    """Carga la sesión actual desde el archivo JSON."""
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def cargar_balance():
    """Carga el balance actual desde el archivo JSON."""
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Crear archivo con valores por defecto si no existe
        balance_default = {
            "efectivo": 0.0,
            "dinero_cuenta": 0.0,
            "historial": []
        }
        with open(BALANCE_FILE, "w", encoding="utf-8") as file:
            json.dump(balance_default, file, indent=4)
        return balance_default


def actualizar_balance(tipo_operacion, cuenta, monto):
    """
    Actualiza el balance según la operación.
    
    Args:
        tipo_operacion: "ingreso" o "gasto"
        cuenta: "efectivo" o "dinero_cuenta"
        monto: float, cantidad a sumar o restar
    """
    balance = cargar_balance()
    
    # Asegurar que las claves existan
    if "efectivo" not in balance:
        balance["efectivo"] = 0.0
    if "dinero_cuenta" not in balance:
        balance["dinero_cuenta"] = 0.0
    if "historial" not in balance:
        balance["historial"] = []
    
    # Actualizar saldo según tipo de operación
    if tipo_operacion == "ingreso":
        balance[cuenta] += float(monto)
    elif tipo_operacion == "gasto":
        balance[cuenta] -= float(monto)
    
    # Guardar cambios
    try:
        with open(BALANCE_FILE, "w", encoding="utf-8") as file:
            json.dump(balance, file, indent=4)
    except Exception as e:
        print(f"Error al actualizar balance: {e}")


def guardar_operacion(data):
    """Guarda la operación en el archivo JSON."""
    if not os.path.exists(OPERACIONES_FILE):
        operaciones = []
    else:
        try:
            with open(OPERACIONES_FILE, "r", encoding="utf-8") as file:
                operaciones = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            operaciones = []

    operaciones.append(data)

    try:
        with open(OPERACIONES_FILE, "w", encoding="utf-8") as file:
            json.dump(operaciones, file, indent=4, ensure_ascii=False)
    except IOError:
        QMessageBox.critical(None, "Error", "No se pudo guardar la operación.")


class RegistrarOperacionDialog(QDialog):
    def __init__(self, tipo_operacion, parent=None):
        """
        Inicializa la ventana para registrar una operación.
        :param tipo_operacion: str, "gasto" o "ingreso".
        :param parent: QWidget, ventana principal.
        """
        super().__init__(parent)
        self.tipo_operacion = tipo_operacion
        self.setWindowTitle(f"Registrar {self.tipo_operacion.capitalize()}")
        self.setModal(True)
        self.cuenta = "efectivo"  # Valor por defecto
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(400, 300)  # Ajustado para acomodar el nuevo campo

        # Título
        titulo_label = QLabel(f"Registrar {self.tipo_operacion.capitalize()}")
        titulo_label.setFont(QFont("Arial", 16, QFont.Bold))
        titulo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo_label)

        # Cambiar color según el tipo de operación
        if self.tipo_operacion == "ingreso":
            titulo_label.setStyleSheet("background-color: #27ae60; color: white; padding: 5px; border-radius: 5px;")
        elif self.tipo_operacion == "gasto":
            titulo_label.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px; border-radius: 5px;")

        # Form layout para los campos
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Campo de cuenta (efectivo o dinero en cuenta)
        cuenta_label = QLabel("Cuenta:")
        cuenta_label.setFont(QFont("Arial", 12))
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.setFont(QFont("Arial", 12))
        self.cuenta_combo.addItem("Efectivo", "efectivo")
        self.cuenta_combo.addItem("Dinero en Cuenta", "dinero_cuenta")
        self.cuenta_combo.setCurrentIndex(0)
        self.cuenta_combo.currentIndexChanged.connect(self.on_cuenta_changed)
        form_layout.addRow(cuenta_label, self.cuenta_combo)

        # Input para la nota
        nota_label = QLabel("Nota:")
        nota_label.setFont(QFont("Arial", 12))
        self.nota_input = QLineEdit()
        self.nota_input.setFont(QFont("Arial", 12))
        self.nota_input.setPlaceholderText("Ingrese una nota")
        self.nota_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #2c3e50;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #e67e22;
            }
        """)
        form_layout.addRow(nota_label, self.nota_input)

        # Input para el monto
        monto_label = QLabel("Monto:")
        monto_label.setFont(QFont("Arial", 12))
        self.monto_input = QLineEdit()
        self.monto_input.setFont(QFont("Arial", 12))
        self.monto_input.setPlaceholderText("Ingrese el monto")
        self.monto_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #2c3e50;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #e67e22;
            }
        """)
        form_layout.addRow(monto_label, self.monto_input)

        layout.addLayout(form_layout)

        # Establecer el color del monto_input según el tipo de operación
        if self.tipo_operacion == "ingreso":
            self.monto_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #2c3e50;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #d4efdf; /* Verde claro */
                }
                QLineEdit:focus {
                    border: 2px solid #27ae60;
                }
            """)
        elif self.tipo_operacion == "gasto":
            self.monto_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #2c3e50;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #fadbd8; /* Rojo claro */
                }
                QLineEdit:focus {
                    border: 2px solid #e74c3c;
                }
            """)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()

        self.confirmar_button = QPushButton("Confirmar")
        self.confirmar_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.confirmar_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.confirmar_button.clicked.connect(self.aceptar)
        botones_layout.addWidget(self.confirmar_button)

        self.cancelar_button = QPushButton("Cancelar")
        self.cancelar_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.cancelar_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        self.cancelar_button.clicked.connect(self.reject)
        botones_layout.addWidget(self.cancelar_button)

        botones_layout.addStretch()
        layout.addLayout(botones_layout)

        # Lista de widgets para navegación con flechas
        self.focusable_widgets = [
            self.cuenta_combo,
            self.nota_input,
            self.monto_input,
            self.confirmar_button,
            self.cancelar_button
        ]

    def on_cuenta_changed(self, index):
        self.cuenta = self.cuenta_combo.itemData(index)

    def aceptar(self):
        """Valida y acepta los datos ingresados."""
        # Validar nota
        nota = self.nota_input.text().strip()
        if not nota:
            QMessageBox.warning(self, "Error", "La nota no puede estar vacía.")
            self.nota_input.setFocus()
            return

        # Validar monto
        monto_text = self.monto_input.text().strip()
        try:
            monto = float(monto_text)
            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Ingrese un monto válido:\n{e}")
            self.monto_input.setFocus()
            return

        # Asignar atributos para acceder desde fuera
        self.nota = nota
        self.monto = monto
        
        # Actualizar el balance
        actualizar_balance(self.tipo_operacion, self.cuenta, self.monto)
        
        self.accept()

    def get_operacion_data(self):
        """Devuelve los datos ingresados."""
        return {
            "tipo": self.tipo_operacion,
            "cuenta": self.cuenta,
            "monto": self.monto,
            "nota": self.nota
        }

    def keyPressEvent(self, event):
        """Maneja la navegación con las teclas Enter y flechas."""
        focus_order = self.focusable_widgets
        current_focus = self.focusWidget()

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            try:
                next_index = (focus_order.index(current_focus) + 1) % len(focus_order)
                next_widget = focus_order[next_index]
                next_widget.setFocus()
                event.accept()
            except ValueError:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Up:
            try:
                prev_index = (focus_order.index(current_focus) - 1) % len(focus_order)
                prev_widget = focus_order[prev_index]
                prev_widget.setFocus()
                event.accept()
            except ValueError:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Down:
            try:
                next_index = (focus_order.index(current_focus) + 1) % len(focus_order)
                next_widget = focus_order[next_index]
                next_widget.setFocus()
                event.accept()
            except ValueError:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)