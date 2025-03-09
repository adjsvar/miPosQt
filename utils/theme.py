# utils/theme.py

"""
Módulo para definir los temas de color y estilos consistentes en la aplicación.
"""

class Theme:
    """Clase para manejar los temas y estilos de la aplicación."""
    
    # Colores principales
    PRIMARY = "#2980b9"     # Azul principal
    SECONDARY = "#27ae60"   # Verde secundario
    ACCENT = "#f39c12"      # Naranja acento
    ERROR = "#e74c3c"       # Rojo error
    WARNING = "#f1c40f"     # Amarillo advertencia
    INFO = "#3498db"        # Azul info
    SUCCESS = "#2ecc71"     # Verde éxito
    
    # Colores de fondo
    BG_DARK = "#2c3e50"     # Fondo oscuro (sidebar)
    BG_LIGHT = "#ecf0f1"    # Fondo claro (main)
    BG_WHITE = "#ffffff"    # Fondo blanco
    
    # Colores de texto
    TEXT_DARK = "#2c3e50"   # Texto oscuro
    TEXT_LIGHT = "#ecf0f1"  # Texto claro
    TEXT_WHITE = "#ffffff"  # Texto blanco
    
    # Estilos para botones
    @staticmethod
    def button_style(color=PRIMARY, text_color=TEXT_WHITE, hover_color=None):
        """Genera el estilo para botones."""
        if hover_color is None:
            # Oscurecer el color principal para el hover
            hover_color = Theme.darken_color(color, 0.8)
            
        return f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {Theme.darken_color(color, 0.7)};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """
    
    # Estilos para QLineEdit
    @staticmethod
    def input_style(focus_color=PRIMARY):
        """Genera el estilo para campos de entrada."""
        return f"""
            QLineEdit {{
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                background-color: #ffffff;
                color: {Theme.TEXT_DARK};
            }}
            QLineEdit:focus {{
                border: 2px solid {focus_color};
                background-color: #f8f9fa;
            }}
        """
    
    # Estilos para QTableWidget
    @staticmethod
    def table_style():
        """Genera el estilo para tablas."""
        return f"""
            QTableWidget {{
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                border: 1px solid #dcdcdc;
                gridline-color: #dcdcdc;
                selection-background-color: #b3d9ff;
                selection-color: #000000;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid #eeeeee;
            }}
            QHeaderView::section {{
                background-color: {Theme.BG_DARK};
                color: {Theme.TEXT_WHITE};
                font-weight: bold;
                padding: 8px;
                border: none;
            }}
        """
    
    # Estilos para QLabel (títulos)
    @staticmethod
    def title_style(color=TEXT_DARK, size=18):
        """Genera el estilo para títulos."""
        return f"""
            QLabel {{
                color: {color};
                font-size: {size}px;
                font-weight: bold;
                padding: 10px;
            }}
        """
    
    # Utilidad para oscurecer colores
    @staticmethod
    def darken_color(hex_color, factor=0.8):
        """Oscurece un color hexadecimal por un factor (0-1)."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # Estilos específicos por componente
    @staticmethod
    def sidebar_button_style(is_active=False):
        """Estilo para botones del sidebar."""
        if is_active:
            return f"""
                QPushButton {{
                    background-color: {Theme.SECONDARY};
                    color: {Theme.TEXT_WHITE};
                    border: none;
                    border-left: 5px solid {Theme.ACCENT};
                    border-radius: 0px;
                    padding: 15px;
                    text-align: left;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Theme.darken_color(Theme.SECONDARY, 0.9)};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {Theme.BG_DARK};
                    color: {Theme.TEXT_WHITE};
                    border: none;
                    border-left: 5px solid transparent;
                    border-radius: 0px;
                    padding: 15px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {Theme.darken_color(Theme.BG_DARK, 0.8)};
                    border-left: 5px solid {Theme.ACCENT};
                }}
            """