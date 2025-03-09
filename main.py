# main.py

import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QDialog,
    QInputDialog, QMessageBox, QShortcut, QLineEdit
)
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt

from ui.login import Login
from ui.header import Header
from ui.footer import Footer
from ui.sidebar import Sidebar
from ui.caja import Caja
from ui.inventario import Inventario
from ui.clientes import Clientes
from ui.informes import Informes
from ui.balance import Balance


def cargar_sesion():
    """Carga el estado de la sesión desde el archivo session.json."""
    try:
        with open("./db/session.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"logged_in": False, "current_user": None}


def verificar_admin(password):
    """Verifica si la clave ingresada es válida para el usuario 'admin'."""
    try:
        with open("./db/usuarios.json", "r") as file:
            usuarios = json.load(file)
        for user in usuarios:
            if user.get("usuario") == "admin" and user.get("password") == password:
                return True
        return False
    except FileNotFoundError:
        return False


def reiniciar_base_datos():
    """Reinicia todos los archivos de la base de datos excepto usuarios.json y session.json."""
    db_dir = "./db"
    archivos_excluidos = {"usuarios.json", "session.json"}
    try:
        for archivo in os.listdir(db_dir):
            if archivo not in archivos_excluidos and archivo.endswith(".json"):
                ruta_archivo = os.path.join(db_dir, archivo)
                with open(ruta_archivo, "w") as file:
                    json.dump([], file, indent=4)
        
        # Reiniciar session.json
        session_path = os.path.join(db_dir, "session.json")
        with open(session_path, "w") as session_file:
            json.dump({"logged_in": False, "current_user": None}, session_file, indent=4)

        QMessageBox.information(None, "Éxito", "Base de datos reiniciada con éxito. La aplicación se cerrará ahora.")
        return True
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al reiniciar la base de datos: {e}")
        return False


class MainSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Header
        self.header = Header()
        layout.addWidget(self.header)

        # Content
        self.content = QStackedWidget()
        layout.addWidget(self.content, stretch=1)

        # Crear páginas de contenido
        self.page_caja = Caja()
        self.page_inventario = Inventario()
        self.page_clientes = Clientes()
        self.page_informes = Informes()
        self.page_balance = Balance()

        self.content.addWidget(self.page_caja)
        self.content.addWidget(self.page_inventario)
        self.content.addWidget(self.page_clientes)
        self.content.addWidget(self.page_informes)       
        self.content.addWidget(self.page_balance)

        # Footer
        self.footer = Footer()
        layout.addWidget(self.footer)

    def focus_on_current_page(self):
        """Activa el foco en la parte específica de la página activa."""
        current_page = self.content.currentWidget()
        if hasattr(current_page, "focus_on_entry"):
            current_page.focus_on_entry()    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("miPosQt")

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Sidebar
        self.sidebar = Sidebar(self)
        main_layout.addWidget(self.sidebar)

        # Main Section
        self.main_section = MainSection()
        main_layout.addWidget(self.main_section)

        # Establecer página inicial
        self.cambiar_pagina("Caja")

        # Atajo de teclado para reiniciar la base de datos
        self.shortcut_reiniciar = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_reiniciar.activated.connect(self.confirmar_reinicio)

        self.shortcut_fullscreen = QShortcut(QKeySequence("F11"), self)
        self.shortcut_fullscreen.activated.connect(self.toggle_fullscreen)

    def toggle_fullscreen(self):
            """Alterna entre pantalla completa y maximizado."""
            if self.isFullScreen():
                self.showMaximized()  # Salir de pantalla completa y volver a maximizado
            else:
                self.showFullScreen()  # Entrar en pantalla completa

    def confirmar_reinicio(self):
        """Solicita la contraseña del administrador para confirmar el reinicio."""
        admin_clave, ok = QInputDialog.getText(
            self, "Confirmar reinicio", "Ingrese la clave del administrador:", QLineEdit.Password
        )
        if not ok or not admin_clave.strip():
            return

        if verificar_admin(admin_clave.strip()):
            if reiniciar_base_datos():
                self.close()  # Cierra la aplicación tras el reinicio
        else:
            QMessageBox.critical(self, "Error", "Clave incorrecta.")

    def cambiar_pagina(self, pagina):
        """Cambia la página activa y realiza acciones específicas."""
        shortcuts = {
            "Caja": {"F5": "Ingreso", "F6": "Gasto", "F10": "Facturar"},
            "Inventario": {},
            "Clientes": {},
            "Informes": {},
            "Balance": {},
        }

        if pagina == "Caja":
            self.main_section.content.setCurrentWidget(self.main_section.page_caja)
            if hasattr(self.main_section.page_caja, "cargar_inventario"):
                self.main_section.page_caja.cargar_inventario()
        elif pagina == "Inventario":
            self.main_section.content.setCurrentWidget(self.main_section.page_inventario)
            if hasattr(self.main_section.page_inventario, "load_data"):
                self.main_section.page_inventario.load_data()
        elif pagina == "Clientes":
            self.main_section.content.setCurrentWidget(self.main_section.page_clientes)
        elif pagina == "Informes":
            self.main_section.content.setCurrentWidget(self.main_section.page_informes)
        elif pagina == "Balance":
            self.main_section.content.setCurrentWidget(self.main_section.page_balance)

        # Actualizar la selección visual en el Sidebar
        self.sidebar.select_button(pagina)

        # Actualizar shortcuts en el footer
        self.main_section.footer.update_shortcuts(shortcuts.get(pagina, {}))

        # Foco en la página activa
        self.main_section.focus_on_current_page()


def main():
    app = QApplication(sys.argv)

    # Verificar estado de la sesión
    session = cargar_sesion()
    if not session.get("logged_in"):
        login_dialog = Login()
        login_dialog.setWindowTitle("Hola, bienvenido a mi querencia")
        if login_dialog.exec_() != QDialog.Accepted:
            sys.exit(0)

    # Crear ventana principal
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()