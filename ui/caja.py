# ui/caja.py

import json
import os
import difflib
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit,
    QLabel, QHeaderView, QMessageBox, QDialog, QMenu, QAction
)
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from .facturar import FacturarDialog
from .registro_operacion import RegistrarOperacionDialog  # Asegúrate de tener este diálogo


class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        self.clear()
        super().focusInEvent(event)


class Caja(QWidget):
    inventario_actualizado = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.inventario = []
        self.ticket_numero = "N/A"
        self.current_user = "cajero_1"
        self.num_session = "N/A"  # Inicializar num_session
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        input_layout = QHBoxLayout()

        self.search_input = CustomLineEdit(self)
        self.search_input.setFont(QFont("Arial", 28))
        self.search_input.setPlaceholderText("ESCRIBE CÓDIGO O DESCRIPCIÓN...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d3d3d3;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #d6eaf8;
            }
        """)
        input_layout.addWidget(self.search_input, stretch=3)

        self.ticket_label = QLabel("Ticket N°: N/A")
        self.ticket_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.ticket_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.ticket_label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.ticket_label, stretch=1)

        layout.addLayout(input_layout)

        self.message_label = QLabel(" ")
        self.message_label.setFont(QFont("Arial", 34, QFont.Bold))
        self.message_label.setStyleSheet("""
            background-color: transparent;
            color: black;
            border-radius: 5px;
            padding: 5px;
        """)
        self.message_label.setAlignment(Qt.AlignLeft)
        self.message_label.setFixedHeight(44)
        layout.addWidget(self.message_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad", "Precio", "Subtotal"])
        self.table.setFont(QFont("Arial", 12))
        self.table.setRowCount(0)

        self.table.horizontalHeader().setFont(QFont("Arial", 14, QFont.Bold))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #b3d9ff;
                color: black;
            }
            QHeaderView::section {
                background-color: #d3d3d3;
                font-weight: bold;
                border: 1px solid black;
                padding: 4px;
                font-size: 15px;
            }
        """)

        layout.addWidget(self.table)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.total_label = QLabel("TOTAL: 0.00")
        self.total_label.setFont(QFont("Arial", 58, QFont.Bold))
        self.total_label.setStyleSheet("""
            QLabel {
                background-color: #f9e79f;
                color: black;
                border: 2px solid #d3d3d3;
                border-radius: 5px;
            }
        """)
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setFixedHeight(90)
        layout.addWidget(self.total_label)

        self.cargar_inventario()
        self.cargar_sesion()
        self.determinar_numero_ticket()

        self.search_input.returnPressed.connect(self.buscar_producto)
        self.table.cellChanged.connect(self.validar_cambio_celda)

        self.actualizar_total()

    def show_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        menu = QMenu(self)
        eliminar_action = QAction("Eliminar Item", self)
        eliminar_action.triggered.connect(lambda: self.eliminar_item(row))
        menu.addAction(eliminar_action)
        menu.exec_(self.table.mapToGlobal(pos))

    def eliminar_item(self, row):
        if row < 0 or row >= self.table.rowCount():
            return
        desc = self.table.item(row, 1).text()
        r = QMessageBox.question(
            self,
            "Eliminar",
            f"¿Desea eliminar '{desc}' del ticket?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if r == QMessageBox.Yes:
            self.table.removeRow(row)
            self.actualizar_total()
            self.mostrar_mensaje("PRODUCTO ELIMINADO.", "success")
            self.search_input.setFocus()

    def cargar_sesion(self):
        ruta_sesion = "./db/session.json"
        try:
            with open(ruta_sesion, "r", encoding='utf-8') as file:
                sesion = json.load(file)
                if sesion.get("logged_in"):
                    self.current_user = sesion.get("current_user", "cajero_1")
                    self.num_session = sesion.get("num_session", "N/A")  # Añadido
                else:
                    self.current_user = "cajero_1"
                    self.num_session = "N/A"  # Añadido
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_user = "cajero_1"
            self.num_session = "N/A"  # Añadido

    def cargar_inventario(self):
        try:
            with open("./db/inventario.json", "r", encoding='utf-8') as file:
                self.inventario = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.inventario = []
            self.mostrar_mensaje("ERROR AL CARGAR INVENTARIO.", "error")

    def determinar_numero_ticket(self):
        hoy = datetime.now().strftime("%d-%m-%Y")
        ruta_tickets = "./db/tickets.json"

        if not os.path.exists(ruta_tickets):
            registro_tickets = []
            with open(ruta_tickets, "w", encoding='utf-8') as file:
                json.dump(registro_tickets, file, indent=4)
        else:
            try:
                with open(ruta_tickets, "r", encoding='utf-8') as file:
                    registro_tickets = json.load(file)
            except (json.JSONDecodeError, FileNotFoundError):
                registro_tickets = []

        tickets_hoy = [t for t in registro_tickets if t.get("dia") == hoy]

        if not tickets_hoy:
            nuevo_num = 1
        else:
            ultimo_ticket = tickets_hoy[-1]
            ultimo_num_str = ultimo_ticket.get("numero_ticket", "").split("-")[-1]
            try:
                ultimo_num = int(ultimo_num_str)
                nuevo_num = ultimo_num + 1
            except ValueError:
                nuevo_num = 1

        self.ticket_numero = f"{hoy}-{nuevo_num}"
        self.ticket_label.setText(f"Ticket N°: {self.ticket_numero}")

    def buscar_producto(self):
        texto = self.search_input.text().strip().lower()
        self.search_input.clear()
        if not texto:
            return

        # Dividir el texto de búsqueda en tokens
        tokens = texto.split()

        # Manejar formatos especiales como subtotal y cantidad
        try:
            if "+" in texto:
                subtotal_str, identificador = texto.split("+", 1)
                subtotal = float(subtotal_str.strip())
                identificador = identificador.strip()
                cantidad = None
            elif "*" in texto:
                cantidad_str, identificador = texto.split("*", 1)
                cantidad = float(cantidad_str.strip())
                identificador = identificador.strip()
                subtotal = None
            else:
                cantidad = 1
                subtotal = None
                identificador = texto.strip()
        except ValueError:
            self.mostrar_mensaje("FORMATO INVÁLIDO.", "error")
            return

        # Primero, buscar si identificador coincide exactamente con algún código
        producto_exacto = next((p for p in self.inventario if p["codigo"].lower() == identificador.lower()), None)
        if producto_exacto:
            if subtotal is not None:
                if producto_exacto.get("es_pesable", False):
                    cantidad = int((subtotal / producto_exacto["precio"]) * 1000)  # Convertir Kg a g
                else:
                    self.mostrar_mensaje("NO SE PUEDE SUBTOTAL EN PRODUCTOS NO PESABLES.", "error")
                    return
            if (cantidad is not None
                and not producto_exacto.get("es_pesable", False)
                and not float(cantidad).is_integer()):
                self.mostrar_mensaje("CANTIDAD INVÁLIDA (DECIMAL) PARA NO PESABLE.", "error")
                return
            self.agregar_producto_a_tabla(producto_exacto, cantidad)
            return

        # Si no hay coincidencia exacta, proceder con la búsqueda aproximada
        # Actualizar tokens si hay identificador separado
        if '+' in texto or '*' in texto:
            tokens = identificador.split()

        # Buscar productos que coincidan con todos los tokens
        productos_matches = []
        for producto in self.inventario:
            # Combinar código y descripción en una sola cadena
            descripcion = f"{producto.get('codigo', '')} {producto.get('descripcion', '')}".lower()
            descripcion_tokens = descripcion.split()

            # Verificar si cada token de búsqueda tiene una coincidencia aproximada en los tokens de la descripción
            all_tokens_match = True
            for token in tokens:
                # Obtener coincidencias aproximadas para el token
                matches = difflib.get_close_matches(token, descripcion_tokens, n=1, cutoff=0.8)
                if not matches:
                    all_tokens_match = False
                    break
            if all_tokens_match:
                productos_matches.append(producto)

        if len(productos_matches) == 1:
            producto = productos_matches[0]
            if subtotal is not None:
                if producto.get("es_pesable", False):
                    cantidad = int((subtotal / producto["precio"]) * 1000)  # Convertir Kg a g
                else:
                    self.mostrar_mensaje("NO SE PUEDE SUBTOTAL EN PRODUCTOS NO PESABLES.", "error")
                    return
            if (cantidad is not None
                and not producto.get("es_pesable", False)
                and not float(cantidad).is_integer()):
                self.mostrar_mensaje("CANTIDAD INVÁLIDA (DECIMAL) PARA NO PESABLE.", "error")
                return
            self.agregar_producto_a_tabla(producto, cantidad)
        elif len(productos_matches) == 0:
            self.mostrar_mensaje("PRODUCTO NO ENCONTRADO.", "error")
        else:
            self.mostrar_mensaje("MÚLTIPLES COINCIDENCIAS, SE MÁS ESPECÍFICO.", "error")

    def agregar_producto_a_tabla(self, producto, cantidad):
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)

        # Código
        cod_item = QTableWidgetItem(producto["codigo"])
        cod_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row_pos, 0, cod_item)

        # Descripción
        desc_item = QTableWidgetItem(producto["descripcion"].upper())
        desc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row_pos, 1, desc_item)

        # Oferta y Precio
        oferta = float(producto.get("oferta", 0))
        precio_original = float(producto["precio"])
        if oferta > 0:
            precio = precio_original * (1 - oferta / 100)
        else:
            precio = precio_original

        # Cantidad
        if producto.get("es_pesable", False):
            cant_item = QTableWidgetItem(f"{int(cantidad)} g")
            cant_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            # Validar que la cantidad sea positiva
            cant_item.setData(Qt.UserRole, "g")
        else:
            cant_item = QTableWidgetItem(f"{int(cantidad)} und")
            cant_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            # Validar que la cantidad sea positiva
            cant_item.setData(Qt.UserRole, "und")
        self.table.setItem(row_pos, 2, cant_item)

        # Precio
        pre_item = QTableWidgetItem(f"{precio:.2f}")
        pre_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row_pos, 3, pre_item)

        # Subtotal
        if producto.get("es_pesable", False):
            subtotal = (cantidad / 1000) * precio  # Convertir g a Kg para el subtotal
        else:
            subtotal = cantidad * precio
        sub_item = QTableWidgetItem(f"{subtotal:.2f}")
        sub_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
        self.table.setItem(row_pos, 4, sub_item)

        self.mostrar_mensaje(
            f"AGREGADO: {producto['descripcion'].upper()} ({cantidad} g)" 
            if producto.get("es_pesable", False) 
            else f"AGREGADO: {producto['descripcion'].upper()} ({cantidad} und)", 
            "success"
        )
        self.actualizar_total()

    def mostrar_mensaje(self, mensaje, tipo):
        if tipo == "success":
            self.message_label.setStyleSheet("""
                background-color: #27ae60;
                color: white;
                font-size: 34px;
                border-radius: 5px;
                padding: 5px;
            """)
        elif tipo == "error":
            self.message_label.setStyleSheet("""
                background-color: #e74c3c;
                color: white;
                font-size: 34px;
                border-radius: 5px;
                padding: 5px;
            """)
        else:
            self.message_label.setStyleSheet("""
                background-color: #3498db;
                color: white;
                font-size: 34px;
                border-radius: 5px;
                padding: 5px;
            """)
        self.message_label.setText(mensaje.upper())

    def keyPressEvent(self, event):
        key = event.key()
        if self.search_input.hasFocus():
            if key == Qt.Key_F5:
                self.abrir_ingresos()
            elif key == Qt.Key_F6:
                self.abrir_gastos()
            elif key == Qt.Key_F10:
                self.abrir_facturacion()
            elif key in (Qt.Key_Down, Qt.Key_Tab):
                if self.table.rowCount() > 0:
                    self.table.setFocus()
                    self.table.setCurrentCell(0, 0)
            else:
                super().keyPressEvent(event)
        elif self.table.hasFocus():
            if key == Qt.Key_F5:
                self.abrir_ingresos()
            elif key == Qt.Key_F6:
                self.abrir_gastos()
            elif key == Qt.Key_F10:
                self.abrir_facturacion()
            elif key == Qt.Key_Up and self.table.currentRow() == 0:
                self.table.clearSelection()
                self.search_input.setFocus()
            elif key == Qt.Key_Delete:
                current_row = self.table.currentRow()
                if current_row >= 0:
                    self.eliminar_item(current_row)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def abrir_facturacion(self):
        total = 0.0
        for row in range(self.table.rowCount()):
            sub_text = self.table.item(row, 4).text()
            try:
                subtotal = float(sub_text)
                total += subtotal
            except ValueError:
                pass
        if total == 0:
            QMessageBox.warning(self, "Error", "No hay productos en el ticket para facturar.")
            return

        dialog = FacturarDialog(total, self)
        if dialog.exec_() == QDialog.Accepted:
            pagos, cambio = dialog.get_pago_data()
            self.guardar_ticket(pagos, cambio)

    def abrir_ingresos(self):
        dialog = RegistrarOperacionDialog(tipo_operacion="ingreso", parent=self)
        if dialog.exec_() == QDialog.Accepted:
            ingreso = dialog.get_operacion_data()
            self.registrar_operacion(ingreso)

    def abrir_gastos(self):
        dialog = RegistrarOperacionDialog(tipo_operacion="gasto", parent=self)
        if dialog.exec_() == QDialog.Accepted:
            gasto = dialog.get_operacion_data()
            self.registrar_operacion(gasto)

    def registrar_operacion(self, operacion):
        """Registra la operación utilizando el nuevo formato."""
        tipo = operacion.get("tipo")
        cuenta = operacion.get("cuenta", "efectivo")  # Nuevo campo de cuenta
        monto = operacion.get("monto")
        nota = operacion.get("nota", "")

        ruta_op = "./db/registro_operaciones.json"
        try:
            if os.path.exists(ruta_op):
                with open(ruta_op, "r", encoding="utf-8") as f:
                    registros = json.load(f)
            else:
                registros = []
        except (json.JSONDecodeError, IOError):
            registros = []

        nueva_operacion = {
            "num_session": self.num_session,
            "tipo": tipo,
            "cuenta": cuenta,  # Agregado el campo cuenta
            "monto": monto,
            "nota": nota,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        registros.append(nueva_operacion)

        try:
            with open(ruta_op, "w", encoding="utf-8") as f:
                json.dump(registros, f, indent=4, ensure_ascii=False)
            self.mostrar_mensaje(f"OPERACIÓN DE {tipo.upper()} REGISTRADA EN {cuenta.upper()}.", "success")
        except IOError:
            self.mostrar_mensaje("ERROR AL REGISTRAR OPERACIÓN.", "error")

    def validar_cambio_celda(self, row, column):
        if column not in (2, 4):
            return
        try:
            cant_item = self.table.item(row, 2)
            precio_item = self.table.item(row, 3)
            sub_item = self.table.item(row, 4)

            cant_text = cant_item.text().replace(" g", "").replace(" und", "").strip()
            unidad = cant_item.data(Qt.UserRole)
            cantidad = int(cant_text)

            precio = float(precio_item.text())
            subtotal = float(sub_item.text()) if sub_item.text() else 0.0

            if cantidad <= 0 and column == 2:
                raise ValueError("Cantidad inválida.")
            if subtotal <= 0 and column == 4:
                raise ValueError("Subtotal inválido.")

            codigo = self.table.item(row, 0).text()
            producto = next((p for p in self.inventario if p["codigo"] == codigo), None)

            if producto:
                oferta = float(producto.get("oferta", 0))
                precio_original = float(producto["precio"])
                if oferta > 0:
                    precio_calculado = precio_original * (1 - oferta / 100)
                else:
                    precio_calculado = precio_original

                if producto.get("es_pesable", False):
                    if unidad == "g":
                        # Convertir gramos a kilogramos para el subtotal
                        calculated_sub = (cantidad / 1000) * precio_calculado
                        sub_item.setText(f"{calculated_sub:.2f}")
                    else:
                        raise ValueError("Unidad inconsistente para producto pesable.")
                else:
                    if unidad == "und":
                        calculated_sub = cantidad * precio_calculado
                        sub_item.setText(f"{calculated_sub:.2f}")
                    else:
                        raise ValueError("Unidad inconsistente para producto no pesable.")
            else:
                raise ValueError("Producto no encontrado.")

            self.actualizar_total()

        except (ValueError, AttributeError):
            self.mostrar_mensaje("VALOR INVÁLIDO, REVISE CAMPOS.", "error")

    def actualizar_total(self):
        total = 0.0
        for row in range(self.table.rowCount()):
            try:
                sub = float(self.table.item(row, 4).text())
                total += sub
            except ValueError:
                pass
        self.total_label.setText(f"TOTAL: {total:.2f}")

    def guardar_ticket(self, pagos, cambio):
        if self.ticket_numero == "N/A":
            self.mostrar_mensaje("TICKET NO DETERMINADO.", "error")
            return
        if self.table.rowCount() == 0:
            self.mostrar_mensaje("NO HAY PRODUCTOS.", "error")
            return

        try:
            with open("./db/session.json", "r", encoding='utf-8') as file:
                session_data = json.load(file)
                num_sess = session_data.get("num_session", "N/A")
        except (FileNotFoundError, json.JSONDecodeError):
            num_sess = "N/A"

        productos = []
        for row in range(self.table.rowCount()):
            codigo = self.table.item(row, 0).text()
            desc = self.table.item(row, 1).text()
            c_text = self.table.item(row, 2).text().replace(" g", "").replace(" und", "").strip()
            unidad = self.table.item(row, 2).data(Qt.UserRole)
            if unidad == "g":
                c_val = int(c_text)
            else:
                c_val = int(c_text)
            pr_unit = float(self.table.item(row, 3).text())
            sub = float(self.table.item(row, 4).text())

            productos.append({
                "codigo": codigo,
                "descripcion": desc,
                "cantidad": c_val,
                "precio_unitario": pr_unit,
                "subtotal": sub
            })

        monto = sum(p["subtotal"] for p in productos)

        reg_ticket = {
            "dia": datetime.now().strftime("%d-%m-%Y"),
            "cajero": self.current_user,
            "articulos": productos,
            "monto": monto,
            "numero_ticket": self.ticket_numero,
            "pagos": pagos,
            "cambio": cambio,
            "num_session": num_sess  # Usar num_session de session.json
        }

        ruta_tickets = "./db/tickets.json"
        if not os.path.exists(ruta_tickets):
            reg_t = []
        else:
            try:
                with open(ruta_tickets, "r", encoding='utf-8') as file:
                    reg_t = json.load(file)
            except (json.JSONDecodeError, FileNotFoundError):
                reg_t = []

        reg_t.append(reg_ticket)

        try:
            with open(ruta_tickets, "w", encoding='utf-8') as file:
                json.dump(reg_t, file, indent=4)
            self.mostrar_mensaje(f"TICKET {self.ticket_numero} GUARDADO.", "success")
            self.actualizar_inventario(productos)
            self.resetear_caja()
        except IOError:
            self.mostrar_mensaje("ERROR AL GUARDAR TICKET.", "error")

    def actualizar_inventario(self, productos_vendidos):
        """
        Actualiza el inventario restando las cantidades vendidas.
        """
        ruta_invent = "./db/inventario.json"
        try:
            with open(ruta_invent, "r", encoding='utf-8') as f:
                inv = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.mostrar_mensaje("ERROR AL CARGAR INVENTARIO PARA ACT.", "error")
            return

        inv_dict = {p["codigo"]: p for p in inv}
        for vendido in productos_vendidos:
            c_vendida = vendido["cantidad"]
            cod = vendido["codigo"]
            producto_vendido = next((p for p in self.inventario if p["codigo"] == cod), None)
            if producto_vendido:
                if producto_vendido.get("es_pesable", False):
                    # Convertir gramos a kilogramos antes de restar
                    inv_dict[cod]["cantidad"] -= c_vendida / 1000
                else:
                    inv_dict[cod]["cantidad"] -= c_vendida
            else:
                # Si no existe, agregarlo con cantidad negativa
                inv.append({
                    "codigo": cod,
                    "descripcion": vendido["descripcion"],
                    "cantidad": -c_vendida / 1000 if vendido.get("es_pesable", False) else -c_vendida,
                    "costo": 0.0,
                    "precio": vendido["precio_unitario"],
                    "es_pesable": vendido.get("es_pesable", False),
                    "fecha_ingreso": datetime.now().strftime("%d-%m-%Y"),
                    "fecha_vencimiento": "01-01-9999",
                    "oferta": 0
                })

        inv_actual = list(inv_dict.values())
        for p in inv:
            if p["codigo"] not in inv_dict:
                inv_actual.append(p)

        try:
            with open(ruta_invent, "w", encoding='utf-8') as f:
                json.dump(inv_actual, f, indent=4)
        except IOError:
            self.mostrar_mensaje("ERROR AL ACT INVENTARIO.", "error")

    def resetear_caja(self):
        self.table.setRowCount(0)
        self.actualizar_total()
        self.determinar_numero_ticket()

    def focus_on_entry(self):
        self.search_input.setFocus()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focus_on_entry()