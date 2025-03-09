# ui/editar.py

from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QCheckBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QDateEdit, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta
import json

class Editar(QDialog):
    def __init__(self, parent=None, modo="agregar", producto=None, guardar_callback=None):
        """
        Inicializa el diálogo de edición/agregado de productos.

        :param parent: Widget padre.
        :param modo: "agregar" o "editar".
        :param producto: Diccionario con los datos del producto a editar. Requerido si modo es "editar".
        :param guardar_callback: Función de callback a ejecutar después de guardar. Debe aceptar (producto, modo).
        """
        super().__init__(parent)
        self.parent = parent
        self.modo = modo
        self.producto = producto or {}
        self.guardar_callback = guardar_callback

        self.inputs = []
        self.current_input_index = 0

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Editar Producto" if self.modo == "editar" else "Agregar Producto")
        self.setFixedSize(600, 600)
        self.setWindowModality(Qt.ApplicationModal)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # Título
        titulo = QLabel("Editar Producto" if self.modo == "editar" else "Agregar Producto")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Formulario
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        main_layout.addLayout(form_layout)

        campos = [
            ("Código", "codigo"),
            ("Descripción", "descripcion"),
            ("¿Es Pesable?", "es_pesable"),
            ("Cantidad", "cantidad"),  # Etiqueta dinámica
            ("Costo", "costo"),
            ("Precio", "precio"),
            ("Fecha de Ingreso", "fecha_ingreso"),
            ("Fecha de Vencimiento", "fecha_vencimiento"),
        ]
        self.entries = {}
        self.labels = {}

        # Valor inicial de 'es_pesable'
        es_pesable_inicial = bool(self.producto.get("es_pesable", False)) if self.modo == "editar" else False

        for i, (label_text, key) in enumerate(campos):
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 16))
            form_layout.addWidget(label, i, 0)
            self.labels[key] = label

            if key == "es_pesable":
                checkbox = QCheckBox()
                checkbox.setChecked(es_pesable_inicial)
                form_layout.addWidget(checkbox, i, 1)
                self.entries[key] = checkbox
                self.inputs.append(checkbox)

                checkbox.stateChanged.connect(self.toggle_cantidad_label)
            elif "fecha" in key:
                date_edit = QDateEdit()
                date_edit.setDisplayFormat("dd-MM-yyyy")
                date_edit.setCalendarPopup(True)
                date_edit.setFont(QFont("Arial", 16))

                if self.modo == "editar":
                    fecha_valor_str = self.producto.get(key, "")
                else:
                    fecha_valor_str = ""

                fecha_valor = self.normalizar_fecha(fecha_valor_str)
                if fecha_valor:
                    date_edit.setDate(QDate(fecha_valor.year, fecha_valor.month, fecha_valor.day))
                else:
                    if self.modo == "agregar":
                        if key == "fecha_vencimiento":
                            hoy = datetime.now()
                            dentro_10 = hoy + timedelta(days=365 * 10)
                            date_edit.setDate(QDate(dentro_10.year, dentro_10.month, dentro_10.day))
                        else:
                            date_edit.setDate(QDate.currentDate())
                            if key == "fecha_ingreso":
                                date_edit.setEnabled(False)
                    elif self.modo == "editar":
                        # Si en modo editar no hay fecha, establecer la fecha actual
                        date_edit.setDate(QDate.currentDate())

                form_layout.addWidget(date_edit, i, 1)
                self.entries[key] = date_edit
                self.inputs.append(date_edit)
            elif key == "cantidad":
                cantidad_valor = self.producto.get(key, "") if self.modo == "editar" else ""

                # Crear QLineEdit en lugar de QDoubleSpinBox
                line_edit = QLineEdit()
                line_edit.setFont(QFont("Arial", 16))
                line_edit.setPlaceholderText("Ingrese la cantidad")

                # Configurar el validador según 'es_pesable_inicial' permitiendo negativos
                if es_pesable_inicial:
                    validator = QDoubleValidator(-1000000.0, 1000000.0, 2)
                else:
                    validator = QIntValidator(-1000000, 1000000)
                line_edit.setValidator(validator)

                if self.modo == "editar":
                    if cantidad_valor != "":
                        line_edit.setText(str(cantidad_valor))
                else:
                    # En modo agregar, dejar el campo en blanco
                    line_edit.clear()

                form_layout.addWidget(line_edit, i, 1)
                self.entries[key] = line_edit
                self.inputs.append(line_edit)

            elif key == "costo":
                costo_valor = self.producto.get(key, "") if self.modo == "editar" else ""

                # Crear QLineEdit para 'costo' con QDoubleValidator
                costo_edit = QLineEdit()
                costo_edit.setFont(QFont("Arial", 16))
                costo_edit.setPlaceholderText("Ingrese el costo")
                costo_edit.setValidator(QDoubleValidator(-1000000.0, 1000000.0, 2))  # Permitir negativos si es necesario

                if self.modo == "editar":
                    if costo_valor != "" and costo_valor is not None:
                        costo_edit.setText(str(costo_valor))
                    else:
                        costo_edit.clear()
                else:
                    # En modo agregar, dejar el campo en blanco
                    costo_edit.clear()

                form_layout.addWidget(costo_edit, i, 1)
                self.entries[key] = costo_edit
                self.inputs.append(costo_edit)
            elif key == "precio":
                precio_valor = self.producto.get(key, "") if self.modo == "editar" else ""

                # Crear QLineEdit para 'precio' con QDoubleValidator
                precio_edit = QLineEdit()
                precio_edit.setFont(QFont("Arial", 16))
                precio_edit.setPlaceholderText("Ingrese el precio")
                precio_edit.setValidator(QDoubleValidator(0.0, 1000000.0, 2))  # Solo valores positivos

                if self.modo == "editar":
                    if precio_valor != "" and precio_valor is not None:
                        precio_edit.setText(str(precio_valor))
                    else:
                        precio_edit.clear()
                else:
                    # En modo agregar, dejar el campo en blanco
                    precio_edit.clear()

                form_layout.addWidget(precio_edit, i, 1)
                self.entries[key] = precio_edit
                self.inputs.append(precio_edit)
            else:
                entry = QLineEdit()
                entry.setFont(QFont("Arial", 16))
                entry.setPlaceholderText(f"Ingrese {label_text.lower()}")
                valor_inicial = str(self.producto.get(key, "")) if self.modo == "editar" else ""

                if key == "codigo" and self.modo == "editar":
                    entry.setReadOnly(True)

                if self.modo == "editar" and self.producto.get(key) is not None:
                    entry.setText(str(self.producto.get(key, "")))
                else:
                    entry.clear()

                form_layout.addWidget(entry, i, 1)
                self.entries[key] = entry
                self.inputs.append(entry)

                if key == "codigo" and self.modo == "agregar":
                    # Conectar solo el evento returnPressed para verificar el código al presionar Enter
                    entry.returnPressed.connect(self.verificar_codigo_live)

        # Mensaje de estado
        self.message_label = QLabel(" ")
        self.message_label.setFixedHeight(40)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 16px; padding: 5px;")
        self.layout().addWidget(self.message_label)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(20)
        self.layout().addLayout(botones_layout)

        botones_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFont(QFont("Arial", 16, QFont.Bold))
        self.btn_guardar.setFixedSize(140, 50)
        self.btn_guardar.clicked.connect(self.guardar_producto)
        botones_layout.addWidget(self.btn_guardar)
        self.inputs.append(self.btn_guardar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFont(QFont("Arial", 16, QFont.Bold))
        self.btn_cancelar.setFixedSize(140, 50)
        self.btn_cancelar.clicked.connect(self.close)
        botones_layout.addWidget(self.btn_cancelar)

        botones_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        if self.inputs:
            self.inputs[0].setFocus()

        # Ajustar la etiqueta y el placeholder de 'cantidad' según 'es_pesable_inicial' sin limpiar el campo
        self.toggle_cantidad_label(es_pesable_inicial, initial=True)

        if self.modo == "agregar":
            self.btn_guardar.setEnabled(False)

    def toggle_cantidad_label(self, estado, initial=False):
        """
        Actualiza la etiqueta y el placeholder del campo 'cantidad' según 'es_pesable'.
        Además, actualiza el validador para permitir float o int.
        Maneja tanto booleanos como enteros provenientes del estado del checkbox.
        """
        # Determinar si el estado es pesable
        if isinstance(estado, int):
            es_pesable = estado == Qt.Checked
        elif isinstance(estado, bool):
            es_pesable = estado
        else:
            es_pesable = False

        if es_pesable:
            self.labels["cantidad"].setText("Cantidad (g)")
            self.entries["cantidad"].setToolTip("Ingrese la cantidad en gramos")
            # Configurar QLineEdit para permitir decimales y negativos
            validator = QDoubleValidator(-1000000.0, 1000000.0, 2)
            self.entries["cantidad"].setValidator(validator)
            self.entries["cantidad"].setPlaceholderText("Ingrese la cantidad en gramos")
        else:
            self.labels["cantidad"].setText("Cantidad (und)")
            self.entries["cantidad"].setToolTip("Ingrese la cantidad en unidades")
            # Configurar QLineEdit para solo permitir enteros y negativos
            validator = QIntValidator(-1000000, 1000000)
            self.entries["cantidad"].setValidator(validator)
            self.entries["cantidad"].setPlaceholderText("Ingrese la cantidad en unidades")

        if not initial:
            # Limpiar el campo 'cantidad' para evitar inconsistencias solo si no es la carga inicial
            self.entries["cantidad"].clear()

    def verificar_codigo_live(self):
        """
        Verifica si el código ingresado ya existe en el inventario.
        Esta verificación se realiza solo al presionar Enter en el campo 'codigo'.
        """
        if self.modo != "agregar":
            return

        codigo = self.entries["codigo"].text().strip().lower()

        if not codigo:
            self.mostrar_mensaje("El campo 'Código' no puede estar vacío.", "error", self.entries["codigo"])
            return

        inventario = self.parent.inventario_data  # Acceder al inventario_data del padre

        for producto in inventario:
            if producto["codigo"].lower() == codigo:
                self.mostrar_mensaje("Ya existe un producto con ese CÓDIGO.", "error", self.entries["codigo"])
                return

        # Si el código es único, limpiar el mensaje de error
        self.message_label.clear()
        self.message_label.setStyleSheet("")
        # Habilitar el botón de guardar si los otros campos obligatorios están llenos
        self.validar_campos_para_guardar()

    def validar_campos_para_guardar(self):
        """
        Habilita el botón de guardar si los campos obligatorios están llenos y el código es único.
        """
        codigo = self.entries["codigo"].text().strip()
        descripcion = self.entries["descripcion"].text().strip()
        cantidad = self.entries["cantidad"].text().strip()
        precio = self.entries["precio"].text().strip()

        if codigo and descripcion and cantidad and precio:
            self.btn_guardar.setEnabled(True)
        else:
            self.btn_guardar.setEnabled(False)

    def keyPressEvent(self, event):
        """
        Maneja la navegación con teclas entre los campos del formulario.
        """
        if event.key() in (Qt.Key_Down, Qt.Key_Up, Qt.Key_Return, Qt.Key_Enter):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.current_input_index = (self.current_input_index + 1) % len(self.inputs)
            elif event.key() == Qt.Key_Down:
                self.current_input_index = (self.current_input_index + 1) % len(self.inputs)
            elif event.key() == Qt.Key_Up:
                self.current_input_index = (self.current_input_index - 1) % len(self.inputs)

            self.inputs[self.current_input_index].setFocus()
        else:
            super().keyPressEvent(event)

    def cargar_inventario(self):
        """
        Carga el inventario desde el archivo JSON.
        """
        try:
            with open("./db/inventario.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def normalizar_fecha(self, fecha_str):
        """
        Normaliza una cadena de fecha a un objeto datetime.

        :param fecha_str: Cadena de fecha en formatos reconocidos.
        :return: Objeto datetime o None si no se puede parsear.
        """
        formatos = ["%d-%m-%Y", "%Y-%m-%d"]
        for f in formatos:
            try:
                return datetime.strptime(fecha_str, f)
            except ValueError:
                pass
        return None

    def mostrar_mensaje(self, mensaje, tipo="error", campo=None):
        """
        Muestra un mensaje de estado en el diálogo.

        :param mensaje: Texto del mensaje.
        :param tipo: Tipo de mensaje ("error", "success", etc.).
        :param campo: Campo al que enfocar en caso de error.
        """
        if tipo == "error":
            self.message_label.setStyleSheet(
                "background-color: #ffcccc; color: red; font-size: 16px; padding: 5px;"
            )
        elif tipo == "success":
            self.message_label.setStyleSheet(
                "background-color: #ccffcc; color: green; font-size: 16px; padding: 5px;"
            )
        else:
            self.message_label.setStyleSheet(
                "background-color: #f0f0f0; color: black; font-size: 16px; padding: 5px;"
            )
        self.message_label.setText(mensaje)
        if campo:
            campo.setFocus()

    def guardar_producto(self):
        """
        Recoge los datos del formulario, valida y envía el producto para ser guardado.
        """
        self.message_label.clear()
        self.message_label.setStyleSheet("")

        datos = {}
        for key, widget in self.entries.items():
            if isinstance(widget, QCheckBox):
                datos[key] = widget.isChecked()
            elif isinstance(widget, QDateEdit):
                datos[key] = widget.date().toString("dd-MM-yyyy")
            elif isinstance(widget, QLineEdit):
                if key == "cantidad":
                    cantidad_text = widget.text().strip()
                    datos[key] = cantidad_text
                elif key == "costo":
                    costo_text = widget.text().strip()
                    datos[key] = costo_text
                elif key == "precio":
                    precio_text = widget.text().strip()
                    datos[key] = precio_text
                else:
                    val = widget.text().strip()
                    if key == "descripcion":
                        val = val.upper()
                    datos[key] = val
            else:
                val = widget.text().strip()
                datos[key] = val

        # Validar campos obligatorios
        obligatorios = ["codigo", "descripcion", "cantidad", "precio"]
        for campo in obligatorios:
            if not datos[campo]:
                self.mostrar_mensaje(f"El campo '{campo.capitalize()}' es obligatorio.", "error", self.entries[campo])
                return

        cod_nuevo = datos["codigo"].lower()
        desc_nuevo = datos["descripcion"].upper()

        # Validar unicidad de código y descripción si es agregar
        if self.modo == "agregar":
            inventario = self.parent.inventario_data
            for prod in inventario:
                if prod["codigo"].lower() == cod_nuevo:
                    self.mostrar_mensaje("Ya existe un producto con ese CÓDIGO.", "error", self.entries["codigo"])
                    return
                if prod["descripcion"].upper() == desc_nuevo:
                    self.mostrar_mensaje("Ya existe un producto con esa DESCRIPCIÓN.", "error", self.entries["descripcion"])
                    return

        es_pesable = datos.get("es_pesable", False)
        try:
            # Procesar "cantidad"
            if es_pesable:
                # Permitir float para productos pesables
                if datos["cantidad"]:
                    cantidad = float(datos["cantidad"])
                else:
                    cantidad = 0.0
                datos["cantidad"] = cantidad
            else:
                # Permitir int para productos no pesables
                cantidad = int(datos["cantidad"])  # Cambiado a int
                datos["cantidad"] = cantidad

            # Procesar "costo" (opcional)
            if datos["costo"]:
                datos["costo"] = float(datos["costo"])
                # Si deseas permitir que 'costo' sea negativo, elimina o comenta la siguiente línea
                # if datos["costo"] < 0:
                #     raise ValueError("El 'Costo' no puede ser negativo.")
            else:
                datos["costo"] = None  # Dejar en blanco si no se ingresa

            # Procesar "precio"
            if datos["precio"]:
                try:
                    datos["precio"] = float(datos["precio"])  # Convertir a float explícitamente
                except ValueError:
                    self.mostrar_mensaje("El 'Precio' debe ser un número válido.", "error", self.entries["precio"])
                    return
                if datos["precio"] < 0:
                    self.mostrar_mensaje("El 'Precio' no puede ser negativo.", "error", self.entries["precio"])
                    return
            else:
                datos["precio"] = 0.0  # Asignar valor predeterminado


        except ValueError as ve:
            self.mostrar_mensaje(str(ve), "error")
            # Enfocar el campo correspondiente según el error
            if "Precio" in str(ve):
                self.entries["precio"].setFocus()
            elif "Costo" in str(ve):
                self.entries["costo"].setFocus()
            elif "Cantidad" in str(ve):
                self.entries["cantidad"].setFocus()
            return

        # Si es editar, asegurarse de que el código no cambie
        if self.modo == "editar":
            datos["codigo"] = self.producto["codigo"]

        # Enviar los datos al callback para ser guardados en el inventario principal
        if self.guardar_callback:
            self.guardar_callback(datos, self.modo)
            if self.modo == "editar":
                self.mostrar_mensaje("Producto guardado con éxito.", "success")
                self.close()
            else:
                self.mostrar_mensaje("Producto guardado con éxito. Agregue otro.", "success")
                # Resetear los campos para agregar otro producto
                self.reset_form()

    def reset_form(self):
        """
        Resetea los campos del formulario para agregar un nuevo producto.
        """
        for key, widget in self.entries.items():
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QDateEdit):
                if key == "fecha_vencimiento":
                    hoy = datetime.now()
                    dentro_10 = hoy + timedelta(days=365 * 10)
                    widget.setDate(QDate(dentro_10.year, dentro_10.month, dentro_10.day))
                else:
                    widget.setDate(QDate.currentDate())
                    if key == "fecha_ingreso":
                        widget.setEnabled(False)
            elif isinstance(widget, QLineEdit):
                if key == "cantidad":
                    es_pesable = self.entries["es_pesable"].isChecked()
                    widget.clear()
                    # Actualizar el validador y placeholder según 'es_pesable'
                    if es_pesable:
                        validator = QDoubleValidator(-1000000.0, 1000000.0, 2)
                        widget.setValidator(validator)
                        widget.setPlaceholderText("Ingrese la cantidad en gramos")
                    else:
                        validator = QIntValidator(-1000000, 1000000)
                        widget.setValidator(validator)
                        widget.setPlaceholderText("Ingrese la cantidad en unidades")
                elif key == "costo":
                    widget.clear()
                    widget.setValidator(QDoubleValidator(-1000000.0, 1000000.0, 2))
                    widget.setPlaceholderText("Ingrese el costo")
                elif key == "precio":
                    widget.clear()
                    widget.setValidator(QDoubleValidator(0.0, 1000000.0, 2))  # Solo valores positivos
                    widget.setPlaceholderText("Ingrese el precio")
                elif key in ["codigo", "descripcion"]:
                    widget.clear()
            else:
                if key in ["codigo", "descripcion", "costo", "precio"]:
                    widget.clear()

        self.current_input_index = 0
        if self.inputs:
            self.inputs[0].setFocus()

    def keyPressEvent(self, event):
        """
        Maneja la navegación con teclas entre los campos del formulario.
        """
        if event.key() in (Qt.Key_Down, Qt.Key_Up, Qt.Key_Return, Qt.Key_Enter):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.current_input_index = (self.current_input_index + 1) % len(self.inputs)
            elif event.key() == Qt.Key_Down:
                self.current_input_index = (self.current_input_index + 1) % len(self.inputs)
            elif event.key() == Qt.Key_Up:
                self.current_input_index = (self.current_input_index - 1) % len(self.inputs)

            self.inputs[self.current_input_index].setFocus()
        else:
            super().keyPressEvent(event)
