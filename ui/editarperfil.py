from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import json
import shutil


class EditarPerfil(QDialog):
    def __init__(self, parent=None, update_sidebar_callback=None):
        super().__init__(parent)
        self.update_sidebar_callback = update_sidebar_callback
        self.selected_image_path = None  # Ruta de la imagen seleccionada
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Editar Perfil")
        self.setFixedSize(500, 450)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Título
        title_label = QLabel("Editar Perfil")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Campos de edición
        form_layout = QVBoxLayout()
        layout.addLayout(form_layout)

        # Nombre de usuario
        self.username_label = QLabel("Nombre de Usuario:")
        self.username_label.setFont(QFont("Arial", 14))
        form_layout.addWidget(self.username_label)

        self.username_entry = QLineEdit()
        self.username_entry.setFont(QFont("Arial", 14))
        self.username_entry.setFixedHeight(40)
        form_layout.addWidget(self.username_entry)

        # Contraseña
        self.password_label = QLabel("Contraseña:")
        self.password_label.setFont(QFont("Arial", 14))
        form_layout.addWidget(self.password_label)

        self.password_entry = QLineEdit()
        self.password_entry.setFont(QFont("Arial", 14))
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFixedHeight(40)
        form_layout.addWidget(self.password_entry)

        # Imagen
        self.image_label = QLabel("Imagen de Perfil:")
        self.image_label.setFont(QFont("Arial", 14))
        form_layout.addWidget(self.image_label)

        self.image_path_label = QLabel("Ruta: Ninguna seleccionada")
        self.image_path_label.setFont(QFont("Arial", 12))
        form_layout.addWidget(self.image_path_label)

        select_image_button = QPushButton("Seleccionar Imagen")
        select_image_button.setFont(QFont("Arial", 14))
        select_image_button.setFixedHeight(40)
        select_image_button.clicked.connect(self.select_image)
        form_layout.addWidget(select_image_button)

        # Espaciador entre "Seleccionar Imagen" y los botones
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Botones Guardar y Cancelar
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.save_button = QPushButton("Guardar Cambios")
        self.save_button.setFont(QFont("Arial", 14))
        self.save_button.setFixedHeight(50)
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)

        cancel_button = QPushButton("Cancelar")
        cancel_button.setFont(QFont("Arial", 14))
        cancel_button.setFixedHeight(50)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        # Configurar la navegación entre widgets
        self.username_entry.setFocus()

    def keyPressEvent(self, event):
        """Captura las teclas presionadas y evita que Enter cierre el formulario."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Mueve el foco al siguiente widget en lugar de cerrar el formulario
            self.focusNextChild()
        else:
            # Permite el comportamiento predeterminado para otras teclas
            super().keyPressEvent(event)

    def select_image(self):
        """Permite seleccionar una nueva imagen para el perfil."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", "Archivos de Imagen (*.png *.jpg *.jpeg)", options=options
        )
        if file_path:
            self.image_path_label.setText(f"Ruta: {file_path}")
            self.selected_image_path = file_path

    def save_changes(self):
        """Guarda los cambios en el perfil del usuario."""
        try:
            # Leer los datos actuales de sesión
            with open("./db/session.json", "r") as session_file:
                session_data = json.load(session_file)
            current_user = session_data["current_user"]

            # Leer los datos de usuarios
            with open("./db/usuarios.json", "r") as users_file:
                users = json.load(users_file)

            # Buscar y actualizar al usuario actual
            updated_fields = False
            for user in users:
                if user["usuario"] == current_user:
                    if self.username_entry.text().strip() and self.username_entry.text().strip() != user["usuario"]:
                        user["usuario"] = self.username_entry.text().strip()
                        session_data["current_user"] = user["usuario"]
                        updated_fields = True

                    if self.password_entry.text().strip():
                        user["password"] = self.password_entry.text().strip()
                        updated_fields = True

                    if self.selected_image_path:
                        new_image_path = f"./assets/{user['usuario']}.jpg"
                        shutil.copy(self.selected_image_path, new_image_path)
                        user["imagen"] = new_image_path
                        updated_fields = True

                    break

            # Guardar los cambios en los archivos si hubo modificaciones
            if updated_fields:
                with open("./db/usuarios.json", "w") as users_file:
                    json.dump(users, users_file, indent=4)
                with open("./db/session.json", "w") as session_file:
                    json.dump(session_data, session_file, indent=4)

                # Llamar al callback para actualizar el Sidebar
                if self.update_sidebar_callback:
                    self.update_sidebar_callback()

            self.close()
        except Exception as e:
            print(f"Error al guardar los cambios: {e}")
