# ui/informe_caja.py

import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from fpdf import FPDF

class InformeDeCaja(QDialog):
    def __init__(self, num_session, cajero, tickets, notas, parent=None):
        super().__init__(parent)
        self.num_session = num_session.strip()
        self.cajero = cajero
        self.tickets = tickets
        self.notas = notas
        self.ruta_json = "./db/cajas_rendidas.json"

        # Quitar botones de cerrar, minimizar y maximizar
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Informe de Caja")
        self.setFixedSize(1200, 800)  # Aumentar el tamaño para acomodar mejor el contenido

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # ------------------ TÍTULO PRINCIPAL ------------------
        title = QLabel(f"Cierre de Caja - {self.cajero}")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # ------------------ FECHA Y NÚMERO DE SESIÓN ------------------
        fecha_layout = QHBoxLayout()
        fecha_label = QLabel(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        fecha_label.setFont(QFont("Arial", 14))
        fecha_label.setAlignment(Qt.AlignLeft)

        sesion_label = QLabel(f"Número de Sesión: {self.num_session}")
        sesion_label.setFont(QFont("Arial", 14))
        sesion_label.setAlignment(Qt.AlignRight)

        fecha_layout.addWidget(fecha_label)
        fecha_layout.addWidget(sesion_label)
        main_layout.addLayout(fecha_layout)

        # ------------------ RESUMEN POR MÉTODOS DE PAGO ------------------
        resumen = self.calcular_resumen()
        resumen_table = QTableWidget()
        resumen_table.setRowCount(1)
        resumen_table.setColumnCount(4)  # Solo métodos de pago
        resumen_table.setHorizontalHeaderLabels(["Efectivo", "Transferencia", "Posnet", "Crédito"])
        resumen_table.horizontalHeader().setFont(QFont("Arial", 16, QFont.Bold))
        resumen_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        resumen_table.horizontalHeader().setHighlightSections(False)
        resumen_table.verticalHeader().setVisible(False)
        resumen_table.setFont(QFont("Arial", 18))
        resumen_table.setEditTriggers(QTableWidget.NoEditTriggers)
        resumen_table.setStyleSheet("""
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
        metodos = ["efectivo", "transferencia", "posnet", "crédito"]  # con acento
        for i, metodo in enumerate(metodos):
            monto = resumen.get(metodo, 0)
            item = QTableWidgetItem(f"${monto:.2f}")
            item.setFont(QFont("Arial", 18, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            resumen_table.setItem(0, i, item)

        main_layout.addWidget(resumen_table)

        # ------------------ SECCIÓN OPERACIONES Y NOTAS ------------------
        operaciones_layout = QHBoxLayout()
        main_layout.addLayout(operaciones_layout)

        # -- Ingresos Layout --
        ingresos_layout = QVBoxLayout()
        ingresos_title = QLabel("Ingresos:")
        ingresos_title.setFont(QFont("Arial", 16, QFont.Bold))
        ingresos_title.setStyleSheet("color: #27ae60;")
        ingresos_layout.addWidget(ingresos_title)
        if resumen["ingresos_detalle"]:
            for ingreso in resumen["ingresos_detalle"]:
                nota = ingreso.get("nota", "Sin nota")
                m = ingreso.get("monto", 0.0)
                lbl = QLabel(f"Nota: {nota}, Monto: ${m:.2f}")
                font = QFont("Arial", 12)
                font.setItalic(True)  # Correcto uso de italic
                lbl.setFont(font)
                ingresos_layout.addWidget(lbl)
        else:
            lbl = QLabel("No hay ingresos para esta sesión.")
            font = QFont("Arial", 12)
            font.setItalic(True)  # Correcto uso de italic
            lbl.setFont(font)
            ingresos_layout.addWidget(lbl)
        operaciones_layout.addLayout(ingresos_layout)

        # -- Egresos Layout --
        egresos_layout = QVBoxLayout()
        egresos_title = QLabel("Egresos:")
        egresos_title.setFont(QFont("Arial", 16, QFont.Bold))
        egresos_title.setStyleSheet("color: #e74c3c;")
        egresos_layout.addWidget(egresos_title)
        if resumen["egresos_detalle"]:
            for egreso in resumen["egresos_detalle"]:
                nota = egreso.get("nota", "Sin nota")
                m = egreso.get("monto", 0.0)
                lbl = QLabel(f"Nota: {nota}, Monto: ${m:.2f}")
                font = QFont("Arial", 12)
                font.setItalic(True)  # Correcto uso de italic
                lbl.setFont(font)
                egresos_layout.addWidget(lbl)
        else:
            lbl = QLabel("No hay egresos para esta sesión.")
            font = QFont("Arial", 12)
            font.setItalic(True)  # Correcto uso de italic
            lbl.setFont(font)
            egresos_layout.addWidget(lbl)
        operaciones_layout.addLayout(egresos_layout)

        # -- Notas de Cierre Layout --
        if isinstance(self.notas, dict) and self.notas:
            notas_cierre_layout = QVBoxLayout()
            notas_title = QLabel("Notas de Cierre:")
            notas_title.setFont(QFont("Arial", 16, QFont.Bold))
            notas_title.setStyleSheet("color: #8e44ad;")
            notas_cierre_layout.addWidget(notas_title)
            for k, v in self.notas.items():
                lbl = QLabel(f"{k}: {v}")
                font = QFont("Arial", 12)
                font.setItalic(True)  # Opcional: Puedes decidir si quieres que las notas sean en cursiva
                lbl.setFont(font)
                notas_cierre_layout.addWidget(lbl)
            operaciones_layout.addLayout(notas_cierre_layout)

        # ------------------ TOTAL DE VENTAS ------------------
        total_ventas_label = QLabel(f"TOTAL EN VENTAS: ${resumen['total']:.2f}")
        total_ventas_label.setFont(QFont("Arial", 36, QFont.Bold))
        total_ventas_label.setAlignment(Qt.AlignCenter)
        total_ventas_label.setStyleSheet("""
            QLabel {
                background-color: #f9e79f;
                color: black;
                border: 2px solid #d3d3d3;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        main_layout.addWidget(total_ventas_label)

        # ------------------ BOTÓN "Cerrar" ------------------
        close_button = QPushButton("Cerrar")
        close_button.setFont(QFont("Arial", 20, QFont.Bold))  # Aumentar tamaño de fuente a 20
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px 30px;  /* Aumentar padding */
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)

        # ------------------ GUARDAR INFORME ------------------
        self.guardar_informe(resumen)

    def calcular_resumen(self):
        """Calcula los totales y detalles de métodos de pago."""
        resumen = {
            "total": 0.0,
            "efectivo": 0.0,
            "transferencia": 0.0,
            "posnet": 0.0,
            "crédito": 0.0,
            "ingresos": 0.0,
            "egresos": 0.0,
            "ingresos_detalle": [],
            "egresos_detalle": [],
        }
        metodos_validos = {"efectivo", "transferencia", "posnet", "crédito"}

        for t in self.tickets:
            monto_ticket = t.get("monto", 0.0)
            resumen["total"] += monto_ticket
            for p in t.get("pagos", []):
                metodo = p.get("metodo", "").strip().lower()
                if metodo in metodos_validos:
                    if metodo == "efectivo":
                        monto_real = p.get("monto", 0.0) - t.get("cambio", 0.0)
                        resumen["efectivo"] += monto_real
                    else:
                        resumen[metodo] += p.get("monto", 0.0)

        # Leer registro_operaciones
        registros = self.cargar_registro_operaciones()
        print(f"Operaciones Cargadas: {registros}")  # Mostrar en consola

        for r in registros:
            if r.get("num_session", "").strip() == self.num_session:
                tipo = r.get("tipo", "").lower().strip()
                if tipo == "ingreso":
                    resumen["ingresos"] += r.get("monto", 0.0)
                    resumen["ingresos_detalle"].append(r)
                elif tipo == "gasto":
                    resumen["egresos"] += r.get("monto", 0.0)
                    resumen["egresos_detalle"].append(r)

        print(f"Resumen Calculado: {resumen}")  # Mostrar en consola

        return resumen

    def cargar_registro_operaciones(self):
        ruta_op = "./db/registro_operaciones.json"
        if os.path.exists(ruta_op):
            try:
                with open(ruta_op, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error al leer registro_operaciones.json: {e}")
                return []
        print("registro_operaciones.json no existe.")
        return []

    def guardar_informe(self, resumen):
        self.guardar_json(resumen)
        self.generar_pdf(resumen)

    def guardar_json(self, resumen):
        caja_data = {
            "num_session": self.num_session,
            "cajero": self.cajero,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notas": self.notas,
            **resumen,
        }
        try:
            if os.path.exists(self.ruta_json):
                with open(self.ruta_json, "r", encoding="utf-8") as file:
                    cajas = json.load(file)
            else:
                cajas = []

            cajas.append(caja_data)
            with open(self.ruta_json, "w", encoding="utf-8") as file:
                json.dump(cajas, file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el informe: {e}")

    def generar_pdf(self, resumen):
        carpeta = f"./rendiciones/{datetime.now().strftime('%Y%m%d')}-{self.cajero}"
        os.makedirs(carpeta, exist_ok=True)
        ruta_pdf = os.path.join(carpeta, f"cierre_caja_{self.num_session}.pdf")

        pdf = FPDF(format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Título principal
        pdf.set_font("Arial", size=18, style='B')
        pdf.cell(200, 10, txt=f"Cierre de Caja - {self.cajero}", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(200, 10, txt=f"Número de Sesión: {self.num_session}", ln=True)
        pdf.ln(5)

        # Resumen de Métodos de Pago
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="Resumen de Métodos de Pago:", ln=True)
        pdf.set_font("Arial", size=12)
        for metodo in ["Efectivo", "Transferencia", "Posnet", "Crédito"]:
            m_key = metodo.lower().replace("í", "i")  # "crédito" -> "credito"
            if metodo.lower() == "crédito":
                m_key = "crédito"
            monto = resumen.get(m_key, 0.0)
            pdf.cell(200, 10, txt=f"{metodo}: ${monto:.2f}", ln=True)
        pdf.ln(5)

        # Detalle Ingresos/Egresos
        if resumen["ingresos_detalle"] or resumen["egresos_detalle"]:
            pdf.set_font("Arial", size=14, style='B')
            pdf.cell(100, 10, txt="Ingresos:", ln=False)
            pdf.cell(100, 10, txt="Egresos:", ln=True)
            pdf.set_font("Arial", size=12)
            max_ing = len(resumen["ingresos_detalle"])
            max_eg = len(resumen["egresos_detalle"])
            max_rows = max(max_ing, max_eg)
            for i in range(max_rows):
                # Ingresos
                if i < max_ing:
                    ing = resumen["ingresos_detalle"][i]
                    nota = ing.get("nota", "Sin nota")
                    m = ing.get("monto", 0.0)
                    ing_text = f"Nota: {nota}, Monto: ${m:.2f}"
                else:
                    ing_text = ""
                pdf.cell(100, 10, txt=ing_text, ln=False)

                # Egresos
                if i < max_eg:
                    eg = resumen["egresos_detalle"][i]
                    nota = eg.get("nota", "Sin nota")
                    m = eg.get("monto", 0.0)
                    eg_text = f"Nota: {nota}, Monto: ${m:.2f}"
                else:
                    eg_text = ""
                pdf.cell(100, 10, txt=eg_text, ln=True)
            pdf.ln(5)

        # Notas de Cierre
        if self.notas:
            pdf.set_font("Arial", size=14, style='B')
            pdf.cell(200, 10, txt="Notas de Cierre:", ln=True)
            pdf.set_font("Arial", size=12)
            for k, v in self.notas.items():
                pdf.multi_cell(0, 10, txt=f"{k}: {v}")
            pdf.ln(5)

        # Total de Ventas
        pdf.set_font("Arial", size=18, style='B')
        pdf.cell(200, 10, txt=f"TOTAL EN VENTAS: ${resumen['total']:.2f}", ln=True, align="C")
        pdf.ln(10)

        # Guardar PDF
        try:
            pdf.output(ruta_pdf)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF: {e}")
