"""
Modern Dark-Mode Design System & Theme for Ikkhi Desktop GUI.
Implements glassmorphic obsidian aesthetics, vibrant neon accents, and curated typography.
"""

DARK_THEME_QSS = """
/* Global Base Typography & Window Canvas (Obsidian Layer 0) */
QMainWindow, QDialog, QWidget#rootWindow {
    background-color: #07090e;
    color: #f8fafc;
    font-family: 'Segoe UI Variable Display', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

/* Cloudflare & Apple Inspired Glassmorphic Cards (Layer 1) */
QFrame.glassCard {
    background-color: #0d121d;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

QFrame.glassCard:hover {
    border: 1px solid rgba(0, 229, 255, 0.28);
    background-color: #101624;
}

/* Apple & OpenClaw Inspired Companion HUD Pill */
QFrame#hudContainer {
    background-color: rgba(11, 15, 25, 0.94);
    border: 1.5px solid rgba(0, 229, 255, 0.45);
    border-radius: 27px;
}

QFrame#hudContainer[state="listening"] {
    border: 2px solid #00e5ff;
    background-color: rgba(11, 22, 38, 0.96);
}

QFrame#hudContainer[state="processing"] {
    border: 2px solid #a855f7;
    background-color: rgba(22, 12, 36, 0.96);
}

QFrame#hudContainer[state="speaking"] {
    border: 2px solid #10b981;
    background-color: rgba(8, 28, 22, 0.96);
}

/* Typography Hierarchy */
QLabel.headingLarge {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.4px;
}

QLabel.headingMedium {
    color: #f1f5f9;
    font-size: 14px;
    font-weight: 600;
}

QLabel.metricValue {
    color: #00e5ff;
    font-family: 'JetBrains Mono', 'Segoe UI Variable', monospace;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

QLabel.metricLabel {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

QLabel.subtext {
    color: #94a3b8;
    font-size: 12px;
}

/* Tactile Keycap Badges (<kbd>) */
QLabel.badgeTag, QLabel.keycapBadge {
    background-color: rgba(255, 255, 255, 0.06);
    color: #38bdf8;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 3px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
}

/* Buttons (Apple & Linear inspired) */
QPushButton.primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4d8, stop:1 #7928ca);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096c7, stop:1 #6b21a8);
    border-color: rgba(0, 229, 255, 0.6);
}

QPushButton.secondaryButton {
    background-color: rgba(255, 255, 255, 0.04);
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton.secondaryButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.20);
    color: #ffffff;
}

/* Form Inputs & Controls */
QLineEdit, QComboBox, QSpinBox {
    background-color: #0b0f19;
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #00e5ff;
    background-color: #0e1422;
}

QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.08);
    background-color: #07090e;
    border-radius: 10px;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: rgba(13, 18, 29, 0.7);
    color: #64748b;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 22px;
    font-weight: 600;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #0d121d;
    color: #00e5ff;
    border-bottom: 2px solid #00e5ff;
}

QTabBar::tab:hover:!selected {
    background-color: rgba(255, 255, 255, 0.04);
    color: #cbd5e1;
}

/* Cloudflare-Style Telemetry Table */
QTableWidget {
    background-color: #0a0e17;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    gridline-color: rgba(255, 255, 255, 0.04);
    color: #e2e8f0;
    font-family: 'Segoe UI Variable', sans-serif;
    selection-background-color: rgba(0, 229, 255, 0.15);
}

QTableWidget::item {
    padding: 8px 12px;
}

QTableWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.03);
}

QHeaderView::section {
    background-color: #0d121d;
    color: #64748b;
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

QScrollBar:vertical {
    background: #07090e;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #1e293b;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #334155;
}
"""
