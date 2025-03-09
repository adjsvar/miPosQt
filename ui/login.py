# ui/login.py
from PyQt5.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import json
import os
from datetime import datetime


class Login(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inicio de Sesión")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.ApplicationModal)

        self.init_ui()

    def init_ui(self):
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Mensaje de bienvenida
        bienvenida_label = QLabel("Hola, bienvenido a mi querencia, ya puedes iniciar sesión")
        bienvenida_label.setFont(QFont("Arial", 12, QFont.Bold))
        bienvenida_label.setAlignment(Qt.AlignCenter)
        bienvenida_label.setWordWrap(True)
        layout.addWidget(bienvenida_label)

        # Selección de usuario
        usuario_label = QLabel("Selecciona tu usuario:")
        usuario_label.setFont(QFont("Arial", 12))
        layout.addWidget(usuario_label)

        self.user_combo = QComboBox()
        self.user_combo.setFont(QFont("Arial", 12))
        self.cargar_usuarios()
        layout.addWidget(self.user_combo)

        # Conectar la señal de cambio de selección para enfocar el campo de contraseña
        self.user_combo.currentIndexChanged.connect(self.enfocar_password)

        # Campo de contraseña
        password_label = QLabel("Contraseña:")
        password_label.setFont(QFont("Arial", 12))
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Botón de inicio de sesión
        login_button = QPushButton("Iniciar Sesión")
        login_button.setFont(QFont("Arial", 12))
        login_button.clicked.connect(self.iniciar_sesion)
        layout.addWidget(login_button)

        # Establecer el foco en el campo de contraseña al iniciar el diálogo
        self.setFocusPolicy(Qt.StrongFocus)
        self.password_input.setFocus()

    def cargar_usuarios(self):
        """Carga los usuarios desde el archivo JSON."""
        try:
            with open("./db/usuarios.json", "r", encoding="utf-8") as file:
                usuarios = json.load(file)
                for usuario in usuarios:
                    self.user_combo.addItem(usuario["usuario"])
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "El archivo de usuarios no existe.")
            self.reject()
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "El archivo de usuarios está corrupto.")
            self.reject()

    def iniciar_sesion(self):
        """Verifica las credenciales e inicia sesión si son correctas."""
        usuario = self.user_combo.currentText()
        password = self.password_input.text()

        # Validación de campos vacíos
        if not usuario or not password:
            QMessageBox.warning(self, "Error", "Usuario y contraseña no pueden estar vacíos.")
            return

        try:
            with open("./db/usuarios.json", "r", encoding="utf-8") as file:
                usuarios = json.load(file)

            for u in usuarios:
                if u["usuario"] == usuario and u["password"] == password:
                    self.guardar_sesion(usuario)
                    self.accept()
                    return

            # Si no se encontró coincidencia, mostrar mensaje de error, limpiar contraseña y enfocar
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            self.password_input.clear()
            self.password_input.setFocus()

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "El archivo de usuarios no existe.")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "El archivo de usuarios está corrupto.")

    def guardar_sesion(self, usuario):
        """Guarda el estado de la sesión en el archivo JSON y registra la sesión."""
        # Crear el número único de sesión
        num_session = datetime.now().strftime("%Y%m%d-%H%M%S")  # Formato AAAAMMDD-HHMMSS
        sesion_data = {
            "usuario": usuario,
            "fecha_hora_inicio": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "num_session": num_session
        }

        # Guardar la sesión activa en session.json
        try:
            with open("./db/session.json", "w", encoding="utf-8") as file:
                json.dump({"logged_in": True, "current_user": usuario, "num_session": num_session}, file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la sesión activa en session.json: {e}")
            return

        # Registrar la sesión en sesiones.json
        try:
            ruta_sesiones = "./db/sesiones.json"

            # Cargar sesiones existentes o crear una lista nueva
            if not os.path.exists(ruta_sesiones):
                sesiones = []
            else:
                with open(ruta_sesiones, "r", encoding="utf-8") as file:
                    sesiones = json.load(file)

            # Agregar la nueva sesión
            sesiones.append(sesion_data)

            # Guardar el registro actualizado
            with open(ruta_sesiones, "w", encoding="utf-8") as file:
                json.dump(sesiones, file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar la sesión en sesiones.json: {e}")

    def enfocar_password(self):
        """
        Enfoca el cursor en el campo de contraseña cuando se selecciona un usuario.
        Opcionalmente, limpia el campo de contraseña al cambiar de usuario.
        """
        self.password_input.clear()
        self.password_input.setFocus()

    def showEvent(self, event):
        """
        Sobrescribe el método showEvent para asegurar que el foco se coloque en el campo de contraseña
        una vez que el diálogo se muestra.
        """
        super().showEvent(event)
        self.password_input.setFocus()
