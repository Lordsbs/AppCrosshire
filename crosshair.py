import sys
import json
import os
import math
import copy
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QComboBox, QColorDialog, QFrame,
    QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QSystemTrayIcon, QMenu, QAction, QInputDialog, QMessageBox,
    QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QBrush, QPainterPath, QIcon, QPixmap
)

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE   = os.path.join(BASE_DIR, "crosshair_config.json")
PROFILES_FILE = os.path.join(BASE_DIR, "crosshair_profiles.json")

DEFAULT_CONFIG = {
    "style": "cross",
    "size": 20,
    "thickness": 2,
    "gap": 5,
    "color": "#00FF41",
    "outline_color": "#000000",
    "outline": True,
    "outline_thickness": 1,
    "dot": False,
    "dot_size": 3,
    "opacity": 255,
    "aspect_ratio": 1.0,
    "t_style": False,
    "show": True,
    "screen_index": 0,
}

STYLES = {
    "cross":        "Cruz clasica",
    "cross_short":  "Cruz corta",
    "dot":          "Solo punto",
    "circle":       "Circulo",
    "circle_cross": "Circulo + Cruz",
    "sniper":       "Francotirador",
    "chevron":      "Chevron",
    "diamond":      "Diamante",
    "square":       "Cuadrado",
    "arrow":        "Flecha",
    "ngon":         "Estrella",
    "x_cross":      "X (aspa)",
    "brackets":     "Corchetes",
}


# ─────────────────────────────────────────────────────────────────────────────
# PERSISTENCE
# ─────────────────────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def load_profiles():
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"Default": dict(DEFAULT_CONFIG)}


