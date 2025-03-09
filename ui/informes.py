# ui/informes.py

import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QHBoxLayout, QCheckBox, QDialog,
    QDialogButtonBox, QSpinBox, QFormLayout
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget


class EditarDescuentoDialog(QDialog):
    def __init__(self, nombre_producto, precio_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Descuento")
        self.setModal(True)
        self.setFixedSize(700, 250)  # Tamaño fijo actualizado

        # Layout principal
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Área con fondo azul para mostrar nombre y precio
        info_layout = QVBoxLayout()
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: #ADD8E6; border-radius: 5px;")  # Azul claro con bordes redondeados
        info_widget.setLayout(info_layout)

        # Nombre del producto (sin prefijo)
        nombre_label = QLabel(f"{nombre_producto}")
        nombre_label.setFont(QFont("Arial", 16))
        nombre_label.setAlignment(Qt.AlignCenter)
        nombre_label.setWordWrap(True)  # Permite envolver el texto en múltiples líneas
        info_layout.addWidget(nombre_label)

        # Precio actual
        precio_label = QLabel(f"Precio Actual: {precio_actual:.2f}")
        precio_label.setFont(QFont("Arial", 16))
        precio_label.setAlignment(Qt.AlignCenter)
        precio_label.setWordWrap(True)  # Permite envolver el texto en múltiples líneas
        info_layout.addWidget(precio_label)

        layout.addWidget(info_widget)

        # Spacer
        layout.addSpacing(20)

        # Input para el descuento
        form_layout = QFormLayout()
        self.spin_descuento = QSpinBox()
        self.spin_descuento.setRange(0, 100)
        self.spin_descuento.setValue(0)  # Inicializado en 0
        self.spin_descuento.setFont(QFont("Arial", 16))
        form_layout.addRow("Descuento (%)", self.spin_descuento)
        layout.addLayout(form_layout)

        # Spacer
        layout.addSpacing(20)

        # Botones Aceptar y Cancelar
        botones = QDialogButtonBox()
        btn_aceptar = QPushButton("Aceptar")
        btn_cancelar = QPushButton("Cancelar")
        botones.addButton(btn_aceptar, QDialogButtonBox.AcceptRole)
        botones.addButton(btn_cancelar, QDialogButtonBox.RejectRole)
        btn_aceptar.setFont(QFont("Arial", 16))
        btn_cancelar.setFont(QFont("Arial", 16))
        btn_aceptar.setStyleSheet("padding: 3px;")
        btn_cancelar.setStyleSheet("padding: 3px;")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def get_descuento(self):
        return self.spin_descuento.value()


class OfertarLoteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ofertar Productos <30 Días")
        self.setModal(True)
        self.setFixedSize(700, 250)  # Tamaño fijo actualizado

        # Layout principal
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Área de instrucción
        instruccion_label = QLabel("Ingrese el porcentaje de descuento para aplicar:")
        instruccion_label.setFont(QFont("Arial", 16))
        instruccion_label.setAlignment(Qt.AlignCenter)
        instruccion_label.setWordWrap(True)  # Permite envolver el texto en múltiples líneas
        layout.addWidget(instruccion_label)

        # Input para el descuento
        form_layout = QFormLayout()
        self.spin_descuento = QSpinBox()
        self.spin_descuento.setRange(0, 100)
        self.spin_descuento.setValue(0)  # Inicializado en 0
        self.spin_descuento.setFont(QFont("Arial", 16))
        form_layout.addRow("Descuento (%)", self.spin_descuento)
        layout.addLayout(form_layout)

        # Spacer
        layout.addSpacing(20)

        # Botones Aceptar y Cancelar
        botones = QDialogButtonBox()
        btn_aceptar = QPushButton("Aceptar")
        btn_cancelar = QPushButton("Cancelar")
        botones.addButton(btn_aceptar, QDialogButtonBox.AcceptRole)
        botones.addButton(btn_cancelar, QDialogButtonBox.RejectRole)
        btn_aceptar.setFont(QFont("Arial", 16))
        btn_cancelar.setFont(QFont("Arial", 16))
        btn_aceptar.setStyleSheet("padding: 3px;")
        btn_cancelar.setStyleSheet("padding: 3px;")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def get_descuento(self):
        return self.spin_descuento.value()


class Informes(QWidget):
    def __init__(self):
        super().__init__()

        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        # ------------------ CREAR EL QTabWidget ------------------
        self.tabs = QTabWidget()
        self.layout_principal.addWidget(self.tabs)

        # Aplicar estilos al QTabBar para aumentar el tamaño de la fuente, agregar padding y ajustar automáticamente
        self.tabs.tabBar().setStyleSheet("""
            QTabBar::tab {
                font-size: 14pt;                 /* Aumenta el tamaño de la fuente */
                padding: 10px 20px;              /* Agrega padding: arriba/abajo 10px, izquierda/derecha 20px */
                min-width: 150px;                 /* Establece un ancho mínimo para las pestañas */
                height: 40px;                     /* Establece una altura mínima para las pestañas */
            }
            QTabBar::tab:selected {
                background-color: #d3d3d3;        /* Color de fondo para la pestaña seleccionada */
                margin-bottom: -1px;              /* Evita el espacio entre pestañas */
            }
            QTabBar::tab:hover {
                background-color: #b0c4de;        /* Color de fondo al pasar el cursor */
            }
        """)

        # Asegurar que las pestañas se expandan para llenar el espacio disponible
        self.tabs.tabBar().setExpanding(True)

        # Pestaña de Vencimientos
        self.tab_vencimientos = QWidget()
        self.tabs.addTab(self.tab_vencimientos, "Vencimientos")
        self.init_tab_vencimientos()

    def init_tab_vencimientos(self):
        layout = QVBoxLayout()
        self.tab_vencimientos.setLayout(layout)

        # ------------------ LAYOUT PARA EL CHECKBOX ------------------
        filtro_layout = QHBoxLayout()

        # Checkbox para filtrar vencimientos de menos de 30 días
        self.checkbox_filtro = QCheckBox("Solo mostrar productos a menos de 30 días por vencerse")
        self.checkbox_filtro.setChecked(True)  # Habilitado por defecto
        self.checkbox_filtro.setFont(QFont("Arial", 14))
        self.checkbox_filtro.stateChanged.connect(self.load_informe_vencimientos)
        filtro_layout.addWidget(self.checkbox_filtro)

        # Spacer para alinear el checkbox a la izquierda
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)

        # ------------------ TABLA DE VENCIMIENTOS ------------------
        self.table_venc = QTableWidget()
        self.table_venc.setColumnCount(4)  # Descripción, Precio, Cantidad, Vencimiento
        self.table_venc.setHorizontalHeaderLabels(["Descripción", "Precio", "Cantidad", "Vencimiento"])
        self.table_venc.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_venc.verticalHeader().setVisible(False)
        self.table_venc.setFont(QFont("Arial", 14))  # Aumentado de 12 a 14
        self.table_venc.setRowCount(0)

        # Seleccionar filas completas, no celdas
        self.table_venc.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_venc.setSelectionMode(QTableWidget.SingleSelection)

        # Doble click para editar precio con descuento individual
        self.table_venc.itemDoubleClicked.connect(self.on_table_doubleclick)

        # Estilos para la selección y padding
        self.table_venc.setStyleSheet("""
            QTableWidget::item {
                padding: 2px; /* Añadido padding de 2px */
                font-size: 14px; /* Aumentado tamaño de fuente en 2px */
            }
            QTableWidget::item:selected {
                background-color: #b3ecff; /* Celeste claro */
                color: black;
                font: bold 14px; /* Negrita */
            }
            QHeaderView::section {
                background-color: #d3d3d3;
                font-weight: bold;
                border: 1px solid black;
                padding: 4px;
            }
        """)

        layout.addWidget(self.table_venc)

        # ------------------ BOTÓN PARA OFERTAR EN LOTE ------------------
        self.btn_ofertar_lote = QPushButton("Ofertar <30 Días")
        self.btn_ofertar_lote.setFont(QFont("Arial", 16))  # Aumentado tamaño de fuente
        self.btn_ofertar_lote.setEnabled(False)  # Se habilita solo tras cargar informe
        self.btn_ofertar_lote.clicked.connect(self.ofertar_lote_30_dias)
        layout.addWidget(self.btn_ofertar_lote)

        # Cargar el informe de vencimientos al iniciar
        self.load_informe_vencimientos()

    def load_informe_vencimientos(self):
        """Carga y ordena el inventario por fecha de vencimiento, colorea filas y muestra la tabla."""
        inventario = self.cargar_inventario()
        if not inventario:
            self.table_venc.setRowCount(0)
            self.btn_ofertar_lote.setEnabled(False)
            return

        # Habilitar botón de ofertar lote
        self.btn_ofertar_lote.setEnabled(True)

        # Determinar si se debe aplicar el filtro de <30 días
        aplicar_filtro = self.checkbox_filtro.isChecked()

        # Convertir (producto, fecha_dt), luego ordenar
        items_venc = []
        for p in inventario:
            fecha_str = p.get("fecha_vencimiento", "")
            fecha_dt = self.parse_fecha(fecha_str)
            items_venc.append((p, fecha_dt))

        # Filtrar productos según el checkbox
        hoy = datetime.now()
        if aplicar_filtro:
            items_venc = [
                (p, fecha_dt) for (p, fecha_dt) in items_venc
                if fecha_dt and (fecha_dt - hoy).days < 30
            ]

        # Separar con fecha y sin fecha
        con_fecha = [x for x in items_venc if x[1] is not None]
        sin_fecha = [x for x in items_venc if x[1] is None]
        con_fecha.sort(key=lambda x: x[1])  # Ordena de más próximo a más lejano
        ordenados = con_fecha + sin_fecha

        self.table_venc.setRowCount(len(ordenados))

        for row, (prod, fecha_dt) in enumerate(ordenados):
            # Descripción
            desc_item = QTableWidgetItem(prod["descripcion"].upper())
            desc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_venc.setItem(row, 0, desc_item)

            # Precio
            precio = float(prod.get("precio", 0.0))
            precio_item = QTableWidgetItem(f"{precio:.2f}")
            precio_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_venc.setItem(row, 1, precio_item)

            # Cantidad
            cant = str(prod.get("cantidad", 0))
            cant_item = QTableWidgetItem(cant)
            cant_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            cant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_venc.setItem(row, 2, cant_item)

            # Vencimiento
            venc_str = prod.get("fecha_vencimiento", "")
            venc_item = QTableWidgetItem(venc_str)
            venc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            venc_item.setTextAlignment(Qt.AlignCenter)
            self.table_venc.setItem(row, 3, venc_item)

            # Colorear la fila
            color_fila = "#ffffff"  # Predeterminado: blanco
            texto_fila = QColor("black")  # Texto predeterminado: negro
            if fecha_dt:
                color_fila, texto_fila = self.compute_row_color(fecha_dt)
            self.color_row(row, color_fila, texto_fila)

        # Mostrar la tabla
        self.table_venc.show()

    def ofertar_lote_30_dias(self):
        """
        Recorre la tabla, si faltan <30 días para vencerse, aplica un descuento porcentual al precio.
        El descuento se aplica directamente al precio sin almacenar un porcentaje de oferta.
        """
        inventario = self.cargar_inventario()
        if not inventario:
            return

        # Crear y mostrar el diálogo personalizado de ofertar en lote
        dialog = OfertarLoteDialog(self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            nuevo_descuento = dialog.get_descuento()
            if nuevo_descuento == 0:
                QMessageBox.information(
                    self, "Sin Descuento",
                    "No se aplicó ningún descuento ya que el valor ingresado es 0."
                )
                return

            # Recorremos la tabla
            rows_cambiados = []
            for row in range(self.table_venc.rowCount()):
                desc = self.table_venc.item(row, 0).text()
                venc_str = self.table_venc.item(row, 3).text()
                fecha_dt = self.parse_fecha(venc_str)
                if fecha_dt:
                    dias = (fecha_dt - datetime.now()).days
                    if dias < 30:
                        # Obtener el producto desde inventario
                        prod = next((p for p in inventario if p["descripcion"].upper() == desc), None)
                        if prod:
                            precio_original = float(prod.get("precio", 0.0))
                            # Aplicar descuento
                            precio_descuento = precio_original * (1 - nuevo_descuento / 100)
                            # Redondear hacia arriba al múltiplo de 50 o 100
                            precio_redondeado = self.round_up_price(precio_descuento)
                            # Actualizar en la tabla
                            self.table_venc.item(row, 1).setText(f"{precio_redondeado:.2f}")
                            rows_cambiados.append(desc)
                            # Actualizar el precio en inventario
                            prod["precio"] = precio_redondeado

            # Guardar cambios en el JSON
            if rows_cambiados:
                self.actualizar_descuento_lote(inventario, rows_cambiados, nuevo_descuento)
                QMessageBox.information(
                    self, "Descuentos en Lote",
                    f"Descuento de {nuevo_descuento}% aplicado a {len(rows_cambiados)} productos."
                )
                # Recargar el informe para reflejar los cambios
                self.load_informe_vencimientos()
            else:
                QMessageBox.information(
                    self, "Sin Cambios",
                    "No hay productos con menos de 30 días de vencimiento."
                )

    def actualizar_descuento_lote(self, inventario, descripciones, nuevo_descuento):
        """
        Aplica el nuevo descuento a todos los productos del inventario
        cuya descripción (en uppercase) esté en descripciones (también uppercase).
        """
        descripciones_upper = set(d.upper() for d in descripciones)

        for prod in inventario:
            if prod.get("descripcion", "").upper() in descripciones_upper:
                # Aplicar descuento y redondear
                precio_original = float(prod.get("precio", 0.0))
                precio_descuento = precio_original * (1 - nuevo_descuento / 100)
                precio_redondeado = self.round_up_price(precio_descuento)
                prod["precio"] = precio_redondeado

        try:
            with open("./db/inventario.json", "w", encoding="utf-8") as file:
                json.dump(inventario, file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar inventario: {e}")

    def on_table_doubleclick(self, item):
        """Permite editar el precio con un descuento individual."""
        row = item.row()
        col = item.column()
        if col not in [0, 1, 2, 3]:
            return  # Permitir doble clic en todas las columnas existentes

        desc = self.table_venc.item(row, 0).text()
        precio_actual_text = self.table_venc.item(row, 1).text()
        try:
            precio_actual = float(precio_actual_text)
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Precio inválido.")
            return

        # Crear y mostrar el diálogo personalizado de editar descuento
        dialog = EditarDescuentoDialog(desc, precio_actual, self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            nuevo_descuento = dialog.get_descuento()
            if nuevo_descuento == 0:
                QMessageBox.information(
                    self, "Sin Descuento",
                    "No se aplicó ningún descuento ya que el valor ingresado es 0."
                )
                return

            # Aplicar descuento
            precio_descuento = precio_actual * (1 - nuevo_descuento / 100)
            precio_redondeado = self.round_up_price(precio_descuento)

            # Obtener el inventario
            inventario = self.cargar_inventario()
            prod = next((p for p in inventario if p["descripcion"].upper() == desc), None)
            if not prod:
                QMessageBox.warning(self, "Aviso", "Producto no encontrado en inventario.")
                return

            # Actualizar en el inventario
            prod["precio"] = precio_redondeado

            # Actualizar en la tabla
            self.table_venc.item(row, 1).setText(f"{precio_redondeado:.2f}")

            # Guardar en JSON
            try:
                with open("./db/inventario.json", "w", encoding="utf-8") as file:
                    json.dump(inventario, file, indent=4)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar inventario: {e}")
                return

            QMessageBox.information(
                self, "Descuento Individual",
                f"Descuento de {nuevo_descuento}% aplicado a {desc}.\nNuevo precio: {precio_redondeado:.2f}."
            )
            # Recargar el informe para reflejar los cambios
            self.load_informe_vencimientos()

    def round_up_price(self, price):
        """
        Redondea el precio hacia arriba al múltiplo de 50 o 100 más cercano.
        Ejemplos:
            533 -> 550
            555 -> 600
            1000 -> 1000
        """
        remainder = price % 100
        if remainder == 0:
            return int(price)
        elif remainder < 50:
            return int(price - remainder + 50)
        else:
            return int(price - remainder + 100)

    def parse_fecha(self, fecha_str):
        """Intenta parsear con varios formatos. Retorna datetime o None."""
        if not fecha_str:
            return None
        formatos = ["%d-%m-%Y", "%Y-%m-%d"]
        for f in formatos:
            try:
                return datetime.strptime(fecha_str, f)
            except ValueError:
                pass
        return None

    def compute_row_color(self, fecha_dt):
        """Colorea la fila según días de diferencia con la fecha actual."""
        hoy = datetime.now()
        dias = (fecha_dt - hoy).days
        if dias < 0:
            # Vencido => negro con letras blancas
            return "#000000", QColor("white")
        elif dias < 30:
            return "#FFA07A", QColor("black")  # Naranja pastel
        elif dias < 60:
            return "#FFFACD", QColor("black")  # Amarillo pastel
        else:
            return "#98FB98", QColor("black")  # Verde pastel

    def color_row(self, row, color, texto_color):
        """Colorea toda la fila con 'color' y establece el color del texto."""
        for col in range(self.table_venc.columnCount()):
            item = self.table_venc.item(row, col)
            if item is not None:
                item.setBackground(QColor(color))
                item.setForeground(texto_color)

    def cargar_inventario(self):
        """Retorna la lista del inventario."""
        try:
            with open("./db/inventario.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.critical(self, "Error", "No se pudo cargar el inventario.")
            return []
