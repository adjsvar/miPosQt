# ui/inventario.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QPushButton,
    QHeaderView, QMenu, QAction, QTableWidgetItem, QMessageBox, QFormLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate
import json
from datetime import datetime

from .editar import Editar
from .inventario_manual import InventarioManual
from .reposicion import Reposicion
from .inventario_automatico import InventarioAutomatico  # Importación agregada


class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, value, is_float=False):
        super().__init__(str(value))
        self.is_float = is_float
        try:
            self.numeric_value = float(value) if is_float else int(value)
        except ValueError:
            self.numeric_value = 0.0 if is_float else 0

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        return super().__lt__(other)


class DateTableWidgetItem(QTableWidgetItem):
    def __init__(self, date_str):
        super().__init__(date_str)
        try:
            self.date_value = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            try:
                self.date_value = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                self.date_value = None

    def __lt__(self, other):
        if isinstance(other, DateTableWidgetItem):
            if self.date_value is None:
                return False
            if other.date_value is None:
                return True
            return self.date_value < other.date_value
        return super().__lt__(other)


class Inventario(QWidget):
    def __init__(self):
        super().__init__()
        self.inventario_data = []
        self.init_ui()
        self.setFocusPolicy(Qt.StrongFocus)
        self.ventana_inventario_automatico = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Layout superior: botones + búsqueda
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        layout.addLayout(top_layout)

        self.btn_agregar = self.crear_boton("Agregar Producto", "#2ecc71", self.abrir_formulario_agregar)
        self.btn_manual = self.crear_boton("Inventario Manual", "#3498db", self.abrir_inventario_manual)
        self.btn_reposicion = self.crear_boton("Reposición", "#f39c12", self.abrir_reposicion)
        self.btn_inventario_automatico = self.crear_boton("Inventario Automático", "#9b59b6", self.abrir_inventario_automatico)

        top_layout.addWidget(self.btn_agregar)
        top_layout.addWidget(self.btn_manual)
        top_layout.addWidget(self.btn_reposicion)
        top_layout.addWidget(self.btn_inventario_automatico)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setFont(QFont("Arial", 14))
        self.search_input.setPlaceholderText("Buscar por código o descripción...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setFixedWidth(300)
        top_layout.addWidget(self.search_input)
        top_layout.addStretch()

        # Crear tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Número de columnas
        self.table.setHorizontalHeaderLabels([
            "Código", "Descripción", "Cantidad", "Precio", "Fecha de Vencimiento"
        ])
        self.table.setFont(QFont("Arial", 14))

        header_font = QFont("Arial", 16, QFont.Bold)
        self.table.horizontalHeader().setFont(header_font)

        # Modo interactivo para fijar anchos
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)        # Código
        header.setSectionResizeMode(1, QHeaderView.Stretch)      # Descripción
        header.setSectionResizeMode(2, QHeaderView.Fixed)        # Cantidad
        header.setSectionResizeMode(3, QHeaderView.Fixed)        # Precio
        header.setSectionResizeMode(4, QHeaderView.Fixed)        # Fecha de Vencimiento

        # Establecer anchos fijos
        self.table.setColumnWidth(0, 120)  # Código
        self.table.setColumnWidth(2, 100)  # Cantidad
        self.table.setColumnWidth(3, 100)  # Precio
        self.table.setColumnWidth(4, 250)  # Fecha de Vencimiento

        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("QTableWidget::item { padding: 10px; }")
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)

        self.table.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.table)

        # Menú contextual + doble clic
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemDoubleClicked.connect(self.on_double_click_item)

        # Cargar datos
        self.load_data()

    def crear_boton(self, texto, color, funcion):
        boton = QPushButton(texto)
        boton.setFont(QFont("Arial", 14))
        boton.setFixedHeight(50)
        boton.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {self.oscurecer_color(color, 0.9)};
            }}
        """)
        boton.clicked.connect(funcion)
        return boton

    def oscurecer_color(self, color, factor):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened_rgb = tuple(max(0, min(255, int(c * factor))) for c in rgb)
        return f"#{darkened_rgb[0]:02x}{darkened_rgb[1]:02x}{darkened_rgb[2]:02x}"

    def load_data(self):
        """
        Carga los datos desde inventario.json a self.inventario_data y actualiza la tabla.
        """
        self.inventario_data = self.cargar_inventario()
        self.populate_table()
        self.focus_on_entry()

    def on_search_text_changed(self, text):
        """
        Actualiza la tabla en tiempo real según el texto de búsqueda.
        """
        self.populate_table(filter_str=text)

    def populate_table(self, filter_str=""):
        """
        Popula la tabla con los datos filtrados o completos.
        """
        self.table.setSortingEnabled(False)

        filtro_l = filter_str.strip().lower()
        if filtro_l:
            data_filtrada = []
            for p in self.inventario_data:
                cod_l = p["codigo"].lower()
                desc_l = p["descripcion"].lower()
                if filtro_l in cod_l or filtro_l in desc_l:
                    data_filtrada.append(p)
        else:
            data_filtrada = self.inventario_data[:]

        self.table.setRowCount(len(data_filtrada))

        for row, producto in enumerate(data_filtrada):
            # Código
            codigo = producto["codigo"]
            codigo_item = QTableWidgetItem(codigo)
            codigo_item.setTextAlignment(Qt.AlignCenter)
            # Almacenar 'codigo' en Qt.UserRole para referencia futura
            codigo_item.setData(Qt.UserRole, codigo)
            self.table.setItem(row, 0, codigo_item)

            # Descripción
            desc_item = QTableWidgetItem(producto["descripcion"])
            desc_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            # Verificar si el producto es pesable para aplicar negrita
            if producto.get("es_pesable", False):
                font = desc_item.font()
                font.setBold(True)
                desc_item.setFont(font)
            self.table.setItem(row, 1, desc_item)

            # Cantidad (Siempre entero)
            cantidad_valor = producto["cantidad"]
            cant_str = str(int(cantidad_valor))
            cant_item = NumericTableWidgetItem(cant_str, is_float=False)
            cant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, cant_item)

            # Precio
            precio_valor = float(producto["precio"])  # Convertir a float
            precio_item = NumericTableWidgetItem(precio_valor, is_float=True)  # Indicar que es float

            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, precio_item)

            # Fecha de Vencimiento
            fecha_venc = DateTableWidgetItem(producto.get("fecha_vencimiento", ""))
            fecha_venc.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, fecha_venc)

            # Debug: Mostrar los valores de cada producto
            print(f"[DEBUG] Producto en fila {row}: {producto}")  # Debug

        self.table.setSortingEnabled(True)

    def cargar_inventario(self):
        """
        Carga el inventario desde el archivo JSON.
        """
        try:
            with open("./db/inventario.json", "r", encoding="utf-8") as file:
                inv = json.load(file)
            for p in inv:
                # Manejar 'cantidad' como int siempre
                p['cantidad'] = int(p.get('cantidad', 0))
                # 'costo' puede ser None
                p['costo'] = float(p['costo']) if 'costo' in p and p['costo'] is not None else None
                p['precio'] = float(p.get('precio', 0))  # Convertir siempre a float
            return inv
        except FileNotFoundError:
            # Si el archivo no existe, retorna una lista vacía
            return []
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Error al decodificar JSON: {e}")
            return []
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error en los datos del inventario: {e}")
            return []

    def show_context_menu(self, pos):
        """
        Muestra el menú contextual al hacer clic derecho en una fila.
        """
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        menu = QMenu(self)
        editar_action = QAction("Editar Producto", self)
        borrar_action = QAction("Eliminar Producto", self)

        editar_action.triggered.connect(lambda: self.editar_producto(row))
        borrar_action.triggered.connect(lambda: self.eliminar_producto(row))

        menu.addAction(editar_action)
        menu.addAction(borrar_action)

        menu.exec_(self.table.mapToGlobal(pos))

    def on_double_click_item(self, item):
        """
        Maneja el doble clic en un ítem para editar el producto.
        """
        row = item.row()
        self.editar_producto(row)

    def editar_producto(self, row):
        """
        Abre el diálogo de edición para el producto seleccionado.
        """
        # Obtener el 'codigo' del producto en la fila seleccionada
        codigo_item = self.table.item(row, 0)
        if not codigo_item:
            QMessageBox.warning(self, "Advertencia", "No se pudo obtener el código del producto.")
            return
        codigo = codigo_item.text()

        # Buscar el producto en self.inventario_data por 'codigo'
        producto = next((p for p in self.inventario_data if p["codigo"] == codigo), None)
        if not producto:
            QMessageBox.warning(self, "Advertencia", f"No se encontró el producto con código '{codigo}'.")
            return

        # Abrir el diálogo de edición con el producto encontrado
        dialog = Editar(
            parent=self,
            modo="editar",
            producto=producto,
            guardar_callback=self.guardar_producto_callback
        )
        dialog.exec_()

    def eliminar_producto(self, row):
        """
        Elimina el producto seleccionado del inventario.
        """
        # Obtener el 'codigo' del producto en la fila seleccionada
        codigo_item = self.table.item(row, 0)
        if not codigo_item:
            QMessageBox.warning(self, "Advertencia", "No se pudo obtener el código del producto.")
            return
        codigo = codigo_item.text()

        resp = QMessageBox.question(
            self,
            "Eliminar Producto",
            f"¿Está seguro de eliminar el producto con código '{codigo}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        # Buscar el índice del producto en self.inventario_data por 'codigo'
        index_to_delete = next((i for i, p in enumerate(self.inventario_data) if p["codigo"] == codigo), None)
        if index_to_delete is None:
            QMessageBox.warning(self, "Advertencia", f"No se encontró el producto con código '{codigo}'.")
            return

        # Eliminar el producto de self.inventario_data
        del self.inventario_data[index_to_delete]

        # Guardar en JSON
        self.guardar_producto_en_json()

        # Actualizar la tabla
        self.populate_table()

    def guardar_producto_en_json(self):
        """
        Guarda los datos del inventario en el archivo JSON.
        """
        try:
            with open("./db/inventario.json", "w", encoding="utf-8") as file:
                # Convertir 'cantidad' a int siempre y manejar 'costo' como opcional
                inv_to_save = []
                for p in self.inventario_data:
                    p_save = p.copy()
                    p_save['cantidad'] = int(p_save['cantidad'])
                    p_save['precio'] = float(p_save['precio'])  # Asegurarse de que sea float
                    # Manejar 'costo': si es None, omitirlo
                    if p_save.get('costo') is not None:
                        p_save['costo'] = float(p_save['costo'])
                    else:
                        p_save.pop('costo', None)  # Eliminar si no existe
                    inv_to_save.append(p_save)
                    print(f"[DEBUG] Guardando Producto: {p_save}")  # Debug

                json.dump(inv_to_save, file, indent=4, ensure_ascii=False)
                print(f"[DEBUG] Inventario guardado exitosamente en 'inventario.json'")  # Debug
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el inventario: {e}")

    def guardar_producto_callback(self, producto, modo):
        """
        Callback para guardar un producto (agregar o editar) en self.inventario_data y sincronizar con JSON.

        :param producto: Diccionario con los datos del producto.
        :param modo: "agregar" o "editar".
        """
        if modo == "agregar":
            # Verificar si el código ya existe
            for p in self.inventario_data:
                if p["codigo"].lower() == producto["codigo"].lower():
                    QMessageBox.warning(self, "Advertencia", f"El código '{producto['codigo']}' ya existe.")
                    return
            self.inventario_data.append(producto)
        elif modo == "editar":
            # Buscar y actualizar el producto
            for i, p in enumerate(self.inventario_data):
                if p["codigo"].lower() == producto["codigo"].lower():
                    self.inventario_data[i] = producto
                    break
            else:
                QMessageBox.warning(self, "Advertencia", "No se encontró el producto para editar.")
                return

        # Guardar los cambios en el JSON
        self.guardar_producto_en_json()

        # Actualizar la tabla
        self.populate_table()

    # -------- Métodos para abrir los formularios externos --------
    def abrir_formulario_agregar(self):
        """
        Abre el diálogo para agregar un nuevo producto.
        """
        dialog = Editar(
            parent=self,
            modo="agregar",
            producto=None,
            guardar_callback=self.guardar_producto_callback
        )
        dialog.exec_()

    def abrir_inventario_manual(self):
        """
        Abre el diálogo de inventario manual.
        """
        dialog = InventarioManual(parent=self, actualizar_tabla_callback=self.load_data)
        dialog.exec_()

    def abrir_reposicion(self):
        """
        Abre el diálogo de reposición de inventario.
        """
        dialog = Reposicion(parent=self, actualizar_tabla_callback=self.load_data)
        dialog.exec_()

    def abrir_inventario_automatico(self):
        """
        Abre la ventana de Inventario Automático.
        """
        if self.ventana_inventario_automatico is None or not self.ventana_inventario_automatico.isVisible():
            self.ventana_inventario_automatico = InventarioAutomatico(parent=self, actualizar_tabla_callback=self.load_data)
            self.ventana_inventario_automatico.show()
        else:
            # Si ya está abierta, traerla al frente
            self.ventana_inventario_automatico.raise_()
            self.ventana_inventario_automatico.activateWindow()

    # --------- NAVEGACIÓN CON FLECHAS ENTRE SEARCH_INPUT Y LA TABLA -----------
    def keyPressEvent(self, event):
        """
        Sobrescribe eventos de teclado para mover foco entre search_input y la tabla.
        """
        if hasattr(self, 'search_input') and self.search_input.hasFocus():
            # Si estamos en el input y se presiona Down o Tab
            if event.key() in (Qt.Key_Down, Qt.Key_Tab):
                if self.table.rowCount() > 0:
                    self.table.setFocus()
                    self.table.setCurrentCell(0, 0)
            else:
                super().keyPressEvent(event)
        elif self.table.hasFocus():
            current_row = self.table.currentRow()
            if event.key() == Qt.Key_Up and current_row == 0:
                # Regresar foco a search
                self.table.clearSelection()
                self.focus_on_entry()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def focus_on_entry(self):
        """
        Establece el foco en el campo de búsqueda.
        """
        self.search_input.setFocus()
