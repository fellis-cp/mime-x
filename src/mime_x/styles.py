QSS = """
QMainWindow {
    background-color: #0A0A0B;
}

QWidget {
    color: #E0E0E0;
    font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
}

/* Sidebar Navigation */
#NavSidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161618, stop:1 #0F0F10);
    border-right: 1px solid #222224;
    min-width: 80px;
    max-width: 80px;
}

#NavButton {
    background: transparent;
    border: none;
    border-radius: 12px;
}

#NavButton:hover {
    background: rgba(255, 255, 255, 0.05);
}

#NavButton[selected="true"] {
    background: rgba(61, 90, 254, 0.15);
    border-left: 3px solid #3D5AFE;
    border-radius: 0 12px 12px 0;
}

/* Page Titles */
#Title {
    font-size: 32px;
    font-weight: 800;
    color: #FFFFFF;
}

#SubTitle {
    font-size: 15px;
    color: #888888;
}

/* Search Input */
QLineEdit {
    background-color: #1A1A1C;
    border: 1px solid #2D2D30;
    border-radius: 10px;
    padding: 10px 15px;
    color: #FFFFFF;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #3D5AFE;
    background-color: #1E1E22;
}

/* List Widget (Explorer) */
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget::item {
    padding: 12px 15px;
    margin-bottom: 4px;
    border-radius: 8px;
    color: #CCCCCC;
}

QListWidget::item:selected {
    background-color: #252528;
    color: #3D5AFE;
    font-weight: bold;
}

QListWidget::item:hover {
    background-color: #1E1E20;
}

/* Detail Panel */
#DetailPanel {
    background-color: #0F0F10;
    border-left: 1px solid #222224;
}

/* Cards (Essentials & Audit) */
#EssentialCard, #AppItemCard {
    background-color: #161618;
    border: 1px solid #222224;
    border-radius: 16px;
    padding: 20px;
}

#EssentialCard:hover, #AppItemCard:hover {
    background-color: #1C1C1E;
    border-color: #333336;
}

/* Buttons */
QPushButton {
    background-color: #252528;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2D2D32;
}

#PrimaryButton {
    background-color: #3D5AFE;
}

#PrimaryButton:hover {
    background-color: #536DFE;
}

#DangerButton {
    background: transparent;
    border: 1px solid rgba(255, 82, 82, 0.4);
    color: #FF5252;
}

#DangerButton:hover {
    background: rgba(255, 82, 82, 0.1);
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2D2D30;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #3D3D42;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
