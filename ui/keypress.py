# ui/keypress.py

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QMainWindow

class KeyPressHandler(QObject):
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window
        # Instalar el filtro de eventos en la ventana principal
        self.main_window.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            key = event.key()
            modifiers = event.modifiers()

            # Ignorar eventos de teclado si un modal está abierto
            if self.main_window.activeModal():
                return False  # Permitir que el modal maneje el evento

            # Manejo de teclas de navegación global
            if key == Qt.Key_Left:
                self.main_window.cambiar_pagina_anterior()
                return True  # Evento manejado
            elif key == Qt.Key_Right:
                self.main_window.cambiar_pagina_siguiente()
                return True
            elif key == Qt.Key_Up:
                self.main_window.navegar_arriba()
                return True
            elif key == Qt.Key_Down:
                self.main_window.navegar_abajo()
                return True

        return super().eventFilter(obj, event)