def save_profiles(profiles):
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# OVERLAY WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class CrosshairOverlay(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self._move_to_screen(config.get("screen_index", 0))

    def _move_to_screen(self, index):
        screens = QApplication.screens()
        index = max(0, min(index, len(screens) - 1))
        self.setGeometry(screens[index].geometry())

    def update_config(self, config):
        old_screen = self.config.get("screen_index", 0)
        self.config = config
        new_screen  = config.get("screen_index", 0)
        if old_screen != new_screen:
            self._move_to_screen(new_screen)
        self.update()

    def paintEvent(self, event):
        if not self.config.get("show", True):
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width()  // 2
        cy = self.height() // 2
        draw_crosshair(painter, cx, cy, self.config)
        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# CROSSHAIR DRAWING ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def draw_crosshair(painter, cx, cy, cfg):
    color         = QColor(cfg["color"])
    color.setAlpha(cfg.get("opacity", 255))
    outline_color = QColor(cfg.get("outline_color", "#000000"))
    outline_color.setAlpha(cfg.get("opacity", 255))

    thickness         = max(1, cfg["thickness"])
    outline_thickness = cfg.get("outline_thickness", 1)
    size              = cfg["size"]
    gap               = cfg["gap"]
    ar                = cfg.get("aspect_ratio", 1.0)
    style             = cfg["style"]
    has_outline       = cfg.get("outline", True)

    h_size = int(size * ar)
    v_size = int(size / ar) if ar else size
    h_gap  = int(gap  * ar)
    v_gap  = int(gap  / ar) if ar else gap

    def draw_line(x1, y1, x2, y2, col, w):
        pen = QPen(col, w, Qt.SolidLine, Qt.FlatCap)
        painter.setPen(pen)
        painter.drawLine(x1, y1, x2, y2)

    def fao(x1, y1, x2, y2):  # fill_and_outline
        if has_outline:
            draw_line(x1, y1, x2, y2, outline_color, thickness + outline_thickness * 2)
        draw_line(x1, y1, x2, y2, color, thickness)

    # ── Styles ────────────────────────────────────────────────────
    if style in ("cross", "cross_short", "circle_cross"):
        fao(cx - h_size, cy, cx - h_gap, cy)
        if not cfg.get("t_style", False):
            fao(cx + h_gap, cy, cx + h_size, cy)
        fao(cx, cy - v_size, cx, cy - v_gap)
        fao(cx, cy + v_gap,  cx, cy + v_size)
        if style == "circle_cross":
            r = int(size * 0.7 * ((ar + 1 / ar) / 2))
            _circle(painter, cx, cy, r, color, outline_color, thickness, outline_thickness, has_outline)

    elif style == "x_cross":
        d  = int(size * 0.7);  dg = int(gap * 0.7)
        fao(cx - d,  cy - int(d  / ar), cx - dg, cy - int(dg / ar))
        fao(cx + dg, cy + int(dg / ar), cx + d,  cy + int(d  / ar))
        if not cfg.get("t_style", False):
            fao(cx + d,  cy - int(d  / ar), cx + dg, cy - int(dg / ar))
            fao(cx - dg, cy + int(dg / ar), cx - d,  cy + int(d  / ar))

    elif style == "dot":
        pass

    elif style == "circle":
        r = int(size * ((ar + 1 / ar) / 2))
        _circle(painter, cx, cy, r, color, outline_color, thickness, outline_thickness, has_outline)

    elif style == "sniper":
        thin = max(1, thickness // 2)
        sw = painter.device().width()
        sh = painter.device().height()
        if has_outline:
            draw_line(0, cy, sw, cy, outline_color, thin + 2)
            draw_line(cx, 0, cx, sh,  outline_color, thin + 2)
        draw_line(0, cy, sw, cy, color, thin)
        draw_line(cx, 0, cx, sh,  color, thin)
        _circle(painter, cx, cy, size, color, outline_color, thickness, outline_thickness, has_outline)

    elif style == "chevron":
        pts = [(cx, cy + v_size), (cx - h_size, cy - v_size),
               (cx, cy - int(v_size * 0.4)), (cx + h_size, cy - v_size)]
        _path(painter, pts, color, outline_color, thickness, outline_thickness, has_outline)

    elif style == "diamond":
        _polygon(painter,
                 [(cx, cy - v_size), (cx + h_size, cy), (cx, cy + v_size), (cx - h_size, cy)],
                 color, outline_color, thickness, outline_thickness, has_outline)

    elif style == "square":
        combos = ([(outline_color, thickness + outline_thickness * 2)] if has_outline else []) + [(color, thickness)]
        for col, w in combos:
            painter.setPen(QPen(col, w))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(cx - h_size, cy - v_size, h_size * 2, v_size * 2)

    elif style == "arrow":
        _polygon(painter,
                 [(cx, cy - v_size), (cx + h_size, cy + v_size),
                  (cx, cy + int(v_size * 0.4)), (cx - h_size, cy + v_size)],
                 color, outline_color, thickness, outline_thickness, has_outline, filled=True)

    elif style == "ngon":
        n = 6
        pts = [(cx + int(h_size * math.cos(math.pi / n + i * 2 * math.pi / n)),
                cy + int(v_size * math.sin(math.pi / n + i * 2 * math.pi / n))) for i in range(n)]
        _polygon(painter, pts, color, outline_color, thickness, outline_thickness, has_outline)

    elif style == "brackets":
        blen = v_size
        bw   = max(4, h_size // 3)
        segs = [
            (cx - h_size, cy - blen, cx - h_size + bw, cy - blen),
            (cx - h_size, cy - blen, cx - h_size,       cy        ),
            (cx - h_size, cy,        cx - h_size + bw, cy        ),
            (cx + h_size, cy - blen, cx + h_size - bw, cy - blen),
            (cx + h_size, cy - blen, cx + h_size,       cy        ),
            (cx + h_size, cy,        cx + h_size - bw, cy        ),
            (cx - h_size, cy + blen, cx - h_size + bw, cy + blen),
            (cx - h_size, cy,        cx - h_size,       cy + blen),
            (cx + h_size, cy + blen, cx + h_size - bw, cy + blen),
            (cx + h_size, cy,        cx + h_size,       cy + blen),
        ]
        for seg in segs:
            fao(*seg)

    # Dot overlay
    if cfg.get("dot", False):
        dot_r = cfg.get("dot_size", 3)
        if has_outline:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(outline_color))
            ot = outline_thickness
            painter.drawEllipse(cx - dot_r - ot, cy - dot_r - ot,
                                (dot_r + ot) * 2, (dot_r + ot) * 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(cx - dot_r, cy - dot_r, dot_r * 2, dot_r * 2)


def _circle(painter, cx, cy, r, color, outline_color, thickness, outline_thickness, has_outline):
    if has_outline:
        painter.setPen(QPen(outline_color, thickness + outline_thickness * 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)
    painter.setPen(QPen(color, thickness))
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)


def _polygon(painter, pts, color, outline_color, thickness, outline_thickness, has_outline, filled=False):
    path = QPainterPath()
    path.moveTo(*pts[0])
    for p in pts[1:]: path.lineTo(*p)
    path.closeSubpath()
    if has_outline:
        painter.setPen(QPen(outline_color, thickness + outline_thickness * 2,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QBrush(outline_color) if filled else Qt.NoBrush)
        painter.drawPath(path)
    painter.setPen(QPen(color, thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(QBrush(color) if filled else Qt.NoBrush)
    painter.drawPath(path)


def _path(painter, pts, color, outline_color, thickness, outline_thickness, has_outline):
    path = QPainterPath()
    path.moveTo(*pts[0])
    for p in pts[1:]: path.lineTo(*p)
    if has_outline:
        painter.setPen(QPen(outline_color, thickness + outline_thickness * 2,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
    painter.setPen(QPen(color, thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)
    painter.drawPath(path)


# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW WIDGET
# ─────────────────────────────────────────────────────────────────────────────
class PreviewWidget(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setFixedSize(150, 150)
        self.setStyleSheet("background: #1a1a2e; border-radius: 8px; border: 1px solid #333;")

    def update_config(self, config):
        self.config = config
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1a1a2e"))
        painter.setPen(QPen(QColor("#2a2a4a"), 1, Qt.DotLine))
        cx, cy = self.width() // 2, self.height() // 2
        painter.drawLine(cx, 0, cx, self.height())
        painter.drawLine(0, cy, self.width(), cy)
        draw_crosshair(painter, cx, cy, self.config)
        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# PROFILES PANEL
# ─────────────────────────────────────────────────────────────────────────────
class ProfilesPanel(QWidget):
    def __init__(self, profiles, active_name, on_load, on_save_here, on_delete, on_new, parent=None):
        super().__init__(parent)
        self.profiles     = profiles
        self.active_name  = active_name
        self.on_load      = on_load
        self.on_save_here = on_save_here
        self.on_delete    = on_delete
        self.on_new       = on_new
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel("PERFILES")
        lbl.setStyleSheet("color:#9090cc; font-weight:bold; font-size:11px; letter-spacing:1px;")
        layout.addWidget(lbl)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #13132a; border: 1px solid #2a2a4a; border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px 10px; color: #c0c0e0;
                border-bottom: 1px solid #1e1e3a;
            }
            QListWidget::item:selected {
                background: #1e3a1e; color: #00FF41;
                border-left: 3px solid #00FF41;
            }
            QListWidget::item:hover { background: #1a1a3a; }
        """)
        self._refresh_list()
        layout.addWidget(self.list_widget)

        r1 = QHBoxLayout()
        b_load = QPushButton("▶  Cargar")
        b_load.setObjectName("accent")
        b_load.clicked.connect(self._load_selected)
        r1.addWidget(b_load)
        b_save = QPushButton("💾  Guardar aqui")
        b_save.clicked.connect(self._save_to_selected)
        r1.addWidget(b_save)
        layout.addLayout(r1)

        r2 = QHBoxLayout()
        b_new = QPushButton("+ Nuevo perfil")
        b_new.setObjectName("save")
        b_new.clicked.connect(self._new_profile)
        r2.addWidget(b_new)
        b_del = QPushButton("X Eliminar")
        b_del.setObjectName("danger")
        b_del.clicked.connect(self._delete_selected)
        r2.addWidget(b_del)
        layout.addLayout(r2)

    def _refresh_list(self):
        self.list_widget.clear()
        for name in self.profiles:
            star = "* " if name == self.active_name else "  "
            item = QListWidgetItem(star + name)
            self.list_widget.addItem(item)
            if name == self.active_name:
                self.list_widget.setCurrentItem(item)

    def _selected_name(self):
        item = self.list_widget.currentItem()
        return item.text().lstrip("* ").strip() if item else None

    def _load_selected(self):
        name = self._selected_name()
        if name:
            self.active_name = name
            self.on_load(name, self.profiles[name])
            self._refresh_list()

    def _save_to_selected(self):
        name = self._selected_name()
        if name:
            self.active_name = name
            self.on_save_here(name)
            self._refresh_list()

    def _new_profile(self):
        name, ok = QInputDialog.getText(self, "Nuevo perfil", "Nombre del nuevo perfil:")
        if ok and name.strip():
            name = name.strip()
            self.on_new(name)
            self.active_name = name
            self._refresh_list()

    def _delete_selected(self):
        name = self._selected_name()
        if not name:
            return
        if len(self.profiles) <= 1:
            QMessageBox.warning(self, "Eliminar", "Debe existir al menos un perfil.")
            return
        if QMessageBox.question(self, "Eliminar perfil",
                                f"Eliminar el perfil '{name}'?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.on_delete(name)
            self.active_name = list(self.profiles.keys())[0]
            self._refresh_list()

    def refresh(self, active_name):
        self.active_name = active_name
        self._refresh_list()


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class SettingsWindow(QMainWindow):
    def __init__(self, config, overlay):
        super().__init__()
        self.config         = config
        self.overlay        = overlay
        self.profiles       = load_profiles()
        self.active_profile = list(self.profiles.keys())[0]
        self.setWindowTitle("Crosshair Manager")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)
        self.setMinimumWidth(700)
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # ─── LEFT: all controls ────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(10)

        header = QLabel("CROSSHAIR OVERLAY")
        header.setStyleSheet("font-size:17px; font-weight:bold; color:#00FF41; letter-spacing:3px;")
        left.addWidget(header)

        # Preview + style group
        top = QHBoxLayout()
        self.preview = PreviewWidget(self.config)
        top.addWidget(self.preview)

        sg = QGroupBox("Estilo")
        sg_l = QVBoxLayout(sg)
        self.style_combo = QComboBox()
        for key, lbl in STYLES.items():
            self.style_combo.addItem(lbl, key)
        self.style_combo.setCurrentIndex(list(STYLES).index(self.config.get("style", "cross")))
        self.style_combo.currentIndexChanged.connect(
            lambda i: self._set("style", self.style_combo.itemData(i)))
        sg_l.addWidget(self.style_combo)

        self.t_cb = QCheckBox("Modo T (sin brazo derecho)")
        self.t_cb.setChecked(self.config.get("t_style", False))
        self.t_cb.stateChanged.connect(lambda v: self._set("t_style", bool(v)))
        sg_l.addWidget(self.t_cb)

        self.dot_cb = QCheckBox("Punto central")
        self.dot_cb.setChecked(self.config.get("dot", False))
        self.dot_cb.stateChanged.connect(lambda v: self._set("dot", bool(v)))
        sg_l.addWidget(self.dot_cb)

        dr = QHBoxLayout()
        dr.addWidget(QLabel("Tamano punto:"))
        self.dot_spin = QSpinBox()
        self.dot_spin.setRange(1, 15)
        self.dot_spin.setValue(self.config.get("dot_size", 3))
        self.dot_spin.valueChanged.connect(lambda v: self._set("dot_size", v))
        dr.addWidget(self.dot_spin)
        sg_l.addLayout(dr)
        top.addWidget(sg)
        left.addLayout(top)

        # Screen selector
        scr_g = QGroupBox("Pantalla")
        scr_l = QHBoxLayout(scr_g)
        scr_l.addWidget(QLabel("Mostrar en:"))
        self.screen_combo = QComboBox()
        self._populate_screens()
        self.screen_combo.currentIndexChanged.connect(lambda i: self._set("screen_index", i))
        scr_l.addWidget(self.screen_combo, stretch=1)
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self._repopulate_screens)
        scr_l.addWidget(refresh_btn)
        left.addWidget(scr_g)

        # Dimensions
        dim_g = QGroupBox("Dimensiones")
        dim_l = QVBoxLayout(dim_g)
        self._add_slider(dim_l, "Tamano:",      "size",      2, 80,  self.config["size"])
        self._add_slider(dim_l, "Grosor:",      "thickness", 1, 15,  self.config["thickness"])
        self._add_slider(dim_l, "Separacion:",  "gap",       0, 30,  self.config["gap"])
        self._add_slider(dim_l, "Opacidad:",    "opacity",   30, 255, self.config.get("opacity", 255))
        ar_row = QHBoxLayout()
        ar_row.addWidget(QLabel("Relacion aspecto:"))
        self.ar_spin = QDoubleSpinBox()
        self.ar_spin.setRange(0.2, 5.0); self.ar_spin.setSingleStep(0.1); self.ar_spin.setDecimals(2)
        self.ar_spin.setValue(self.config.get("aspect_ratio", 1.0))
        self.ar_spin.valueChanged.connect(lambda v: self._set("aspect_ratio", v))
        ar_row.addWidget(self.ar_spin)
        dim_l.addLayout(ar_row)
        left.addWidget(dim_g)

        # Colors
        col_g = QGroupBox("Colores")
        col_l = QHBoxLayout(col_g)
        self.color_btn = self._make_color_btn("Color principal", "color")
        col_l.addWidget(self.color_btn)
        self.outline_cb = QCheckBox("Outline")
        self.outline_cb.setChecked(self.config.get("outline", True))
        self.outline_cb.stateChanged.connect(lambda v: self._set("outline", bool(v)))
        col_l.addWidget(self.outline_cb)
        self.outline_color_btn = self._make_color_btn("Color outline", "outline_color")
        col_l.addWidget(self.outline_color_btn)
        ol_l = QVBoxLayout()
        ol_l.addWidget(QLabel("Grosor:"))
        self.ol_spin = QSpinBox()
        self.ol_spin.setRange(1, 6); self.ol_spin.setValue(self.config.get("outline_thickness", 1))
        self.ol_spin.valueChanged.connect(lambda v: self._set("outline_thickness", v))
        ol_l.addWidget(self.ol_spin)
        col_l.addLayout(ol_l)
        left.addWidget(col_g)

        # Buttons
        br = QHBoxLayout()
        self.toggle_btn = QPushButton("Ocultar crosshair" if self.config.get("show") else "Mostrar crosshair")
        self.toggle_btn.setObjectName("accent")
        self.toggle_btn.clicked.connect(self._toggle_visibility)
        br.addWidget(self.toggle_btn)
        reset_btn = QPushButton("Restablecer config")
        reset_btn.clicked.connect(self._reset)
        br.addWidget(reset_btn)
        left.addLayout(br)
        left.addStretch()

        # ─── RIGHT: profiles ───────────────────────────────────
        self.profiles_panel = ProfilesPanel(
            self.profiles, self.active_profile,
            on_load      = self._profile_load,
            on_save_here = self._profile_save,
            on_delete    = self._profile_delete,
            on_new       = self._profile_new,
        )
        self.profiles_panel.setMinimumWidth(190)
        self.profiles_panel.setMaximumWidth(230)

        root.addLayout(left, stretch=3)
        root.addWidget(self.profiles_panel, stretch=1)

    # ── Screen helpers ────────────────────────────────────────────
    def _populate_screens(self):
        current = self.config.get("screen_index", 0)
        screens = QApplication.screens()
        for i, s in enumerate(screens):
            g = s.geometry()
            name = s.name() or f"Pantalla {i+1}"
            self.screen_combo.addItem(f"{name}  [{g.width()}x{g.height()}]", i)
        self.screen_combo.setCurrentIndex(min(current, len(screens) - 1))

    def _repopulate_screens(self):
        self.screen_combo.blockSignals(True)
        self.screen_combo.clear()
        self._populate_screens()
        self.screen_combo.blockSignals(False)

    # ── Widget helpers ────────────────────────────────────────────
    def _add_slider(self, layout, label, key, lo, hi, current):
        row = QHBoxLayout()
        lbl = QLabel(label); lbl.setMinimumWidth(120)
        row.addWidget(lbl)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(lo, hi); slider.setValue(current)
        val_lbl = QLabel(str(current)); val_lbl.setMinimumWidth(32)
        def on_change(v, k=key, vl=val_lbl):
            vl.setText(str(v)); self._set(k, v)
        slider.valueChanged.connect(on_change)
        row.addWidget(slider); row.addWidget(val_lbl)
        layout.addLayout(row)

    def _make_color_btn(self, label, key):
        btn = QPushButton(label); btn.setFixedHeight(34)
        self._update_color_btn(btn, self.config.get(key, "#00FF41"))
        def pick(k=key, b=btn):
            c = QColorDialog.getColor(QColor(self.config[k]), self, label)
            if c.isValid():
                self.config[k] = c.name()
                self._update_color_btn(b, c.name())
                self._refresh()
        btn.clicked.connect(pick)
        return btn

    @staticmethod
    def _update_color_btn(btn, hex_color):
        c = QColor(hex_color)
        bright = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000 > 128
        btn.setStyleSheet(
            f"background-color:{hex_color}; color:{'#000' if bright else '#fff'};"
            "border-radius:4px; font-weight:bold;")

    def _set(self, key, value):
        self.config[key] = value
        self._refresh()

    def _refresh(self):
        self.preview.update_config(self.config)
        self.overlay.update_config(self.config)

    def _toggle_visibility(self):
        vis = not self.config.get("show", True)
        self._set("show", vis)
        self.toggle_btn.setText("Ocultar crosshair" if vis else "Mostrar crosshair")

    def _reset(self):
        screen = self.config.get("screen_index", 0)
        self.config.update(DEFAULT_CONFIG)
        self.config["screen_index"] = screen
        self._rebuild()

    def _rebuild(self):
        self.close()
        win = SettingsWindow(self.config, self.overlay)
        win.show()

    # ── Profile callbacks ─────────────────────────────────────────
    def _profile_load(self, name, profile_cfg):
        screen = self.config.get("screen_index", 0)
        self.config.update(copy.deepcopy(profile_cfg))
        self.config["screen_index"] = screen
        self.active_profile = name
        self._refresh()
        self.close()
        win = SettingsWindow(self.config, self.overlay)
        win.active_profile = name
        win.profiles_panel.refresh(name)
        win.show()

    def _profile_save(self, name):
        self.profiles[name] = copy.deepcopy(self.config)
        save_profiles(self.profiles)
        self.active_profile = name

    def _profile_new(self, name):
        self.profiles[name] = copy.deepcopy(self.config)
        save_profiles(self.profiles)
        self.active_profile = name

    def _profile_delete(self, name):
        if name in self.profiles:
            del self.profiles[name]
            save_profiles(self.profiles)

    def closeEvent(self, event):
        save_config(self.config)
        super().closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
DARK_STYLE = """
QWidget {
    background-color: #0f0f1a; color: #e0e0e0;
    font-family: 'Segoe UI', Consolas, monospace; font-size: 12px;
}
QGroupBox {
    border: 1px solid #2a2a4a; border-radius: 6px;
    margin-top: 8px; padding-top: 8px;
    font-weight: bold; color: #9090cc;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QSlider::groove:horizontal { height: 4px; background: #2a2a4a; border-radius: 2px; }
QSlider::handle:horizontal {
    background: #00FF41; border: none;
    width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
}
QSlider::sub-page:horizontal { background: #00AA2F; border-radius: 2px; }
QPushButton {
    background-color: #1e1e3a; color: #c0c0e0;
    border: 1px solid #3a3a5a; border-radius: 5px;
    padding: 6px 12px; font-weight: bold;
}
QPushButton:hover { background-color: #2a2a4a; border-color: #5a5aaa; }
QPushButton#accent { background-color: #003a1a; color: #00FF41; border-color: #00AA2F; }
QPushButton#accent:hover { background-color: #004a22; }
QPushButton#save { background-color: #1a1a4a; color: #7080ff; border-color: #4050cc; }
QPushButton#save:hover { background-color: #2a2a5a; }
QPushButton#danger { background-color: #3a1010; color: #ff6060; border-color: #aa2020; }
QPushButton#danger:hover { background-color: #4a1818; }
QComboBox {
    background-color: #1e1e3a; border: 1px solid #3a3a5a;
    border-radius: 4px; padding: 5px 10px; color: #e0e0e0;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background: #1e1e3a; selection-background-color: #2a3a2a; }
QSpinBox, QDoubleSpinBox {
    background-color: #1e1e3a; border: 1px solid #3a3a5a;
    border-radius: 4px; padding: 4px 8px; color: #e0e0e0;
}
QCheckBox { color: #c0c0e0; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border-radius: 3px;
    border: 1px solid #3a3a5a; background: #1e1e3a;
}
QCheckBox::indicator:checked { background: #00AA2F; border-color: #00FF41; }
QLabel { color: #c0c0e0; }
"""


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config  = load_config()
    overlay = CrosshairOverlay(config)
    overlay.show()

    settings = SettingsWindow(config, overlay)
    settings.show()

    # Tray icon
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor("#00FF41"), 2))
    p.drawLine(16, 4, 16, 28); p.drawLine(4, 16, 28, 16)
    p.drawEllipse(12, 12, 8, 8)
    p.end()

    tray = QSystemTrayIcon(QIcon(px), app)
    tray.setToolTip("Crosshair Overlay")
    menu = QMenu()
    a_settings = QAction("Configuracion", app)
    a_settings.triggered.connect(lambda: (settings.show(), settings.raise_()))
    a_toggle = QAction("Mostrar/Ocultar", app)
    a_toggle.triggered.connect(lambda: (
        config.__setitem__("show", not config.get("show", True)),
        overlay.update_config(config)
    ))
    a_quit = QAction("Salir", app)
    a_quit.triggered.connect(app.quit)
    menu.addAction(a_settings)
    menu.addAction(a_toggle)
    menu.addSeparator()
    menu.addAction(a_quit)
    tray.setContextMenu(menu)
    tray.show()
    tray.activated.connect(
        lambda r: (settings.show(), settings.raise_())
        if r == QSystemTrayIcon.DoubleClick else None
    )

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
