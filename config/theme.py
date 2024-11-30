# -*- coding: utf-8 -*-

# الألوان الرئيسية
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#34495e"
ACCENT_COLOR = "#3498db"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f1c40f"
DANGER_COLOR = "#e74c3c"

# أنماط العناصر
MAIN_STYLE = f"""
QMainWindow {{
    background-color: white;
}}

QMenuBar {{
    background-color: {PRIMARY_COLOR};
    color: white;
    padding: 5px;
}}

QMenuBar::item:selected {{
    background-color: {SECONDARY_COLOR};
}}

QMenu {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
}}

QMenu::item:selected {{
    background-color: {SECONDARY_COLOR};
}}
"""

SIDEBAR_STYLE = f"""
QWidget {{
    background-color: {PRIMARY_COLOR};
    color: white;
}}

QPushButton {{
    text-align: right;
    padding: 12px;
    border: none;
    background-color: transparent;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {SECONDARY_COLOR};
}}

QPushButton:checked {{
    background-color: {ACCENT_COLOR};
}}

QLabel {{
    padding: 15px;
    font-size: 13px;
}}
"""

TABLE_STYLE = """
QTableWidget {
    background-color: white;
    alternate-background-color: #f5f5f5;
    selection-background-color: #e0e0e0;
    border: none;
}

QTableWidget::item {
    padding: 5px;
}

QHeaderView::section {
    background-color: #f0f0f0;
    padding: 5px;
    border: none;
    font-weight: bold;
}
"""

BUTTON_STYLE = f"""
QPushButton {{
    background-color: {ACCENT_COLOR};
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {SECONDARY_COLOR};
}}

QPushButton:pressed {{
    background-color: {PRIMARY_COLOR};
}}

QPushButton:disabled {{
    background-color: #cccccc;
}}
"""

INPUT_STYLE = """
QLineEdit, QComboBox {
    padding: 8px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: white;
}

QLineEdit:focus, QComboBox:focus {
    border-color: #3498db;
}

QComboBox::drop-down {
    border: none;
    padding-right: 15px;
}
"""

DIALOG_STYLE = f"""
QDialog {{
    background-color: white;
}}

QLabel {{
    color: {PRIMARY_COLOR};
}}

QPushButton[type="success"] {{
    background-color: {SUCCESS_COLOR};
}}

QPushButton[type="danger"] {{
    background-color: {DANGER_COLOR};
}}
""" 