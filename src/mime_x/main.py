import sys
import os
import subprocess
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFrame, QScrollArea, QStackedWidget, QGridLayout, QSizePolicy,
    QStyledItemDelegate, QStyle
)
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QIcon, QColor, QFont, QPixmap, QPainter, QBrush, QPen

import sys
import os

# Add current directory to path to support direct script execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mime_manager
from mime_manager import MimeManager, AppInfo
import styles
from styles import QSS

class MimeDelegate(QStyledItemDelegate):
    """High-performance delegate for the MIME list to show extensions nicely."""
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        mimetype = index.data(Qt.DisplayRole)
        extensions = index.data(Qt.UserRole) or ""
        icon = index.data(Qt.DecorationRole)
        
        # Draw background
        if option.state & QStyle.State_Selected:
            bg_color = QColor("#2D2D32")
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(option.rect.adjusted(5, 2, -5, -2), 8, 8)
            text_color = QColor("#3D5AFE")
        elif option.state & QStyle.State_MouseOver:
            bg_color = QColor("#1E1E20")
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(option.rect.adjusted(5, 2, -5, -2), 8, 8)
            text_color = QColor("#EEEEEE")
        else:
            text_color = QColor("#CCCCCC")

        # Draw Icon
        if icon:
            icon_rect = option.rect.adjusted(15, 12, -option.rect.width() + 15 + 32, -12)
            icon.paint(painter, icon_rect, Qt.AlignCenter)

        # Draw Text
        painter.setPen(QPen(text_color))
        font = painter.font()
        font.setBold(True if option.state & QStyle.State_Selected else False)
        painter.setFont(font)
        
        # Adjust text rect for icon
        text_rect = option.rect.adjusted(62, 8, -15, -8)
        painter.drawText(text_rect.adjusted(0, 0, 0, -15), Qt.AlignLeft | Qt.AlignVCenter, mimetype)
        
        if extensions:
            font.setBold(False)
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(QPen(QColor("#666666")))
            painter.drawText(text_rect.adjusted(0, 15, 0, 0), Qt.AlignLeft | Qt.AlignVCenter, extensions)
            
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 60)

