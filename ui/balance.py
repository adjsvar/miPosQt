# ui/balance.py

import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGridLayout
)
from PyQt5.QtGui import QFont, QDoubleValidator, QColor
from PyQt5.QtCore import Qt


class Balance(QWidget):
    def __init__(self):
        super().__init__()
        self.balance_data = self.cargar_balance()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Título principal
        title = QLabel("Balance de Cuentas")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Grid para mostrar los saldos actuales
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        layout.addLayout(grid_layout)

        # Etiquetas para las cuentas
        self.crear_etiqueta_cuenta("Efectivo", 0, 0, grid_layout)
        self.crear_etiqueta_cuenta("MercadoPago", 0, 1, grid_layout)
        self.crear_etiqueta_cuenta("BBVA", 0, 2, grid_layout)
        self.crear_etiqueta_cuenta("Total", 0, 3, grid_layout)

        # Labels para mostrar los saldos
        self.efectivo_label = self.crear_label_saldo(1, 0, grid_layout)
        self.mercadopago_label = self.crear_label_saldo(1, 1, grid_layout)
        self.bbva_label = self.crear_label_saldo(1, 2, grid_layout)
        self.total_label = self.crear_label_saldo(1, 3, grid_layout, is_total=True)

        # Grid para editar los saldos
        edit_grid = QGridLayout()
        edit_grid.setSpacing(20)
        layout.addLayout(edit_grid)

        # Sección de título para ajustes
        ajuste_title = QLabel("Ajustar Balances")
        ajuste_title.setFont(QFont("Arial", 18, QFont.Bold))
        ajuste_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(ajuste_title)

        # Etiquetas para editar
        self.crear_etiqueta_cuenta("Efectivo", 0, 0, edit_grid)
        self.crear_etiqueta_cuenta("MercadoPago", 0, 1, edit_grid)
        self.crear_etiqueta_cuenta("BBVA", 0, 2, edit_grid)

        # Inputs para editar los saldos
        self.efectivo_input = self.crear_input_saldo(1, 0, edit_grid)
        self.mercadopago_input = self.crear_input_saldo(1, 1, edit_grid)
        self.bbva_input = self.crear_input_saldo(1, 2, edit_grid)

        # Botón para guardar cambios
        guardar_button = QPushButton("Guardar Cambios")
        guardar_button.setFont(QFont("Arial", 16, QFont.Bold))
        guardar_button.setFixedHeight(50)
        guardar_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        guardar_button.clicked.connect(self.guardar_cambios)
        layout.addWidget(guardar_button)

        # Historial de cambios (título)
        historial_title = QLabel("Historial de Ajustes")
        historial_title.setFont(QFont("Arial", 18, QFont.Bold))
        historial_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(historial_title)

        # Tabla de historial
        self.historial_table = QTableWidget()
        self.historial_table.setColumnCount(5)
        self.historial_table.setHorizontalHeaderLabels(["Fecha", "Efectivo", "MercadoPago", "BBVA", "Nota"])
        self.historial_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.historial_table.verticalHeader().setVisible(False)
        self.historial_table.setFont(QFont("Arial", 14))
        self.historial_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #b3d9ff;
                color: black;
            }
            QHeaderView::section {
                background-color: #d3d3d3;
                font-weight: bold;
                border: 1px solid black;
                padding: 4px;
            }
        """)
        layout.addWidget(self.historial_table)

        # Cargar datos iniciales
        self.actualizar_ui()

    def crear_etiqueta_cuenta(self, texto, fila, columna, layout):
        """Crea una etiqueta para el nombre de la cuenta."""
        label = QLabel(texto)
        label.setFont(QFont("Arial", 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 5px;
            }
        """)
        layout.addWidget(label, fila, columna)
        return label

    def crear_label_saldo(self, fila, columna, layout, is_total=False):
        """Crea un label para mostrar el saldo de una cuenta."""
        label = QLabel("$0.00")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        
        # Estilo diferente para el total
        if is_total:
            label.setStyleSheet("""
                QLabel {
                    background-color: #f9e79f;
                    color: #2c3e50;
                    padding: 10px;
                    border-radius: 5px;
                }
            """)
        else:
            label.setStyleSheet("""
                QLabel {
                    background-color: #eaeded;
                    color: #2c3e50;
                    padding: 10px;
                    border-radius: 5px;
                }
            """)
        
        layout.addWidget(label, fila, columna)
        return label

    def crear_input_saldo(self, fila, columna, layout):
        """Crea un input para editar el saldo de una cuenta."""
        input_field = QLineEdit()
        input_field.setFont(QFont("Arial", 16))
        input_field.setPlaceholderText("Nuevo saldo...")
        input_field.setValidator(QDoubleValidator(0, 999999999.99, 2))
        input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(input_field, fila, columna)
        return input_field

    def actualizar_ui(self):
        """Actualiza la interfaz con los datos de balance actuales."""
        efectivo = self.balance_data.get("efectivo", 0)
        mercadopago = self.balance_data.get("mercadopago", 0)
        bbva = self.balance_data.get("bbva", 0)
        total = efectivo + mercadopago + bbva

        # Actualizar labels
        self.efectivo_label.setText(f"${efectivo:.2f}")
        self.mercadopago_label.setText(f"${mercadopago:.2f}")
        self.bbva_label.setText(f"${bbva:.2f}")
        self.total_label.setText(f"${total:.2f}")

        # Cargar historial
        self.cargar_historial()

    def cargar_historial(self):
        """Carga el historial de ajustes en la tabla."""
        historial = self.balance_data.get("historial", [])
        self.historial_table.setRowCount(len(historial))

        for i, ajuste in enumerate(historial):
            # Fecha
            fecha_item = QTableWidgetItem(ajuste.get("fecha", ""))
            fecha_item.setTextAlignment(Qt.AlignCenter)
            self.historial_table.setItem(i, 0, fecha_item)

            # Efectivo
            efectivo_item = QTableWidgetItem(f"${ajuste.get('efectivo', 0):.2f}")
            efectivo_item.setTextAlignment(Qt.AlignCenter)
            self.historial_table.setItem(i, 1, efectivo_item)

            # MercadoPago
            mp_item = QTableWidgetItem(f"${ajuste.get('mercadopago', 0):.2f}")
            mp_item.setTextAlignment(Qt.AlignCenter)
            self.historial_table.setItem(i, 2, mp_item)

            # BBVA
            bbva_item = QTableWidgetItem(f"${ajuste.get('bbva', 0):.2f}")
            bbva_item.setTextAlignment(Qt.AlignCenter)
            self.historial_table.setItem(i, 3, bbva_item)

            # Nota
            nota_item = QTableWidgetItem(ajuste.get("nota", ""))
            nota_item.setTextAlignment(Qt.AlignCenter)
            self.historial_table.setItem(i, 4, nota_item)

    def guardar_cambios(self):
        """Procesa y guarda los cambios en los balances."""
        try:
            # Obtener los nuevos valores (si se ingresaron)
            nuevo_efectivo = self.efectivo_input.text().strip()
            nuevo_mercadopago = self.mercadopago_input.text().strip()
            nuevo_bbva = self.bbva_input.text().strip()

            # Si no se ingresó ningún valor, mostrar mensaje y salir
            if not nuevo_efectivo and not nuevo_mercadopago and not nuevo_bbva:
                QMessageBox.warning(self, "Aviso", "No se ingresó ningún valor para ajustar.")
                return

            # Pedir una nota para el registro
            nota, ok = QMessageBox.getText(self, "Nota", "Ingrese una nota para este ajuste:")
            if not ok:
                return

            # Actualizar valores sólo si se ingresaron
            cambios = False
            if nuevo_efectivo:
                self.balance_data["efectivo"] = float(nuevo_efectivo)
                cambios = True
            
            if nuevo_mercadopago:
                self.balance_data["mercadopago"] = float(nuevo_mercadopago)
                cambios = True
            
            if nuevo_bbva:
                self.balance_data["bbva"] = float(nuevo_bbva)
                cambios = True

            # Si hubo cambios, agregar al historial
            if cambios:
                # Crear registro para historial
                registro = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "efectivo": self.balance_data["efectivo"],
                    "mercadopago": self.balance_data["mercadopago"],
                    "bbva": self.balance_data["bbva"],
                    "nota": nota
                }
                
                # Agregar al historial
                if "historial" not in self.balance_data:
                    self.balance_data["historial"] = []
                
                self.balance_data["historial"].insert(0, registro)  # Insertar al inicio para mostrar más reciente primero
                
                # Guardar en archivo
                self.guardar_balance()
                
                # Actualizar UI
                self.actualizar_ui()
                
                # Limpiar inputs
                self.efectivo_input.clear()
                self.mercadopago_input.clear()
                self.bbva_input.clear()
                
                QMessageBox.information(self, "Éxito", "Balances actualizados correctamente.")
        
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese valores numéricos válidos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {str(e)}")

    def cargar_balance(self):
        """Carga los datos de balance desde el archivo JSON."""
        try:
            ruta_balance = "./db/balance.json"
            if not os.path.exists(ruta_balance):
                # Si no existe el archivo, crear uno con valores iniciales
                balance_inicial = {
                    "efectivo": 0.0,
                    "mercadopago": 0.0,
                    "bbva": 0.0,
                    "historial": []
                }
                with open(ruta_balance, "w", encoding="utf-8") as file:
                    json.dump(balance_inicial, file, indent=4)
                return balance_inicial
            else:
                with open(ruta_balance, "r", encoding="utf-8") as file:
                    return json.load(file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar balance: {str(e)}")
            return {"efectivo": 0.0, "mercadopago": 0.0, "bbva": 0.0, "historial": []}

    def guardar_balance(self):
        """Guarda los datos de balance en el archivo JSON."""
        try:
            with open("./db/balance.json", "w", encoding="utf-8") as file:
                json.dump(self.balance_data, file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar balance: {str(e)}")

    def focus_on_entry(self):
        """Establece el foco en el primer campo de entrada."""
        self.efectivo_input.setFocus()