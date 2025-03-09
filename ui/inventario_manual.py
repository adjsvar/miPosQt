# ui/inventario_manual.py

import json
from datetime import datetime, timedelta  # Importación correcta de datetime
from PyQt5.QtCore import Qt, QStringListModel, QDate
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QSpacerItem, QSizePolicy, QCompleter, QDateEdit
)


class InventarioManual(QDialog):
    def __init__(self, parent=None, actualizar_tabla_callback=None):
        super().__init__(parent)
        self.actualizar_tabla_callback = actualizar_tabla_callback

        # Ajustar el tamaño a 700x500 para acomodar nuevos campos
        self.setFixedSize(700, 500)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Inventario Manual")

        self.inventario = self.cargar_inventario()
        self.producto_actual = None
        self.cantidad_original = 0
        self.costo_original = 0.0
        self.precio_original = 0.0

        # Crea la lista "CÓDIGO - DESCRIPCIÓN" para el QCompleter
        self.lista_completa = self.build_lista_completa()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # ---------- Parte Superior con Fondo Azul ----------
        top_layout = QVBoxLayout()
        top_layout.setSpacing(10)

        self.label_producto = QLabel("Producto Seleccionado: Ninguno")
        self.label_producto.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_producto.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        self.label_producto.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.label_producto)

        self.label_cantidad_actual = QLabel("Cantidad Actual: 0 | Costo Actual: 0.0 | Precio Actual: 0.0")
        self.label_cantidad_actual.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_cantidad_actual.setStyleSheet("""
            background-color: #2980b9;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        self.label_cantidad_actual.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.label_cantidad_actual)

        main_layout.addLayout(top_layout)

        # ---------- Grid Layout para Etiquetas e Inputs ----------
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        main_layout.addLayout(form_layout)

        # Campo de Búsqueda
        label_busqueda = QLabel("Buscar Producto:")
        label_busqueda.setFont(QFont("Arial", 14))
        form_layout.addWidget(label_busqueda, 0, 0, alignment=Qt.AlignRight)

        self.search_line = QLineEdit()
        self.search_line.setFont(QFont("Arial", 14))
        self.search_line.setPlaceholderText("Código o descripción...")
        form_layout.addWidget(self.search_line, 0, 1)

        # Configuración de QCompleter
        self.completer_model = QStringListModel(self.lista_completa, self)
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)  # Permite búsqueda por subcadena
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.on_completer_activated)

        self.search_line.setCompleter(self.completer)
        self.search_line.returnPressed.connect(self.buscar_producto)

        # Campo de Cantidad
        label_cantidad = QLabel("Cantidad:")
        label_cantidad.setFont(QFont("Arial", 14))
        form_layout.addWidget(label_cantidad, 1, 0, alignment=Qt.AlignRight)

        self.quantity_line = QLineEdit()
        self.quantity_line.setFont(QFont("Arial", 14))
        self.quantity_line.setPlaceholderText("Cantidad a establecer...")
        self.quantity_line.setValidator(QIntValidator(0, 999999999, self))
        form_layout.addWidget(self.quantity_line, 1, 1)

        # Campo de Costo
        label_costo = QLabel("Costo:")
        label_costo.setFont(QFont("Arial", 14))
        form_layout.addWidget(label_costo, 2, 0, alignment=Qt.AlignRight)

        self.costo_edit = QLineEdit()
        self.costo_edit.setFont(QFont("Arial", 14))
        self.costo_edit.setPlaceholderText("Costo (Opcional)")
        self.costo_edit.setValidator(QDoubleValidator(0.0, 999999999.99, 2, self))
        form_layout.addWidget(self.costo_edit, 2, 1)

        # Campo de Precio
        label_precio = QLabel("Precio:")
        label_precio.setFont(QFont("Arial", 14))
        form_layout.addWidget(label_precio, 3, 0, alignment=Qt.AlignRight)

        self.precio_edit = QLineEdit()
        self.precio_edit.setFont(QFont("Arial", 14))
        self.precio_edit.setPlaceholderText("Precio (Opcional)")
        self.precio_edit.setValidator(QDoubleValidator(0.0, 999999999.99, 2, self))
        form_layout.addWidget(self.precio_edit, 3, 1)

        # Campo de Fecha de Vencimiento
        label_fecha_vencimiento = QLabel("Fecha de Vencimiento:")
        label_fecha_vencimiento.setFont(QFont("Arial", 14))
        form_layout.addWidget(label_fecha_vencimiento, 4, 0, alignment=Qt.AlignRight)

        self.fecha_vencimiento_edit = QDateEdit()
        self.fecha_vencimiento_edit.setDisplayFormat("dd-MM-yyyy")
        self.fecha_vencimiento_edit.setCalendarPopup(True)
        self.fecha_vencimiento_edit.setFont(QFont("Arial", 14))
        self.fecha_vencimiento_edit.setToolTip("Fecha de Vencimiento (Opcional)")
        form_layout.addWidget(self.fecha_vencimiento_edit, 4, 1)

        # ---------- Mensajes ----------
        self.message_label = QLabel(" ")
        self.message_label.setFixedHeight(40)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 16px; padding: 5px;")
        main_layout.addWidget(self.message_label)

        # ---------- Botones Guardar/Cancelar ----------
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        main_layout.addLayout(button_layout)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_guardar.setFixedSize(120, 40)
        self.btn_guardar.clicked.connect(self.guardar_cantidad)
        button_layout.addWidget(self.btn_guardar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_cancelar.setFixedSize(120, 40)
        self.btn_cancelar.clicked.connect(self.cancelar_operacion)
        button_layout.addWidget(self.btn_cancelar)

        button_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # ---------- Lista de Inputs para Navegación ----------
        self.inputs = [
            self.search_line,
            self.quantity_line,
            self.costo_edit,
            self.precio_edit,
            self.fecha_vencimiento_edit,
            self.btn_guardar
            # Se excluye self.btn_cancelar para evitar activar guardado al presionar Enter
        ]
        if self.inputs:
            self.inputs[0].setFocus()

    # ---------- LÓGICA DE INVENTARIO / COMPLETER ----------

    def cargar_inventario(self):
        """Carga el inventario desde inventario.json."""
        try:
            with open("./db/inventario.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def build_lista_completa(self):
        """Construye la lista "CÓDIGO - DESCRIPCIÓN" para todas las entradas del inventario."""
        lista = []
        for p in self.inventario:
            texto = f"{p['codigo']} - {p['descripcion']}"
            lista.append(texto)
        return lista

    # Cuando se selecciona algo en el QCompleter
    def on_completer_activated(self, text):
        # "Contra-escritura": Bloqueamos el campo con ese texto
        self.search_line.setText(text)
        self.search_line.setReadOnly(True)
        # Localizar el producto real
        codigo = text.split(" - ")[0].strip()
        producto = next((p for p in self.inventario if p["codigo"] == codigo), None)
        if producto:
            self.asignar_producto(producto)
            # Enfocar el campo de cantidad
            self.quantity_line.setFocus()
        else:
            self.limpiar_info_producto()

    # Al presionar Enter en search_line sin haber elegido sugerencia
    # si quieres forzar la primera sugerencia, hazlo aquí
    def buscar_producto(self):
        texto = self.search_line.text().strip()
        if not texto:
            self.limpiar_info_producto()
            self.search_line.setReadOnly(False)
            return
        # No hacemos nada adicional, la búsqueda la gestiona QCompleter
        pass

    # ---------- LÓGICA DE ASIGNAR PRODUCTO Y GUARDAR ----------

    def asignar_producto(self, producto):
        """Configura la interfaz para un producto seleccionado."""
        self.producto_actual = producto
        self.cantidad_original = producto.get("cantidad", 0)
        self.costo_original = producto.get("costo", 0.0)
        self.precio_original = producto.get("precio", 0.0)
        nombre_str = f"{producto['codigo']} - {producto['descripcion']}"
        cant_str = f"Cantidad Actual: {self.cantidad_original} | Costo Actual: {self.costo_original} | Precio Actual: {self.precio_original}"
        self.label_producto.setText(nombre_str)
        self.label_cantidad_actual.setText(cant_str)

        # Poblamos solo el campo de fecha de vencimiento con el valor actual
        fecha_vencimiento = producto.get("fecha_vencimiento", "")
        if fecha_vencimiento:
            fecha = self.normalizar_fecha(fecha_vencimiento)
            if fecha:
                self.fecha_vencimiento_edit.setDate(QDate(fecha.year, fecha.month, fecha.day))
            else:
                self.fecha_vencimiento_edit.setDate(QDate.currentDate())
        else:
            self.fecha_vencimiento_edit.setDate(QDate.currentDate())

        # Dejar los demás campos en blanco
        self.quantity_line.clear()
        self.costo_edit.clear()
        self.precio_edit.clear()

    def limpiar_info_producto(self):
        """Limpia los labels y la variable producto_actual."""
        self.label_producto.setText("Producto Seleccionado: Ninguno")
        self.label_cantidad_actual.setText("Cantidad Actual: 0 | Costo Actual: 0.0 | Precio Actual: 0.0")
        self.producto_actual = None
        self.cantidad_original = 0
        self.costo_original = 0.0
        self.precio_original = 0.0

        # Limpiamos los campos opcionales
        self.fecha_vencimiento_edit.setDate(QDate.currentDate())
        self.quantity_line.clear()
        self.costo_edit.clear()
        self.precio_edit.clear()

    def guardar_cantidad(self):
        """Establece la nueva cantidad y guarda en inventario.json."""
        if not self.producto_actual:
            QMessageBox.warning(self, "Advertencia", "No se ha seleccionado ningún producto.")
            return

        cantidad_text = self.quantity_line.text().strip()
        if cantidad_text == "":
            nueva_cantidad = self.cantidad_original
        else:
            try:
                nueva_cantidad = int(cantidad_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "La cantidad debe ser un número entero.")
                self.quantity_line.setFocus()
                return

        # Obtener valores opcionales
        fecha_vencimiento_text = self.fecha_vencimiento_edit.date().toString("dd-MM-yyyy")
        costo_text = self.costo_edit.text().strip()
        precio_text = self.precio_edit.text().strip()

        # Validar y parsear campos opcionales
        nueva_fecha_vencimiento = self.producto_actual.get("fecha_vencimiento", "")
        nuevo_costo = self.costo_original
        nuevo_precio = self.precio_original

        # Fecha de Vencimiento es opcional
        if fecha_vencimiento_text:
            fecha = self.normalizar_fecha(fecha_vencimiento_text)
            if fecha:
                nueva_fecha_vencimiento = fecha_vencimiento_text

        # Costo es opcional
        if costo_text:
            try:
                nuevo_costo = float(costo_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "El costo debe ser un número válido.")
                self.costo_edit.setFocus()
                return

        # Precio es opcional
        if precio_text:
            try:
                nuevo_precio = float(precio_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "El precio debe ser un número válido.")
                self.precio_edit.setFocus()
                return

        # Actualizar en el inventario
        for p in self.inventario:
            if p["codigo"] == self.producto_actual["codigo"]:
                p["cantidad"] = nueva_cantidad
                p["fecha_vencimiento"] = nueva_fecha_vencimiento
                p["costo"] = nuevo_costo
                p["precio"] = nuevo_precio
                break

        # Guardar JSON
        try:
            with open("./db/inventario.json", "w", encoding="utf-8") as file:
                json.dump(self.inventario, file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la información: {e}")
            return

        QMessageBox.information(self, "Hecho", "Información actualizada con éxito.")

        if self.actualizar_tabla_callback:
            self.actualizar_tabla_callback()

        # Reset para nueva búsqueda
        self.producto_actual = None
        self.cantidad_original = 0
        self.costo_original = 0.0
        self.precio_original = 0.0
        self.search_line.setText("")
        self.search_line.setReadOnly(False)
        self.quantity_line.clear()
        self.fecha_vencimiento_edit.setDate(QDate.currentDate())
        self.costo_edit.clear()
        self.precio_edit.clear()
        self.limpiar_info_producto()
        self.search_line.setFocus()

    def cancelar_operacion(self):
        """Cierra el formulario."""
        self.close()

    # ---------- FUNCIONES AUXILIARES ----------

    def normalizar_fecha(self, fecha_str):
        """Convierte una cadena de fecha a un objeto datetime."""
        formatos = ["%d-%m-%Y", "%Y-%m-%d"]
        for f in formatos:
            try:
                return datetime.strptime(fecha_str, f)
            except ValueError:
                pass
        return None

    # ---------- NAVEGACIÓN CON TECLAS ----------

    def keyPressEvent(self, event):
        """Maneja la navegación con teclas de flecha y Enter."""
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            # Obtener el índice actual del foco
            current_widget = self.focusWidget()
            try:
                current_index = self.inputs.index(current_widget)
                # Si no es el último widget, mover al siguiente
                if current_index < len(self.inputs) - 1:
                    self.inputs[current_index + 1].setFocus()
                else:
                    # Si es el último widget (Guardar), activar guardar
                    self.guardar_cantidad()
            except ValueError:
                pass
        elif key == Qt.Key_Down:
            self.move_focus(1)
        elif key == Qt.Key_Up:
            self.move_focus(-1)
        else:
            super().keyPressEvent(event)

    def move_focus(self, direction):
        """Mueve el foco hacia arriba o abajo en la lista de inputs."""
        current_widget = self.focusWidget()
        try:
            current_index = self.inputs.index(current_widget)
            new_index = (current_index + direction) % len(self.inputs)
            self.inputs[new_index].setFocus()
        except ValueError:
            pass
