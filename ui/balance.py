# ui/balance.py

import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGridLayout,
    QInputDialog
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

        # Etiquetas para las cuentas - CAMBIO: de "BBVA" y "MercadoPago" a "Dinero en Cuenta"
        self.crear_etiqueta_cuenta("Efectivo", 0, 0, grid_layout)
        self.crear_etiqueta_cuenta("Dinero en Cuenta", 0, 1, grid_layout)
        self.crear_etiqueta_cuenta("Total", 0, 2, grid_layout)

        # Labels para mostrar los saldos
        self.efectivo_label = self.crear_label_saldo(1, 0, grid_layout)
        self.dinero_cuenta_label = self.crear_label_saldo(1, 1, grid_layout)
        self.total_label = self.crear_label_saldo(1, 2, grid_layout, is_total=True)

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
        self.crear_etiqueta_cuenta("Dinero en Cuenta", 0, 1, edit_grid)

        # Inputs para editar los saldos
        self.efectivo_input = self.crear_input_saldo(1, 0, edit_grid)
        self.dinero_cuenta_input = self.crear_input_saldo(1, 1, edit_grid)

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
        self.historial_table.setColumnCount(4)
        self.historial_table.setHorizontalHeaderLabels(["Fecha", "Efectivo", "Dinero en Cuenta", "Nota"])
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
        # Inicializar claves si no existen
        if "efectivo" not in self.balance_data:
            self.balance_data["efectivo"] = 0.0
        if "dinero_cuenta" not in self.balance_data:
            self.balance_data["dinero_cuenta"] = 0.0
            
        efectivo = self.balance_data.get("efectivo", 0)
        dinero_cuenta = self.balance_data.get("dinero_cuenta", 0)
        total = efectivo + dinero_cuenta

        # Actualizar labels
        self.efectivo_label.setText(f"${efectivo:.2f}")
        self.dinero_cuenta_label.setText(f"${dinero_cuenta:.2f}")
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

            # Dinero en Cuenta
            dinero_cuenta_item = QTableWidgetItem(f"${ajuste.get('dinero_cuenta', 0):.2f}")
            dinero_cuenta_item.setTextAlignment(Qt.AlignCenter)
            self.historial_table.setItem(i, 2, dinero_cuenta_item)

            # Nota
            nota_item = QTableWidgetItem(ajuste.get("nota", ""))
            nota_item.setTextAlignment(Qt.AlignCenter)
            self.historial_table.setItem(i, 3, nota_item)

    def guardar_cambios(self):
        """Procesa y guarda los cambios en los balances."""
        try:
            # Obtener los nuevos valores (si se ingresaron)
            nuevo_efectivo = self.efectivo_input.text().strip()
            nuevo_dinero_cuenta = self.dinero_cuenta_input.text().strip()

            # Si no se ingresó ningún valor, mostrar mensaje y salir
            if not nuevo_efectivo and not nuevo_dinero_cuenta:
                QMessageBox.warning(self, "Aviso", "No se ingresó ningún valor para ajustar.")
                return

            # Pedir una nota para el registro mediante QInputDialog
            nota, ok = QInputDialog.getText(self, "Nota", "Ingrese una nota para este ajuste:")
            if not ok:
                return

            # Inicializar valores en caso de que no existan en el balance_data
            if "efectivo" not in self.balance_data:
                self.balance_data["efectivo"] = 0.0
            if "dinero_cuenta" not in self.balance_data:
                self.balance_data["dinero_cuenta"] = 0.0

            # Actualizar valores sólo si se ingresaron
            cambios = False
            if nuevo_efectivo:
                self.balance_data["efectivo"] = float(nuevo_efectivo)
                cambios = True
            
            if nuevo_dinero_cuenta:
                self.balance_data["dinero_cuenta"] = float(nuevo_dinero_cuenta)
                cambios = True

            # Si hubo cambios, agregar al historial
            if cambios:
                # Crear registro para historial
                registro = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "efectivo": self.balance_data["efectivo"],
                    "dinero_cuenta": self.balance_data["dinero_cuenta"],
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
                self.dinero_cuenta_input.clear()
                
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
                    "dinero_cuenta": 0.0,
                    "historial": []
                }
                with open(ruta_balance, "w", encoding="utf-8") as file:
                    json.dump(balance_inicial, file, indent=4)
                return balance_inicial
            else:
                with open(ruta_balance, "r", encoding="utf-8") as file:
                    balance = json.load(file)
                    
                # Convertir de formato antiguo a nuevo si es necesario
                if "mercadopago" in balance and "bbva" in balance:
                    dinero_cuenta = balance.get("mercadopago", 0) + balance.get("bbva", 0)
                    balance["dinero_cuenta"] = dinero_cuenta
                    # Eliminar claves antiguas
                    if "mercadopago" in balance:
                        del balance["mercadopago"]
                    if "bbva" in balance:
                        del balance["bbva"]
                    
                    # Actualizar histórico si existe
                    if "historial" in balance:
                        for registro in balance["historial"]:
                            if "mercadopago" in registro and "bbva" in registro:
                                registro["dinero_cuenta"] = registro.get("mercadopago", 0) + registro.get("bbva", 0)
                                if "mercadopago" in registro:
                                    del registro["mercadopago"]
                                if "bbva" in registro:
                                    del registro["bbva"]
                                    
                    # Guardar cambios
                    with open(ruta_balance, "w", encoding="utf-8") as file:
                        json.dump(balance, file, indent=4)
                        
                return balance
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar balance: {str(e)}")
            return {"efectivo": 0.0, "dinero_cuenta": 0.0, "historial": []}

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