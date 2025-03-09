# ui/sidebar.py

import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy,
    QMessageBox, QDialog  # Asegúrate de incluir QDialog
)

from PyQt5.QtWidgets import QApplication  # Añadido para cerrar la aplicación


from .editarperfil import EditarPerfil
from .informe_caja import InformeDeCaja
from .notas import NotasDialog
from .informes import Informes  # Asegúrate de importar la clase Informes


class Sidebar(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.setFixedWidth(200)  # Ancho del sidebar

        # Definir el color de fondo
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#2c3e50"))  # Color oscuro de fondo
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        # Foto de usuario
        self.user_image_label = QLabel()
        pixmap = QPixmap(self.get_user_image())
        pixmap = self.make_square_pixmap(pixmap, size=120)
        self.user_image_label.setPixmap(pixmap)
        self.user_image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.user_image_label)

        # Mensaje de usuario
        self.welcome_label = QLabel(f"{self.get_current_user()}")
        self.welcome_label.setFont(QFont("Arial", 14))
        self.welcome_label.setStyleSheet("color: white;")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setFixedHeight(50)
        main_layout.addWidget(self.welcome_label)

        # Botón Editar Perfil
        edit_profile_button = QPushButton("Editar Perfil")
        edit_profile_button.setFixedHeight(50)
        edit_profile_button.setFont(QFont("Arial", 16))
        edit_profile_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_profile_button.clicked.connect(self.open_edit_profile)
        main_layout.addWidget(edit_profile_button)

        # Espaciador
        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botones principales
        self.buttons = {}
        button_names = ["Caja", "Inventario", "Clientes", "Informes"]
        for name in button_names:
            button = QPushButton(name)
            button.setFixedHeight(50)
            button.setFont(QFont("Arial", 16))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #3d566e;
                }
            """)
            button.clicked.connect(self.change_content)
            main_layout.addWidget(button)
            self.buttons[name] = button

        # Seleccionar botón inicial (opcional)
        self.select_button("Caja")

           # Añadir un estirador para empujar los botones principales hacia arriba
        main_layout.addStretch()

        # Layout para el botón "Cerrar Sesión"
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 10)  # Márgenes para alinear con otros botones
        bottom_layout.setSpacing(0)

        # Botón "Cerrar Sesión"
        logout_button = QPushButton("Cierre de Caja")
        logout_button.setFixedHeight(50)
        logout_button.setFont(QFont("Arial", 16))
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 10px;
                margin-left: 10px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        logout_button.clicked.connect(self.logout)

        # Añadir el botón al layout inferior
        bottom_layout.addWidget(logout_button, alignment=Qt.AlignBottom)

        # Añadir el layout inferior al layout principal
        main_layout.addLayout(bottom_layout)


    def select_button(self, name):
        """Actualiza el estilo del botón seleccionado."""
        for button_name, button in self.buttons.items():
            if button_name == name:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #1abc9c;
                        color: white;
                        border: none;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #16a085;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #34495e;
                        color: white;
                        border: none;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #3d566e;
                    }
                """)

    def get_user_image(self):
        """Obtiene la ruta de la imagen del usuario actual desde el archivo JSON de sesión."""
        try:
            with open("./db/session.json", "r", encoding="utf-8") as session_file:
                session_data = json.load(session_file)
            current_user = session_data.get("current_user", "")
            with open("./db/usuarios.json", "r", encoding="utf-8") as users_file:
                users = json.load(users_file)
                for user in users:
                    if user["usuario"] == current_user:
                        return user.get("imagen", "./assets/anonimo.jpg")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        # Si falla, retorna una imagen por defecto
        return "./assets/anonimo.jpg"

    def get_current_user(self):
        """Obtiene el nombre del usuario actual desde el archivo JSON de sesión."""
        try:
            with open("./db/session.json", "r", encoding="utf-8") as session_file:
                session_data = json.load(session_file)
                return session_data.get("current_user", "Invitado")
        except (FileNotFoundError, json.JSONDecodeError):
            return "Invitado"

    def make_square_pixmap(self, pixmap, size=200):
        """Convierte un QPixmap a un formato cuadrado recortando y escalando."""
        if pixmap.isNull():
            pixmap = QPixmap("./assets/anonimo.jpg")  # Imagen por defecto si no se carga correctamente
        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        image = pixmap.toImage()
        side = min(image.width(), image.height())
        square_image = image.copy(
            (image.width() - side) // 2,
            (image.height() - side) // 2,
            side,
            side
        )
        return QPixmap.fromImage(square_image)

    def change_content(self):
        """Cambia el contenido mostrado en la aplicación y marca el botón seleccionado."""
        sender = self.sender()
        page = sender.text()
        self.select_button(page)
        self.main.cambiar_pagina(page)

        # MODIFICACIÓN: Recargar la lista de clientes al hacer clic en "Clientes"
        if page == "Clientes":
            if hasattr(self.main.main_section.page_clientes, "load_clientes"):
                self.main.main_section.page_clientes.load_clientes()

        # NUEVA MODIFICACIÓN: Recargar informes al hacer clic en "Informes"
        if page == "Informes":
            if hasattr(self.main.main_section.page_informes, "load_informe_vencimientos"):
                self.main.main_section.page_informes.load_informe_vencimientos()

    def open_edit_profile(self):
        """Abre la ventana para editar el perfil."""
        edit_profile_dialog = EditarPerfil(parent=self, update_sidebar_callback=self.update_user_info)
        edit_profile_dialog.exec_()

    def logout(self):
        """
        Cierra la sesión del usuario y muestra, si procede, el NotasDialog
        y el InformeDeCaja con los tickets de la sesión actual.
        """
        # 1. Cargar datos de la sesión
        try:
            with open("./db/session.json", "r", encoding="utf-8") as file:
                session_data = json.load(file)
                num_session = session_data.get("num_session", "N/A")
                current_user = session_data.get("current_user", "Desconocido")
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "No se encontró la sesión activa.")
            return

        # 2. Cargar tickets de la sesión actual
        try:
            with open("./db/tickets.json", "r", encoding="utf-8") as file:
                all_tickets = json.load(file)
            tickets_session = [t for t in all_tickets if t.get("num_session") == num_session]
        except FileNotFoundError:
            tickets_session = []

        # 3. Verificar si existen tickets para la sesión
        if tickets_session:
            # Mostrar el diálogo de notas
            notas_dialog = NotasDialog(parent=self)
            if notas_dialog.exec_() == QDialog.Accepted:
                notas = notas_dialog.get_notas()
            else:
                # Si el usuario cancela el diálogo de notas, se cancela el logout
                return

            # Mostrar el informe de caja con las notas
            informe_dialog = InformeDeCaja(num_session, current_user, tickets_session, notas, parent=self)
            if informe_dialog.exec_() == QDialog.Accepted:
                # Al cerrar el informe, terminar la aplicación (cerrar sesión)
                session_data = {"logged_in": False, "current_user": ""}
                try:
                    with open("./db/session.json", "w", encoding="utf-8") as file:
                        json.dump(session_data, file, indent=4)
                    QApplication.quit()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"No se pudo cerrar sesión: {e}")
        else:
            # Si no hay tickets, confirmar si realmente se desea cerrar
            respuesta = QMessageBox.question(
                self,
                "Cerrar Sesión",
                "No se encontraron tickets para esta sesión. ¿Desea cerrar sesión?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if respuesta == QMessageBox.Yes:
                session_data = {"logged_in": False, "current_user": ""}
                try:
                    with open("./db/session.json", "w", encoding="utf-8") as file:
                        json.dump(session_data, file, indent=4)
                    QApplication.quit()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"No se pudo cerrar sesión: {e}")

    def update_user_info(self):
        """Actualiza la foto y el nombre del usuario en el sidebar."""
        pixmap = QPixmap(self.get_user_image())
        pixmap = self.make_square_pixmap(pixmap, size=120)
        self.user_image_label.setPixmap(pixmap)
        self.welcome_label.setText(self.get_current_user())