class AppItemWidget(QWidget):
    def __init__(self, app: AppInfo, is_default: bool, on_set_default=None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        # Icon
        icon_label = QLabel()
        icon = QIcon.fromTheme(app.icon, QIcon.fromTheme("application-x-executable"))
        icon_label.setPixmap(icon.pixmap(32, 32))
        layout.addWidget(icon_label, 0, Qt.AlignVCenter)

        # Text
        text_w = QWidget()
        text_v = QVBoxLayout(text_w)
        text_v.setContentsMargins(0, 0, 0, 0)
        text_v.setSpacing(4)
        
        name_l = QLabel(app.name)
        name_l.setStyleSheet("font-weight: 700; font-size: 15px; color: #FFFFFF;")
        name_l.setWordWrap(True)
        text_v.addWidget(name_l)
        
        id_l = QLabel(app.desktop_id)
        id_l.setStyleSheet("font-size: 11px; color: #888888;")
        id_l.setWordWrap(True)
        text_v.addWidget(id_l)
        layout.addWidget(text_w, 1)

        if is_default:
            badge = QLabel("Default")
            badge.setStyleSheet("background: #3D5AFE; color: white; border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: 800;")
            layout.addWidget(badge, 0, Qt.AlignVCenter)
        elif on_set_default:
            btn = QPushButton("Set Default")
            btn.setObjectName("PrimaryButton")
            btn.setFixedSize(110, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: on_set_default(app.desktop_id))
            layout.addWidget(btn, 0, Qt.AlignVCenter)

class EssentialCard(QFrame):
    ICONS = {
        "Web Browser": "applications-internet",
        "PDF Reader": "application-pdf",
        "Video Player": "multimedia-video-player",
        "Music Player": "multimedia-audio-player",
        "Image Viewer": "image-viewer",
        "Text Editor": "text-editor",
        "Terminals": "utilities-terminal"
    }
    
    def __init__(self, category: str, mimetypes: List[str], manager: MimeManager, on_change=None):
        super().__init__()
        self.setObjectName("EssentialCard")
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel()
        icon_name = self.ICONS.get(category, "preferences-desktop-default-applications")
        icon = QIcon.fromTheme(icon_name, QIcon.fromTheme("folder"))
        icon_label.setPixmap(icon.pixmap(48, 48))
        main_layout.addWidget(icon_label, 0, Qt.AlignVCenter)
        
        # Info
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        cat_label = QLabel(category)
        cat_label.setStyleSheet("font-weight: 800; font-size: 18px; color: #FFFFFF;")
        layout.addWidget(cat_label)
        
        primary_mime = mimetypes[0]
        default_id = manager.get_default_app_id(primary_mime)
        
        info = QLabel()
        info.setWordWrap(True)
        if default_id:
            app = manager.apps.get(default_id)
            info.setText(f"Current: {app.name if app else default_id}")
            info.setStyleSheet("color: #3D5AFE; font-weight: 700;")
        else:
            info.setText("Not set")
            info.setStyleSheet("color: #666666;")
        layout.addWidget(info)
        
        apps = manager.get_supporting_apps(primary_mime)
        count = QLabel(f"{len(apps)} apps available")
        count.setStyleSheet("font-size: 12px; color: #555555;")
        layout.addWidget(count)
        
        main_layout.addWidget(content, 1)
        self.setCursor(Qt.PointingHandCursor)
        self.mousePressEvent = lambda e: on_change(category, mimetypes) if on_change else None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XDG MIME Manager")
        self.setMinimumSize(1000, 750)
        self.manager = MimeManager()
        self.setup_ui()
        self.switch_page(0)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Navigation
        self.sidebar = QFrame()
        self.sidebar.setObjectName("NavSidebar")
        nav_v = QVBoxLayout(self.sidebar)
        nav_v.setContentsMargins(0, 30, 0, 30)
        nav_v.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        nav_v.setSpacing(20)
        
        self.nav_btns = []
        nav_v.addWidget(self.create_nav_item("speed", "Dashboard", 0))
        nav_v.addWidget(self.create_nav_item("list", "Explorer", 1))
        nav_v.addWidget(self.create_nav_item("info", "Audit", 2))
        layout.addWidget(self.sidebar)

        # 2. Main content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.init_dashboard())
        self.stack.addWidget(self.init_explorer())
        self.stack.addWidget(self.init_audit())
        layout.addWidget(self.stack)

    def create_nav_item(self, icon_n: str, tip: str, idx: int):
        btn = QPushButton()
        btn.setObjectName("NavButton")
        btn.setFixedSize(50, 50)
        btn.setToolTip(tip)
        btn.setIcon(QIcon.fromTheme(f"view-{icon_n}-symbolic", QIcon.fromTheme("help-about")))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(lambda: self.switch_page(idx))
        self.nav_btns.append(btn)
        return btn

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        if idx == 2: self.refresh_audit()
        for i, b in enumerate(self.nav_btns):
            b.setProperty("selected", i == idx)
            b.style().polish(b)

    def init_dashboard(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(30)
        
        top = QVBoxLayout()
        t = QLabel("System Essentials")
        t.setObjectName("Title")
        top.addWidget(t)
        sub = QLabel("Configure your primary applications for daily tasks.")
        sub.setObjectName("SubTitle")
        top.addWidget(sub)
        v.addLayout(top)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.dash_grid_w = QWidget()
        self.dash_grid = QGridLayout(self.dash_grid_w)
        self.dash_grid.setSpacing(25)
        self.refresh_dashboard()
        scroll.setWidget(self.dash_grid_w)
        v.addWidget(scroll)
        return page

    def refresh_dashboard(self):
        while self.dash_grid.count():
            w = self.dash_grid.takeAt(0).widget()
            if w: w.deleteLater()
        r, c = 0, 0
        for cat, ms in self.manager.ESSENTIALS.items():
            card = EssentialCard(cat, ms, self.manager, self.on_dash_click)
            self.dash_grid.addWidget(card, r, c)
            c += 1
            if c > 2: c = 0; r += 1

    def on_dash_click(self, cat, ms):
        self.switch_page(1)
        self.search_in.setText(ms[0])

    def init_explorer(self):
        page = QWidget()
        h = QHBoxLayout(page)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        
        # List
        left = QWidget()
        left.setFixedWidth(350)
        left_v = QVBoxLayout(left)
        left_v.setContentsMargins(30, 40, 20, 20)
        left_v.setSpacing(15)
        
        lt = QLabel("All File Types")
        lt.setStyleSheet("font-weight: 800; font-size: 20px; color: #FFF;")
        left_v.addWidget(lt)
        
        self.search_in = QLineEdit()
        self.search_in.setPlaceholderText("Search types or extensions...")
        self.search_in.textChanged.connect(self.filter_list)
        left_v.addWidget(self.search_in)
        
        self.list_w = QListWidget()
        self.list_w.setItemDelegate(MimeDelegate())
        
        for m in self.manager.mime_list:
            it = QListWidgetItem(self.list_w)
            it.setData(Qt.DisplayRole, m)
            exts = self.manager.mime_to_ext.get(m, [])
            it.setData(Qt.UserRole, ", ".join(exts))
            
            # Icon fetch
            it.setData(Qt.DecorationRole, QIcon.fromTheme(m.replace("/", "-"), QIcon.fromTheme("text-x-generic")))
            
        self.list_w.currentRowChanged.connect(self.on_mime_change)
        left_v.addWidget(self.list_w)
        h.addWidget(left)
        
        # Detail
        self.detail = QFrame()
        self.detail.setObjectName("DetailPanel")
        self.detail_v = QVBoxLayout(self.detail)
        self.detail_v.setContentsMargins(40, 40, 40, 40)
        self.detail_v.setAlignment(Qt.AlignTop)
        
        self.empty_l = QLabel("Select a type to manage associations")
        self.empty_l.setStyleSheet("color: #444; font-size: 18px;")
        self.empty_l.setAlignment(Qt.AlignCenter)
        self.detail_v.addStretch()
        self.detail_v.addWidget(self.empty_l)
        self.detail_v.addStretch()
        h.addWidget(self.detail, 1)
        return page

    def filter_list(self, t):
        t = t.lower()
        for i in range(self.list_w.count()):
            it = self.list_w.item(i)
            it.setHidden(t not in it.data(Qt.DisplayRole).lower() and t not in (it.data(Qt.UserRole) or "").lower())

    def on_mime_change(self, row):
        if row < 0: return
        it = self.list_w.item(row)
        self.show_details(it.data(Qt.DisplayRole))

    def show_details(self, mime):
        while self.detail_v.count():
            w = self.detail_v.takeAt(0).widget()
            if w: w.deleteLater()
        
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 20)
        tv = QVBoxLayout()
        tl = QLabel(mime)
        tl.setObjectName("Title")
        tl.setWordWrap(True)
        tv.addWidget(tl)
        sl = QLabel("Custom associations for this type")
        sl.setObjectName("SubTitle")
        tv.addWidget(sl)
        header.addLayout(tv, 1)
        ub = QPushButton("Unset")
        ub.setObjectName("DangerButton")
        ub.setFixedWidth(100)
        ub.clicked.connect(lambda: self.do_unset(mime))
        header.addWidget(ub, 0, Qt.AlignTop)
        self.detail_v.addLayout(header)
        
        apps = self.manager.get_supporting_apps(mime)
        def_id = self.manager.get_default_app_id(mime)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scw = QWidget()
        scv = QVBoxLayout(scw)
        scv.setSpacing(10)
        
        if not apps:
            nl = QLabel("No compatible apps found.")
            nl.setStyleSheet("color: #555; font-style: italic; margin-top: 20px;")
            scv.addWidget(nl)
        else:
            for a in apps:
                card = QFrame()
                card.setObjectName("AppItemCard")
                cv = QVBoxLayout(card)
                cv.setContentsMargins(0, 0, 0, 0)
                cv.addWidget(AppItemWidget(a, a.desktop_id == def_id, lambda aid: self.do_set(mime, aid)))
                scv.addWidget(card)
        scv.addStretch()
        scroll.setWidget(scw)
        self.detail_v.addWidget(scroll)

    def do_set(self, m, aid):
        if self.manager.set_default_app(m, aid):
            self.show_details(m)
            self.refresh_dashboard()

    def do_unset(self, m):
        self.manager.unset_default(m)
        self.show_details(m)
        self.refresh_dashboard()

    def init_audit(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(30)
        
        t = QLabel("Audit & Overrides")
        t.setObjectName("Title")
        v.addWidget(t)
        sub = QLabel("Manage all manually set associations in one place.")
        sub.setObjectName("SubTitle")
        v.addWidget(sub)
        
        self.aud_scroll = QScrollArea()
        self.aud_scroll.setWidgetResizable(True)
        self.aud_scroll.setStyleSheet("background: transparent; border: none;")
        self.aud_cont = QWidget()
        self.aud_v = QVBoxLayout(self.aud_cont)
        self.aud_v.setSpacing(10)
        self.aud_v.setAlignment(Qt.AlignTop)
        self.aud_scroll.setWidget(self.aud_cont)
        v.addWidget(self.aud_scroll)
        return page

    def refresh_audit(self):
        while self.aud_v.count():
            w = self.aud_v.takeAt(0).widget()
            if w: w.deleteLater()
        os = self.manager.get_user_overrides()
        if not os:
            el = QLabel("No custom associations found.")
            el.setStyleSheet("color: #444; margin-top: 50px;")
            el.setAlignment(Qt.AlignCenter)
            self.aud_v.addWidget(el)
        else:
            for o in os:
                card = QFrame()
                card.setObjectName("AppItemCard")
                ch = QHBoxLayout(card)
                ch.setContentsMargins(15, 10, 15, 10)
                ch.setSpacing(15)
                
                # Icon
                icon_label = QLabel()
                icon = QIcon.fromTheme(o["mimetype"].replace("/", "-"), QIcon.fromTheme("text-x-generic"))
                icon_label.setPixmap(icon.pixmap(32, 32))
                ch.addWidget(icon_label, 0, Qt.AlignVCenter)
                
                lv = QVBoxLayout()
                m_l = QLabel(o["mimetype"])
                m_l.setStyleSheet("font-weight: 700; color: #FFF;")
                lv.addWidget(m_l)
                app = self.manager.apps.get(o["app_id"])
                a_l = QLabel(f"➔ {app.name if app else o['app_id']}")
                a_l.setStyleSheet("color: #3D5AFE; font-size: 13px;")
                lv.addWidget(a_l)
                ch.addLayout(lv, 1)
                
                rb = QPushButton("Reset")
                rb.setObjectName("DangerButton")
                rb.setFixedSize(80, 30)
                rb.clicked.connect(lambda m=o["mimetype"]: self.do_reset_aud(m))
                ch.addWidget(rb)
                self.aud_v.addWidget(card)
        self.aud_v.addStretch()

    def do_reset_aud(self, m):
        self.manager.unset_default(m)
        self.refresh_audit()
        self.refresh_dashboard()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    if not font.exactMatch(): font = QFont("sans-serif", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
