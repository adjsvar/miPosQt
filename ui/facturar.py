# ui/facturar.py

import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QWidget, QButtonGroup, QInputDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

CLIENTES_FILE = "./db/clientes.json"


def cargar_clientes():
    """Carga los clientes desde el archivo JSON."""
    if not os.path.exists(CLIENTES_FILE):
        return []
    try:
        with open(CLIENTES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def guardar_clientes(clientes):
    """Guarda los clientes en el archivo JSON."""
    try:
        with open(CLIENTES_FILE, "w", encoding="utf-8") as file:
            json.dump(clientes, file, indent=4, ensure_ascii=False)
    except IOError:
        QMessageBox.critical(None, "Error", "No se pudo guardar el archivo de clientes.")


class FacturarDialog(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Facturación")
        self.setModal(True)
        self.total = total
        self.pagado = 0
        self.pagos = []  # Lista de dicts: {"metodo": "Efectivo", "monto": 1000}
        self.cambio = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setMinimumSize(800, 500)

        # Mostrar el total
        total_layout = QHBoxLayout()
        total_label = QLabel("Total a Pagar:")
        total_label.setFont(QFont("Arial", 20, QFont.Bold))  # Letra más grande
        self.total_display = QLabel(f"${self.total:.2f}")
        self.total_display.setFont(QFont("Arial", 26, QFont.Bold))  # Letra más grande
        self.total_display.setStyleSheet("""
            QLabel {
                background-color: orange; 
                color: white; 
                padding: 15px; 
                border-radius: 5px;
                font-size: 28px;
            }
        """)
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_display)
        layout.addLayout(total_layout)

        # Input para monto de pago
        pago_layout = QHBoxLayout()
        pago_label = QLabel("Monto de Pago:")
        pago_label.setFont(QFont("Arial", 18, QFont.Bold))  # Aumentamos fuente
        self.pago_input = QLineEdit()
        self.pago_input.setFont(QFont("Arial", 20, QFont.Bold))  # Tamaño de fuente mayor
        self.pago_input.setPlaceholderText("Ingrese el monto a pagar")
        self.pago_input.setFocus()
        self.pago_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #2c3e50;
                border-radius: 8px;
                padding: 2px;
                background-color: #ecf0f1;
                color: #2c3e50;
                font-size: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #e67e22;
                background-color: #fdebd0;
                color: #2c3e50;
                font-size: 40px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        pago_layout.addWidget(pago_label)
        pago_layout.addWidget(self.pago_input)
        layout.addLayout(pago_layout)

        # Tabla para mostrar los pagos
        self.pagos_table = QTableWidget()
        self.pagos_table.setColumnCount(2)
        self.pagos_table.setHorizontalHeaderLabels(["Método de Pago", "Monto"])
        self.pagos_table.horizontalHeader().setStretchLastSection(True)
        self.pagos_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pagos_table.setSelectionMode(QTableWidget.NoSelection)
        self.pagos_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pagos_table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                background-color: #f9f9f9;
                alternate-background-color: #e1e1e1;
                gridline-color: #cccccc;
                border: 1px solid #cccccc;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: 1px solid #2c3e50;
            }
        """)
        layout.addWidget(self.pagos_table)

        # Resumen (Restante o Cambio)
        resumen_layout = QVBoxLayout()
        self.resumen_label = QLabel(f"Restante: ${self.total:.2f}")
        self.resumen_label.setFont(QFont("Arial", 24, QFont.Bold))  # Letra más grande
        self.resumen_label.setAlignment(Qt.AlignCenter)
        self.resumen_label.setStyleSheet("""
            QLabel {
                background-color: orange; 
                color: white; 
                padding: 15px; 
                border-radius: 10px;
                font-size: 26px;
            }
        """)
        resumen_layout.addWidget(self.resumen_label)
        layout.addLayout(resumen_layout)

        # Placeholder para los botones de métodos de pago
        self.metodos_pago_placeholder = QWidget()
        self.metodos_pago_placeholder.setFixedHeight(60)
        layout.addWidget(self.metodos_pago_placeholder)

        metodos_pago_layout = QHBoxLayout()
        self.metodos_pago_placeholder.setLayout(metodos_pago_layout)

        # Botones de métodos de pago
        self.boton_efectivo = QPushButton("Efectivo")
        self.boton_transferencia = QPushButton("Transferencia")
        self.boton_posnet = QPushButton("Posnet")
        self.boton_credito = QPushButton("Crédito")  # Con acento

        botones_pago = [
            self.boton_efectivo,
            self.boton_transferencia,
            self.boton_posnet,
            self.boton_credito
        ]
        color_base = "#2980b9"
        color_hover_focus = "#e67e22"

        for b in botones_pago:
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_base};
                    color: white;
                    border: none;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_hover_focus};
                }}
                QPushButton:focus {{
                    background-color: {color_hover_focus};
                }}
            """)
            b.setFont(QFont("Arial", 16))
            b.setFixedSize(130, 40)
            b.hide()
            metodos_pago_layout.addWidget(b)

        metodos_pago_layout.insertStretch(0)
        metodos_pago_layout.addStretch()

        # Botones Confirmar y Cancelar
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        self.confirmar_button = QPushButton("Confirmar")
        self.confirmar_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.confirmar_button.clicked.connect(self.confirmar_factura)
        self.confirmar_button.setEnabled(False)
        self.confirmar_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:focus {
                background-color: #e67e22;
            }
        """)

        self.cancelar_button = QPushButton("Cancelar")
        self.cancelar_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.cancelar_button.clicked.connect(self.reject)
        self.cancelar_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:focus {
                background-color: #e67e22;
            }
        """)

        botones_layout.addStretch()
        botones_layout.addWidget(self.confirmar_button)
        botones_layout.addWidget(self.cancelar_button)
        botones_layout.addStretch()
        layout.addLayout(botones_layout)

        # Grupo de botones para métodos de pago
        self.grupo_botones_pago = QButtonGroup()
        self.grupo_botones_pago.setExclusive(True)
        self.grupo_botones_pago.addButton(self.boton_efectivo)
        self.grupo_botones_pago.addButton(self.boton_transferencia)
        self.grupo_botones_pago.addButton(self.boton_posnet)
        self.grupo_botones_pago.addButton(self.boton_credito)

        self.boton_efectivo.setChecked(True)

        # Conectar
        self.boton_efectivo.clicked.connect(lambda: self.seleccionar_metodo_pago("Efectivo"))
        self.boton_transferencia.clicked.connect(lambda: self.seleccionar_metodo_pago("Transferencia"))
        self.boton_posnet.clicked.connect(lambda: self.seleccionar_metodo_pago("Posnet"))
        self.boton_credito.clicked.connect(lambda: self.seleccionar_metodo_pago("Crédito"))

        self.pago_input.returnPressed.connect(self.mostrar_metodos_pago)

    def keyPressEvent(self, event):
        # Lógica de flechas izq/der para moverse entre botones de métodos de pago
        if self.metodos_pago_placeholder.isVisible():
            if event.key() in (Qt.Key_Left, Qt.Key_Right):
                botones = self.grupo_botones_pago.buttons()
                current_button = self.grupo_botones_pago.checkedButton()
                if current_button is None:
                    if botones:
                        botones[0].setChecked(True)
                        return
                try:
                    index = botones.index(current_button)
                except ValueError:
                    return
                if event.key() == Qt.Key_Right:
                    next_index = (index + 1) % len(botones)
                else:
                    next_index = (index - 1) % len(botones)
                botones[next_index].setChecked(True)
            elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                current_button = self.grupo_botones_pago.checkedButton()
                if current_button:
                    current_button.click()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def mostrar_metodos_pago(self):
        """Tras ingresar el monto y dar Enter, se muestran los botones de métodos de pago."""
        texto = self.pago_input.text().strip()
        if not texto:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido.")
            self.pago_input.setFocus()
            return
        try:
            monto = float(texto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido.")
            self.pago_input.setFocus()
            return

        self.metodos_pago_placeholder.show()
        for b in self.grupo_botones_pago.buttons():
            b.show()
        self.boton_efectivo.setFocus()  # Focus en Efectivo

    def seleccionar_metodo_pago(self, metodo):
        """Agrega un pago con el método seleccionado."""
        texto = self.pago_input.text().strip()
        try:
            monto = float(texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Monto inválido.")
            self.pago_input.setFocus()
            return
        if monto <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0.")
            self.pago_input.setFocus()
            return

        restante = self.total - sum(p["monto"] for p in self.pagos)
        # **Modificar la condición para permitir sobrepago solo en "Efectivo"**
        if metodo != "Efectivo" and monto > restante:
            QMessageBox.warning(self, "Error", f"El monto no puede exceder total.")
            self.pago_input.setFocus()
            return

        if metodo == "Crédito":
            self.gestionar_credito(monto)
        else:
            self.pagos.append({"metodo": metodo, "monto": monto})
            self.actualizar_tabla()
            self.actualizar_resumen()

        self.pago_input.clear()
        self.metodos_pago_placeholder.hide()
        for b in self.grupo_botones_pago.buttons():
            b.hide()

        if self.pagado >= self.total:
            self.confirmar_button.setFocus()
        else:
            self.pago_input.setFocus()

    def gestionar_credito(self, monto):
        """Selecciona el cliente y añade la deuda, aplicando descuento si es VIP."""
        clientes = cargar_clientes()
        if not clientes:
            QMessageBox.warning(self, "Sin Clientes", "No hay clientes registrados.")
            return

        nombres = [c["nombre"] for c in clientes]
        cliente_sel, ok = QInputDialog.getItem(
            self, "Seleccionar Cliente", "Seleccione el cliente:", nombres, editable=False
        )
        if ok and cliente_sel:
            for c in clientes:
                if c["nombre"] == cliente_sel:
                    # Verificar si el cliente es VIP
                    es_vip = c.get("vip", False)
                    monto_original = monto
                    if es_vip:
                        monto *= 0.90  # Aplicar el 10% de descuento
                        QMessageBox.information(
                            self, "Descuento VIP",
                            f"El cliente {cliente_sel} es VIP. Se aplicó un 10% de descuento: "
                            f"De ${monto_original:.2f} a ${monto:.2f}."
                        )
                        # Ajustar el total del ticket
                        self.total *= 0.90
                        self.total_display.setText(f"${self.total:.2f}")
                        self.actualizar_resumen()

                    # Guardar el monto descontado en la deuda
                    c["deuda"] += monto
                    if "ticketsdeuda" not in c:
                        c["ticketsdeuda"] = []

                    # Tomar número de ticket del parent (Caja)
                    caja_parent = self.parent()
                    if hasattr(caja_parent, "ticket_numero"):
                        c["ticketsdeuda"].append(caja_parent.ticket_numero)
                    else:
                        c["ticketsdeuda"].append("Desconocido")
                    break

            guardar_clientes(clientes)

            # Registrar el monto descontado en el ticket
            self.pagos.append({"metodo": "Crédito", "monto": monto})  # Guardar monto con descuento
            self.actualizar_tabla()
            self.actualizar_resumen()

            QMessageBox.information(
                self, "Crédito Registrado",
                f"El monto ${monto:.2f} ha sido cargado al cliente {cliente_sel}."
            )

    def actualizar_tabla(self):
        """Actualiza la tabla de pagos."""
        self.pagos_table.setRowCount(len(self.pagos))
        for row, pago in enumerate(self.pagos):
            metodo_item = QTableWidgetItem(pago["metodo"])
            metodo_item.setTextAlignment(Qt.AlignCenter)
            monto_item = QTableWidgetItem(f"${pago['monto']:.2f}")
            monto_item.setTextAlignment(Qt.AlignCenter)
            self.pagos_table.setItem(row, 0, metodo_item)
            self.pagos_table.setItem(row, 1, monto_item)

    def actualizar_resumen(self):
        """Calcula pagado vs total => restante/cambio => habilitar botón Confirmar."""
        self.pagado = sum(p["monto"] for p in self.pagos)
        restante = self.total - self.pagado
        if restante > 0:
            self.resumen_label.setText(f"Restante: ${restante:.2f}")
            self.resumen_label.setStyleSheet("""
                QLabel {
                    background-color: orange;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    font-size: 30px;
                }
            """)
            self.confirmar_button.setEnabled(False)
        else:
            cambio = abs(restante)
            self.resumen_label.setText(f"Cambio: ${cambio:.2f}")
            self.resumen_label.setStyleSheet("""
                QLabel {
                    background-color: green;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    font-size: 30px;
                }
            """)
            self.confirmar_button.setEnabled(True)
            self.confirmar_button.setFocus()

    def confirmar_factura(self):
        if self.pagado < self.total and not any(p["metodo"] == "Efectivo" for p in self.pagos):
            QMessageBox.warning(self, "Error", "El monto pagado es menor al total.")
            return
        self.metodos_pago = self.pagos.copy()
        self.cambio = abs(self.total - self.pagado)
        self.accept()

    def get_pago_data(self):
        """Devuelve la lista de pagos y el cambio."""
        return self.metodos_pago, self.cambio
