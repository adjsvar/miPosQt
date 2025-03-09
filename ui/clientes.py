# clientes.py

import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QDialog, QLineEdit, QHBoxLayout, QCheckBox, QFormLayout,
    QMenu, QAction
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QHeaderView


class AgregarClienteDialog(QDialog):
    """Diálogo personalizado para agregar un nuevo cliente."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Cliente")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Margen de 20px
        layout.setSpacing(20)  # Espacio entre elementos
        self.setLayout(layout)

        # Formulario para los campos de Nombre y Documento
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setSpacing(15)  # Espacio entre filas

        # Campo Nombre
        self.nombre_label = QLabel("Nombre:")
        self.nombre_label.setFont(QFont("Arial", 22))  # Aumentar tamaño de fuente
        self.nombre_input = QLineEdit()
        self.nombre_input.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        self.nombre_input.setPlaceholderText("Ingrese el nombre del cliente")
        self.nombre_input.setMinimumHeight(50)  # Altura ajustada
        form_layout.addRow(self.nombre_label, self.nombre_input)

        # Campo Documento (Opcional)
        self.documento_label = QLabel("Documento:")
        self.documento_label.setFont(QFont("Arial", 22))  # Aumentar tamaño de fuente
        self.documento_input = QLineEdit()
        self.documento_input.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        self.documento_input.setPlaceholderText("Ingrese el documento del cliente (Opcional)")
        self.documento_input.setMinimumHeight(50)  # Altura ajustada
        form_layout.addRow(self.documento_label, self.documento_input)

        layout.addLayout(form_layout)

        # Checkbox VIP
        self.vip_checkbox = QCheckBox("Cliente VIP (10% de descuento en deuda)")
        self.vip_checkbox.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        layout.addWidget(self.vip_checkbox)

        # Botones Aceptar y Cancelar
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()

        aceptar_button = QPushButton("Aceptar")
        aceptar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Tamaño de fuente aumentado
        aceptar_button.setFixedWidth(180)  # Ancho ajustado
        aceptar_button.setFixedHeight(60)  # Altura ajustada
        aceptar_button.clicked.connect(self.aceptar)

        cancelar_button = QPushButton("Cancelar")
        cancelar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Tamaño de fuente aumentado
        cancelar_button.setFixedWidth(180)  # Ancho ajustado
        cancelar_button.setFixedHeight(60)  # Altura ajustada
        cancelar_button.clicked.connect(self.reject)

        botones_layout.addWidget(aceptar_button)
        botones_layout.addWidget(cancelar_button)
        botones_layout.addStretch()

        layout.addLayout(botones_layout)

    def aceptar(self):
        """Valida y acepta los datos ingresados."""
        nombre = self.nombre_input.text().strip()
        documento = self.documento_input.text().strip()
        vip = self.vip_checkbox.isChecked()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
            self.nombre_input.setFocus()
            return

        # El campo documento es opcional, por lo que no se valida su llenado

        # Asignar atributos para acceder desde fuera
        self.nombre = nombre
        self.documento = documento
        self.vip = vip
        self.accept()

    def get_datos(self):
        """Devuelve los datos ingresados."""
        return {
            "nombre": self.nombre,
            "documento": self.documento,
            "vip": self.vip,
            "deuda": 0.0,
            "ticketsdeuda": []
        }


class PagarDeudaModal(QDialog):
    """Modal para pagar deuda existente."""

    def __init__(self, cliente, save_callback, update_table_callback, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.save_callback = save_callback
        self.update_table_callback = update_table_callback
        self.setWindowTitle("Pagar Deuda")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Margen de 20px
        layout.setSpacing(20)  # Espacio entre elementos
        self.setLayout(layout)

        # Deuda actual
        deuda_label = QLabel(f"Deuda Actual: ${self.cliente['deuda']:.2f}")
        deuda_label.setFont(QFont("Arial", 27, QFont.Bold))  # Fuente reducida a 3/4 de 36
        deuda_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(deuda_label)

        # Input para monto
        monto_layout = QHBoxLayout()
        monto_layout.setSpacing(15)  # Espacio entre label e input
        monto_label = QLabel("Monto a Pagar:")
        monto_label.setFont(QFont("Arial", 22))  # Fuente reducida a 3/4 de 30
        self.monto_input = QLineEdit()
        self.monto_input.setFont(QFont("Arial", 22))  # Fuente reducida a 3/4 de 30
        self.monto_input.setPlaceholderText("Ingrese el monto")
        self.monto_input.setMinimumHeight(52)  # Altura ajustada a 70 * 0.75 = 52.5
        monto_layout.addWidget(monto_label)
        monto_layout.addWidget(self.monto_input)
        layout.addLayout(monto_layout)
        self.monto_input.setFocus()

        # Botones para aceptar y cancelar
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(30)  # Espacio entre botones
        botones_layout.addStretch()

        aceptar_button = QPushButton("Aceptar")
        aceptar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Fuente reducida a 3/4 de 30
        aceptar_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        aceptar_button.setFixedWidth(180)  # Ancho ajustado a 240 * 0.75 = 180
        aceptar_button.clicked.connect(self.pagar_deuda)
        botones_layout.addWidget(aceptar_button)

        cancelar_button = QPushButton("Cancelar")
        cancelar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Fuente reducida a 3/4 de 30
        cancelar_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        cancelar_button.setFixedWidth(180)  # Ancho ajustado a 240 * 0.75 = 180
        cancelar_button.clicked.connect(self.reject)
        botones_layout.addWidget(cancelar_button)

        botones_layout.addStretch()
        layout.addLayout(botones_layout)

        # Lista de widgets para navegación con flechas
        self.focusable_widgets = [
            self.monto_input,
            aceptar_button,
            cancelar_button
        ]

    def keyPressEvent(self, event):
        """Maneja las teclas de flecha para navegar entre widgets."""
        if event.key() == Qt.Key_Down:
            self.navigate_focus(next=True)
            event.accept()
        elif event.key() == Qt.Key_Up:
            self.navigate_focus(next=False)
            event.accept()
        elif event.key() in (Qt.Key_Left, Qt.Key_Right):
            # Opcional: Manejar flechas izquierda y derecha si es necesario
            event.ignore()
        else:
            super().keyPressEvent(event)

    def navigate_focus(self, next=True):
        """Cambia el foco al siguiente o anterior widget en la lista."""
        current_widget = self.focusWidget()
        if current_widget in self.focusable_widgets:
            current_index = self.focusable_widgets.index(current_widget)
            if next:
                next_index = (current_index + 1) % len(self.focusable_widgets)
            else:
                next_index = (current_index - 1) % len(self.focusable_widgets)
            self.focusable_widgets[next_index].setFocus()

    def pagar_deuda(self):
        """Registra el pago y actualiza la tabla."""
        try:
            monto_text = self.monto_input.text().strip()
            monto = float(monto_text)
            if monto <= 0:
                raise ValueError("El monto debe ser positivo.")
            if monto > self.cliente["deuda"]:
                raise ValueError("El monto excede la deuda actual.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Ingrese un monto válido:\n{e}")
            self.monto_input.setFocus()
            return

        # Actualizar la deuda del cliente
        self.cliente["deuda"] -= monto

        # Registrar el pago en "ticketsdeuda"
        self.cliente["ticketsdeuda"].append({
            "monto": monto,
            "tipo": "pago_deuda"
        })

        self.save_callback()          # Guardar cambios en clientes.json
        self.update_table_callback()  # Refrescar tabla
        QMessageBox.information(self, "Éxito", "El pago se registró exitosamente.")
        self.accept()


class AgregarDeudaDialog(QDialog):
    """Diálogo para agregar deuda existente."""

    def __init__(self, cliente, save_callback, update_table_callback, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.save_callback = save_callback
        self.update_table_callback = update_table_callback
        self.setWindowTitle("Agregar Deuda")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Margen de 20px
        layout.setSpacing(20)  # Espacio entre elementos
        self.setLayout(layout)

        # Deuda actual
        deuda_label = QLabel(f"Deuda Actual: ${self.cliente['deuda']:.2f}")
        deuda_label.setFont(QFont("Arial", 27, QFont.Bold))  # Fuente reducida a 3/4 de 36
        deuda_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(deuda_label)

        # Input para monto
        monto_layout = QHBoxLayout()
        monto_layout.setSpacing(15)  # Espacio entre label e input
        monto_label = QLabel("Monto de Deuda:")
        monto_label.setFont(QFont("Arial", 22))  # Fuente reducida a 3/4 de 30
        self.monto_input = QLineEdit()
        self.monto_input.setFont(QFont("Arial", 22))  # Fuente reducida a 3/4 de 30
        self.monto_input.setPlaceholderText("Ingrese el monto de deuda")
        self.monto_input.setMinimumHeight(52)  # Altura ajustada a 70 * 0.75 = 52.5
        monto_layout.addWidget(monto_label)
        monto_layout.addWidget(self.monto_input)
        layout.addLayout(monto_layout)
        self.monto_input.setFocus()

        # Botones para aceptar y cancelar
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(30)  # Espacio entre botones
        botones_layout.addStretch()

        aceptar_button = QPushButton("Aceptar")
        aceptar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Fuente reducida a 3/4 de 30
        aceptar_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        aceptar_button.setFixedWidth(180)  # Ancho ajustado a 240 * 0.75 = 180
        aceptar_button.clicked.connect(self.agregar_deuda)
        botones_layout.addWidget(aceptar_button)

        cancelar_button = QPushButton("Cancelar")
        cancelar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Fuente reducida a 3/4 de 30
        cancelar_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        cancelar_button.setFixedWidth(180)  # Ancho ajustado a 240 * 0.75 = 180
        cancelar_button.clicked.connect(self.reject)
        botones_layout.addWidget(cancelar_button)

        botones_layout.addStretch()
        layout.addLayout(botones_layout)

        # Lista de widgets para navegación con flechas
        self.focusable_widgets = [
            self.monto_input,
            aceptar_button,
            cancelar_button
        ]

    def keyPressEvent(self, event):
        """Maneja las teclas de flecha para navegar entre widgets."""
        if event.key() == Qt.Key_Down:
            self.navigate_focus(next=True)
            event.accept()
        elif event.key() == Qt.Key_Up:
            self.navigate_focus(next=False)
            event.accept()
        elif event.key() in (Qt.Key_Left, Qt.Key_Right):
            # Opcional: Manejar flechas izquierda y derecha si es necesario
            event.ignore()
        else:
            super().keyPressEvent(event)

    def navigate_focus(self, next=True):
        """Cambia el foco al siguiente o anterior widget en la lista."""
        current_widget = self.focusWidget()
        if current_widget in self.focusable_widgets:
            current_index = self.focusable_widgets.index(current_widget)
            if next:
                next_index = (current_index + 1) % len(self.focusable_widgets)
            else:
                next_index = (current_index - 1) % len(self.focusable_widgets)
            self.focusable_widgets[next_index].setFocus()

    def agregar_deuda(self):
        """Agrega deuda manualmente con un descuento del 10% si el cliente es VIP."""
        try:
            monto_text = self.monto_input.text().strip()
            monto = float(monto_text)
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a 0.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Ingrese un monto válido:\n{e}")
            self.monto_input.setFocus()
            return

        if self.cliente["vip"]:
            descuento = monto * 0.1
            monto_descuento = monto - descuento
            self.cliente["deuda"] += monto_descuento

            # Registrar la deuda agregada con el descuento aplicado
            self.cliente["ticketsdeuda"].append({
                "monto": monto_descuento,
                "tipo": "agregar_deuda",
                "descuento_aplicado": descuento
            })

            mensaje = (
                f"Se ha agregado una deuda de ${monto_descuento:.2f} "
                f"con un descuento del 10% (${descuento:.2f})."
            )
        else:
            monto_descuento = monto
            self.cliente["deuda"] += monto_descuento

            # Registrar la deuda agregada sin descuento
            self.cliente["ticketsdeuda"].append({
                "monto": monto_descuento,
                "tipo": "agregar_deuda",
                "descuento_aplicado": 0.0
            })

            mensaje = f"Se ha agregado una deuda de ${monto_descuento:.2f}."

        self.save_callback()
        self.update_table_callback()

        QMessageBox.information(
            self, "Deuda Agregada", mensaje
        )
        self.accept()


class ClienteModal(QDialog):
    """Diálogo para editar un cliente existente."""

    def __init__(self, cliente, save_callback, update_table_callback, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.save_callback = save_callback
        self.update_table_callback = update_table_callback
        self.setWindowTitle(f"Editar Cliente - {cliente['nombre']}")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Margen de 20px
        layout.setSpacing(20)  # Espacio entre elementos
        self.setLayout(layout)

        # Formulario para los campos de Nombre y Documento
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setSpacing(15)  # Espacio entre filas

        # Campo Nombre
        self.nombre_label = QLabel("Nombre:")
        self.nombre_label.setFont(QFont("Arial", 22))  # Aumentar tamaño de fuente
        self.nombre_input = QLineEdit()
        self.nombre_input.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        self.nombre_input.setPlaceholderText("Ingrese el nombre del cliente")
        self.nombre_input.setMinimumHeight(50)  # Altura ajustada
        form_layout.addRow(self.nombre_label, self.nombre_input)

        # Campo Documento (Opcional)
        self.documento_label = QLabel("Documento:")
        self.documento_label.setFont(QFont("Arial", 22))  # Aumentar tamaño de fuente
        self.documento_input = QLineEdit()
        self.documento_input.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        self.documento_input.setPlaceholderText("Ingrese el documento del cliente (Opcional)")
        self.documento_input.setMinimumHeight(50)  # Altura ajustada
        form_layout.addRow(self.documento_label, self.documento_input)

        layout.addLayout(form_layout)

        # Asignar valores existentes al editar
        self.nombre_input.setText(self.cliente["nombre"])
        self.documento_input.setText(self.cliente["documento"])

        # Checkbox VIP
        self.vip_checkbox = QCheckBox("Cliente VIP (10% de descuento en deuda)")
        self.vip_checkbox.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        self.vip_checkbox.setChecked(self.cliente["vip"])
        layout.addWidget(self.vip_checkbox)

        # Botones para pagar y agregar deuda
        botones_deuda_layout = QHBoxLayout()
        botones_deuda_layout.setSpacing(30)  # Espacio entre botones

        self.pagar_button = QPushButton("Pagar Deuda")
        self.pagar_button.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        self.pagar_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        self.pagar_button.setFixedWidth(225)  # Ancho ajustado a 300 * 0.75 = 225
        self.pagar_button.clicked.connect(self.abrir_modal_pagar_deuda)
        botones_deuda_layout.addWidget(self.pagar_button)

        self.agregar_deuda_button = QPushButton("Agregar Deuda")
        self.agregar_deuda_button.setFont(QFont("Arial", 22))  # Tamaño de fuente aumentado
        self.agregar_deuda_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        self.agregar_deuda_button.setFixedWidth(225)  # Ancho ajustado a 300 * 0.75 = 225
        self.agregar_deuda_button.clicked.connect(self.agregar_deuda)
        botones_deuda_layout.addWidget(self.agregar_deuda_button)

        layout.addLayout(botones_deuda_layout)

        # Botones para aceptar y cancelar
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(30)  # Espacio entre botones
        botones_layout.addStretch()

        aceptar_button = QPushButton("Aceptar")
        aceptar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Tamaño de fuente aumentado
        aceptar_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        aceptar_button.setFixedWidth(180)  # Ancho ajustado a 240 * 0.75 = 180
        aceptar_button.clicked.connect(self.aceptar)
        botones_layout.addWidget(aceptar_button)

        cancelar_button = QPushButton("Cancelar")
        cancelar_button.setFont(QFont("Arial", 22, QFont.Bold))  # Tamaño de fuente aumentado
        cancelar_button.setFixedHeight(60)  # Altura ajustada a 80 * 0.75 = 60
        cancelar_button.setFixedWidth(180)  # Ancho ajustado a 240 * 0.75 = 180
        cancelar_button.clicked.connect(self.reject)
        botones_layout.addWidget(cancelar_button)

        botones_layout.addStretch()
        layout.addLayout(botones_layout)

        # Lista de widgets para navegación con flechas
        self.focusable_widgets = [
            self.nombre_input,
            self.documento_input,
            self.vip_checkbox,
            self.pagar_button,
            self.agregar_deuda_button,
            aceptar_button,
            cancelar_button
        ]

    def keyPressEvent(self, event):
        """Maneja las teclas de flecha para navegar entre widgets."""
        if event.key() == Qt.Key_Down:
            self.navigate_focus(next=True)
            event.accept()
        elif event.key() == Qt.Key_Up:
            self.navigate_focus(next=False)
            event.accept()
        elif event.key() in (Qt.Key_Left, Qt.Key_Right):
            # Opcional: Manejar flechas izquierda y derecha si es necesario
            event.ignore()
        else:
            super().keyPressEvent(event)

    def navigate_focus(self, next=True):
        """Cambia el foco al siguiente o anterior widget en la lista."""
        current_widget = self.focusWidget()
        if current_widget in self.focusable_widgets:
            current_index = self.focusable_widgets.index(current_widget)
            if next:
                next_index = (current_index + 1) % len(self.focusable_widgets)
            else:
                next_index = (current_index - 1) % len(self.focusable_widgets)
            self.focusable_widgets[next_index].setFocus()

    def abrir_modal_pagar_deuda(self):
        """Abre un modal para registrar el pago de deuda solo si hay deuda."""
        if self.cliente["deuda"] <= 0:
            QMessageBox.information(self, "Sin Deuda", "Este cliente no tiene deuda para pagar.")
            return

        modal = PagarDeudaModal(
            self.cliente,
            self.save_callback,
            self.update_table_callback,
            self
        )
        modal.exec_()

    def agregar_deuda(self):
        """Abre un modal para agregar deuda manualmente con un descuento del 10% si el cliente es VIP."""
        modal = AgregarDeudaDialog(
            self.cliente,
            self.save_callback,
            self.update_table_callback,
            self
        )
        modal.exec_()

    def aceptar(self):
        """Guarda los cambios realizados al cliente."""
        nuevo_nombre = self.nombre_input.text().strip()
        nuevo_documento = self.documento_input.text().strip()
        vip = self.vip_checkbox.isChecked()

        if not nuevo_nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
            self.nombre_input.setFocus()
            return

        # El campo documento es opcional, por lo que no se valida su llenado

        # Verificar si el nuevo documento ya existe en otro cliente (si no está vacío)
        if nuevo_documento:
            for c in self.parent().clientes:
                if c["documento"] == nuevo_documento and c != self.cliente:
                    QMessageBox.warning(self, "Error", "El documento ya está en uso.")
                    self.documento_input.setFocus()
                    return

        self.cliente["nombre"] = nuevo_nombre
        self.cliente["documento"] = nuevo_documento
        self.cliente["vip"] = vip

        self.save_callback()
        self.update_table_callback()
        self.accept()


class Clientes(QWidget):
    """Clase principal para gestionar los clientes."""

    CLIENTES_FILE = "./db/clientes.json"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clientes")
        self.setMinimumSize(800, 500)  # Tamaño original: 800x500
        self.init_ui()
        self.load_clientes()  # Carga de clientes al iniciar

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Margen de 20px
        layout.setSpacing(20)  # Espacio entre elementos
        self.setLayout(layout)

        # Título
        title = QLabel("Lista de Clientes")
        title.setFont(QFont("Arial", 25, QFont.Bold))  # Tamaño de fuente original
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Tabla de clientes
        self.clientes_table = QTableWidget()
        self.clientes_table.setColumnCount(3)  # 3 columnas: Nombre, Documento, Deuda
        self.clientes_table.setHorizontalHeaderLabels(["Nombre", "Documento", "Deuda"])
        self.clientes_table.horizontalHeader().setStretchLastSection(True)
        self.clientes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.clientes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.clientes_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.clientes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.clientes_table.setSelectionMode(QTableWidget.SingleSelection)
        self.clientes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.clientes_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clientes_table.customContextMenuRequested.connect(self.show_context_menu)
        self.clientes_table.setStyleSheet("""
            QTableWidget {
                font-size: 15px;  /* Tamaño de fuente original */
                background-color: #f9f9f9;
                alternate-background-color: #e1e1e1;
                gridline-color: #cccccc;
                border: 1px solid #cccccc;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 15px;  /* Tamaño de fuente original */
                border: 1px solid #2c3e50;
            }
        """)
        self.clientes_table.setAlternatingRowColors(True)
        self.clientes_table.itemDoubleClicked.connect(self.abrir_modal_cliente)
        layout.addWidget(self.clientes_table)

        # Botón para agregar cliente
        self.agregar_button = QPushButton("Agregar Cliente")
        self.agregar_button.setFont(QFont("Arial", 18, QFont.Bold))  # Tamaño de fuente original
        self.agregar_button.setFixedHeight(50)  # Altura original
        self.agregar_button.clicked.connect(self.agregar_cliente)
        layout.addWidget(self.agregar_button, alignment=Qt.AlignCenter)

    def load_clientes(self):
        """Carga los clientes desde el archivo JSON y actualiza la tabla."""
        if not os.path.exists(self.CLIENTES_FILE):
            self.create_clientes_file()

        try:
            with open(self.CLIENTES_FILE, "r", encoding="utf-8") as file:
                self.clientes = json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo de clientes: {e}")
            self.clientes = []

        # Asegurarnos de que cada cliente tenga las claves "ticketsdeuda", "documento" y "vip"
        for cliente in self.clientes:
            if "ticketsdeuda" not in cliente:
                cliente["ticketsdeuda"] = []
            if "documento" not in cliente:
                cliente["documento"] = ""
            if "vip" not in cliente:
                cliente["vip"] = False

        self.save_clientes()  # Guarda cualquier cambio en la estructura

        # Actualizar la interfaz
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Actualiza la tabla de clientes."""
        self.clientes_table.blockSignals(True)  # Bloquear señales para evitar recursiones
        self.clientes_table.setRowCount(len(self.clientes))
        for row, cliente in enumerate(self.clientes):
            nombre_item = QTableWidgetItem(cliente["nombre"])
            nombre_item.setTextAlignment(Qt.AlignCenter)
            nombre_item.setFont(QFont("Arial", 15))  # Tamaño de fuente original

            documento_item = QTableWidgetItem(cliente["documento"])
            documento_item.setTextAlignment(Qt.AlignCenter)
            documento_item.setFont(QFont("Arial", 15))  # Tamaño de fuente original

            deuda_item = QTableWidgetItem(f"${cliente['deuda']:.2f}")
            deuda_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            deuda_item.setFont(QFont("Arial", 15))  # Tamaño de fuente original

            # Resaltar fila si es VIP
            if cliente["vip"]:
                nombre_item.setBackground(QColor(255, 255, 200))  # Amarillo claro
                documento_item.setBackground(QColor(255, 255, 200))
                deuda_item.setBackground(QColor(255, 255, 200))

            self.clientes_table.setItem(row, 0, nombre_item)
            self.clientes_table.setItem(row, 1, documento_item)
            self.clientes_table.setItem(row, 2, deuda_item)

            # Establecer una altura fija para todas las filas
            self.clientes_table.setRowHeight(row, 45)  # Altura original

        self.clientes_table.clearSelection()  # Limpiar selección para evitar señales
        self.clientes_table.blockSignals(False)  # Desbloquear señales
        self.clientes_table.repaint()

    def abrir_modal_cliente(self, item):
        """Abre un modal para editar información del cliente seleccionado."""
        row = item.row()
        cliente = self.clientes[row]
        modal = ClienteModal(
            cliente,
            self.save_clientes,
            self.actualizar_tabla,
            self
        )
        modal.exec_()

    def agregar_cliente(self):
        """Agrega un nuevo cliente."""
        dialog = AgregarClienteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            datos = dialog.get_datos()

            # Verificar si el documento ya existe (si no está vacío)
            if datos["documento"]:
                for cliente in self.clientes:
                    if cliente["documento"] == datos["documento"]:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"Ya existe un cliente con el documento '{datos['documento']}'."
                        )
                        return

            self.clientes.append(datos)
            self.save_clientes()
            self.load_clientes()
        # Enfocar el botón después de agregar un cliente
        self.agregar_button.setFocus()

    def eliminar_cliente(self, row):
        """Elimina un cliente seleccionado."""
        cliente = self.clientes[row]
        respuesta = QMessageBox.question(
            self, "Eliminar Cliente", f"¿Está seguro de eliminar al cliente '{cliente['nombre']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            del self.clientes[row]
            self.save_clientes()
            self.load_clientes()

    def save_clientes(self):
        """Guarda la lista de clientes en el archivo JSON."""
        try:
            with open(self.CLIENTES_FILE, "w", encoding="utf-8") as file:
                json.dump(self.clientes, file, indent=4, ensure_ascii=False)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo de clientes: {e}")

    def create_clientes_file(self):
        """Crea un archivo JSON de clientes si no existe."""
        try:
            os.makedirs(os.path.dirname(self.CLIENTES_FILE), exist_ok=True)
            with open(self.CLIENTES_FILE, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4, ensure_ascii=False)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el archivo de clientes: {e}")

    def show_context_menu(self, pos):
        """Muestra un menú contextual para editar o eliminar clientes."""
        context_menu = QMenu(self)
        selected_row = self.clientes_table.rowAt(pos.y())
        if selected_row >= 0:
            editar_action = QAction("Editar Cliente", self)
            editar_action.triggered.connect(lambda: self.abrir_modal_cliente(self.clientes_table.item(selected_row, 0)))
            context_menu.addAction(editar_action)

            eliminar_action = QAction("Eliminar Cliente", self)
            eliminar_action.triggered.connect(lambda: self.eliminar_cliente(selected_row))
            context_menu.addAction(eliminar_action)

        context_menu.exec_(self.clientes_table.viewport().mapToGlobal(pos))

    def keyPressEvent(self, event):
        """Elimina un cliente seleccionado con la tecla Supr."""
        if event.key() == Qt.Key_Delete:
            selected_row = self.clientes_table.currentRow()
            if selected_row >= 0:
                self.eliminar_cliente(selected_row)
        else:
            super().keyPressEvent(event)


# Código para ejecutar la aplicación si este archivo se ejecuta directamente
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ventana = Clientes()
    ventana.show()
    sys.exit(app.exec_())
