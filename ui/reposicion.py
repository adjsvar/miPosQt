# ui/reposicion.py

import json
from datetime import datetime
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDateEdit, QMessageBox, QCompleter, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import QRegExp


class Reposicion(QDialog):
    def __init__(self, parent=None, actualizar_tabla_callback=None):
        super().__init__(parent)
        self.actualizar_tabla_callback = actualizar_tabla_callback

        # Cargar inventario
        self.inventario = self.cargar_inventario()

        # Datos del producto seleccionado
        self.producto_actual = None
        self.cantidad_actual = 0
        self.costo_actual = 0.0
        self.precio_actual = 0.0
        self.venc_actual = ""

        # Lista para el autocompletado
        self.lista_completa = self.build_lista_completa()

        # Configurar ventana
        self.setWindowTitle("Reposición de Productos")
        self.setFixedSize(900, 500)
        self.setWindowModality(Qt.ApplicationModal)

        # Inicializar interfaz
        self.init_ui()

        # Índice para la navegación entre campos
        self.current_input_index = 0

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # ------------------ LABEL DEL PRODUCTO (FONDO AZUL) ------------------
        self.label_producto = QLabel("")
        self.label_producto.setFont(QFont("Arial", 16, QFont.Bold))
        # Permitir salto de línea (word wrap)
        self.label_producto.setWordWrap(True)
        self.label_producto.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 10px;
        """)
        self.label_producto.setAlignment(Qt.AlignCenter)
        # Aumentar algo la altura mínima para que no se corte el texto
        self.label_producto.setMinimumHeight(80)
        layout.addWidget(self.label_producto)

        # ------------------ LABEL DE ERROR (debajo del producto) ------------------
        self.label_error = QLabel("")
        self.label_error.setFont(QFont("Arial", 14))
        self.label_error.setWordWrap(True)
        self.label_error.setStyleSheet("")
        self.label_error.setAlignment(Qt.AlignCenter)
        # Dejarlo con un poco de altura para cuando aparezca
        self.label_error.setMinimumHeight(50)
        layout.addWidget(self.label_error)

        # ------------------ CAMPO DE BÚSQUEDA CON QCompleter ------------------
        self.search_line = QLineEdit()
        self.search_line.setFont(QFont("Arial", 16))
        self.search_line.setPlaceholderText("Código o descripción...")

        self.completer_model = QStringListModel(self.lista_completa, self)
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)  # subcadena
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.on_completer_activated)

        self.search_line.setCompleter(self.completer)
        layout.addWidget(self.search_line)

        # ------------------ CAMPOS: CANTIDAD, COSTO, PRECIO, FECHA -------------
        # Cantidad
        self.cantidad_line = QLineEdit()
        self.cantidad_line.setFont(QFont("Arial", 16))
        self.cantidad_line.setPlaceholderText("Cantidad a reponer (obligatoria, se suma)")
        self.cantidad_line.setValidator(QIntValidator(1, 999999999, self))
        layout.addWidget(self.cantidad_line)

        # Costo (opcional)
        self.costo_line = QLineEdit()
        self.costo_line.setFont(QFont("Arial", 16))
        self.costo_line.setPlaceholderText("Nuevo costo (opcional)")
        # Validar solo números con hasta 2 decimales
        reg_ex = QRegExp(r'^\d+(\.\d{0,2})?$')
        input_validator = QRegExpValidator(reg_ex, self.costo_line)
        self.costo_line.setValidator(input_validator)
        layout.addWidget(self.costo_line)

        # Precio (opcional)
        self.precio_line = QLineEdit()
        self.precio_line.setFont(QFont("Arial", 16))
        self.precio_line.setPlaceholderText("Nuevo precio (opcional)")
        # Validar solo números con hasta 2 decimales
        self.precio_line.setValidator(QRegExpValidator(reg_ex, self.precio_line))
        layout.addWidget(self.precio_line)

        # Fecha de Vencimiento (QLineEdit con validación)
        self.venc_line = QLineEdit()
        self.venc_line.setFont(QFont("Arial", 16))
        self.venc_line.setPlaceholderText("Fecha de vencimiento (dd-MM-yyyy) (opcional)")
        # Validar formato de fecha
        date_reg_ex = QRegExp(r'^(0[1-9]|[12]\d|3[01])[-](0[1-9]|1[0-2])[-]\d{4}$')
        date_validator = QRegExpValidator(date_reg_ex, self.venc_line)
        self.venc_line.setValidator(date_validator)
        layout.addWidget(self.venc_line)

        # ------------------ BOTONES: GUARDAR & CANCELAR ------------------
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFont(QFont("Arial", 16, QFont.Bold))
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        button_layout.addWidget(self.btn_guardar)

        # Botón "Cancelar" no se mueve con flechas/Enter
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFont(QFont("Arial", 16, QFont.Bold))
        self.btn_cancelar.clicked.connect(self.close)
        button_layout.addWidget(self.btn_cancelar)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Definir la lista de inputs (sin el botón "Cancelar" para que no se acceda con flechas/Enter)
        self.inputs = [
            self.search_line,
            self.cantidad_line,
            self.costo_line,
            self.precio_line,
            self.venc_line,
            self.btn_guardar
            # No incluimos self.btn_cancelar
        ]

        # Enfocar el primer campo
        self.inputs[0].setFocus()

    # ------------------ OVERRIDE KEY EVENTS  ------------------

    def keyPressEvent(self, event):
        """
        Moverse con flechas arriba/abajo y Enter entre self.inputs,
        ignorar el botón "Cancelar".
        ESC => cierra la ventana (no se incluye en la lista).
        """
        if event.key() == Qt.Key_Escape:
            # Cierra con Escape
            self.close()
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Down):
            self.current_input_index = (self.current_input_index + 1) % len(self.inputs)
            self.inputs[self.current_input_index].setFocus()
            return
        elif event.key() == Qt.Key_Up:
            self.current_input_index = (self.current_input_index - 1) % len(self.inputs)
            self.inputs[self.current_input_index].setFocus()
            return
        else:
            super().keyPressEvent(event)

    # ------------------ LÓGICA DE INVENTARIO ------------------

    def cargar_inventario(self):
        """Carga inventario desde el JSON."""
        try:
            with open("./db/inventario.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def build_lista_completa(self):
        """Lista 'CODIGO - DESCRIPCION' para QCompleter."""
        lista = []
        for p in self.inventario:
            texto = f"{p['codigo']} - {p['descripcion']}"
            lista.append(texto)
        return lista

    def on_completer_activated(self, text):
        """Al seleccionar un producto, se bloquea el search_line y se asigna el producto."""
        self.search_line.setText(text)
        self.search_line.setReadOnly(True)
        codigo = text.split(" - ")[0].strip()
        producto = next((p for p in self.inventario if p["codigo"] == codigo), None)
        if producto:
            self.asignar_producto(producto)
            # Pasar foco a cantidad
            idx_cant = self.inputs.index(self.cantidad_line)
            self.current_input_index = idx_cant
            self.cantidad_line.setFocus()
        else:
            self.limpiar_info()

    # ------------------ MOSTRAR / LIMPIAR INFO PRODUCTO ------------------

    def asignar_producto(self, producto):
        """
        Muestra la info del producto en label_producto,
        y setea en QLineEdit la fecha previa si existe.
        """
        self.limpiar_error()  # Limpiar mensaje de error si lo había

        self.producto_actual = producto
        self.cantidad_actual = producto.get("cantidad", 0)
        self.costo_actual = float(producto.get("costo", 0.0))
        self.precio_actual = float(producto.get("precio", 0.0))
        self.venc_actual = producto.get("fecha_vencimiento", "")

        # Nombre + desc en label_producto
        nombre_str = f"{producto['codigo']} - {producto['descripcion']}"
        self.label_producto.setText(nombre_str)

        # Cargar la fecha de vencimiento en el QLineEdit
        if self.venc_actual:
            # Si existe una fecha de vencimiento, mostrarla
            self.venc_line.setText(self.venc_actual)
        else:
            # Dejar el campo de fecha vacío
            self.venc_line.clear()

        # Limpiar inputs
        self.cantidad_line.clear()
        self.costo_line.clear()
        self.precio_line.clear()

    def limpiar_info(self):
        """Si no se encontró producto, limpiamos todo."""
        self.limpiar_error()
        self.producto_actual = None
        self.cantidad_actual = 0
        self.costo_actual = 0.0
        self.precio_actual = 0.0
        self.venc_actual = ""
        self.search_line.setReadOnly(False)
        self.label_producto.setText("")

    # ------------------ MENSAJES DE ERROR EN label_error ------------------

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en label_error con fondo rojo."""
        self.label_error.setStyleSheet("""
            background-color: #ffcccc;  /* rojo claro */
            color: red;
            font-size: 14px;
            padding: 5px;
        """)
        self.label_error.setText(mensaje)

    def limpiar_error(self):
        """Limpia el mensaje de error."""
        self.label_error.setStyleSheet("")
        self.label_error.clear()

    # ------------------ GUARDAR CAMBIOS ------------------

    def guardar_cambios(self):
        """
        Verifica que 'Cantidad' sea >0,
        suma la cantidad ingresada,
        actualiza costo/precio si se ingresan,
        actualiza fecha de vencimiento desde QLineEdit,
        setea fecha_ingreso a hoy.
        """
        self.limpiar_error()

        if not self.producto_actual:
            self.mostrar_error("No se ha seleccionado ningún producto.")
            self.search_line.setFocus()
            return

        # Cantidad obligatoria
        cant_txt = self.cantidad_line.text().strip()
        if not cant_txt.isdigit() or int(cant_txt) <= 0:
            self.mostrar_error("El campo 'Cantidad' es obligatorio (entero > 0).")
            self.cantidad_line.setFocus()
            return

        cant_reponer = int(cant_txt)
        cant_final = self.cantidad_actual + cant_reponer

        # Costo
        cost_txt = self.costo_line.text().strip()
        if cost_txt:
            try:
                nuevo_costo = float(cost_txt)
                if nuevo_costo < 0:
                    raise ValueError("El costo no puede ser negativo.")
            except ValueError as e:
                self.mostrar_error(f"El costo debe ser numérico y positivo.\n{e}")
                self.costo_line.setFocus()
                return
        else:
            nuevo_costo = self.costo_actual

        # Precio
        prec_txt = self.precio_line.text().strip()
        if prec_txt:
            try:
                nuevo_precio = float(prec_txt)
                if nuevo_precio < 0:
                    raise ValueError("El precio no puede ser negativo.")
            except ValueError as e:
                self.mostrar_error(f"El precio debe ser numérico y positivo.\n{e}")
                self.precio_line.setFocus()
                return
        else:
            nuevo_precio = self.precio_actual

        # Fecha de vencimiento
        nueva_venc = self.venc_line.text().strip()
        if nueva_venc:
            # Validar formato de fecha
            try:
                datetime.strptime(nueva_venc, "%d-%m-%Y")
            except ValueError:
                self.mostrar_error("La fecha de vencimiento debe tener el formato dd-MM-yyyy.")
                self.venc_line.setFocus()
                return

        # Actualizar inventario
        codigo = self.producto_actual["codigo"]
        for p in self.inventario:
            if p["codigo"] == codigo:
                p["cantidad"] = cant_final
                p["costo"] = nuevo_costo
                p["precio"] = nuevo_precio
                p["fecha_vencimiento"] = nueva_venc  # Puede ser vacío si no se ingresó
                p["fecha_ingreso"] = datetime.now().strftime("%d-%m-%Y")
                break

        # Guardar en JSON
        self.guardar_inventario()

        if self.actualizar_tabla_callback:
            self.actualizar_tabla_callback()

        QMessageBox.information(self, "Éxito", "Reposición realizada con éxito.")

        # Reset
        self.search_line.clear()
        self.search_line.setReadOnly(False)
        self.cantidad_line.clear()
        self.costo_line.clear()
        self.precio_line.clear()
        self.venc_line.clear()
        self.limpiar_info()

        # Foco al primer input
        self.current_input_index = 0
        self.inputs[0].setFocus()

    def guardar_inventario(self):
        """Guarda el inventario en inventario.json."""
        try:
            with open("./db/inventario.json", "w", encoding="utf-8") as file:
                json.dump(self.inventario, file, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar inventario: {e}")

