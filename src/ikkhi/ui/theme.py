"""
Modern Dark-Mode Design System & Theme for Ikkhi Desktop GUI.
Implements glassmorphic obsidian aesthetics, vibrant neon accents, and curated typography.
"""

DARK_THEME_QSS = """
/* Global Base Typography & Window Canvas */
QMainWindow, QDialog, QWidget#rootWindow {
    background-color: #0b0f17;
    color: #e6edf3;
    font-family: 'Segoe UI Variable Display', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}

/* Glassmorphic Cards & Panels */
QFrame.glassCard {
    background-color: rgba(18, 24, 38, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

QFrame.glassCard:hover {
    border: 1px solid rgba(0, 229, 255, 0.3);
}

/* HUD Overlay Styles */
QFrame#hudContainer {
    background-color: rgba(11, 15, 23, 0.92);
    border: 1.5px solid rgba(0, 229, 255, 0.5);
    border-radius: 24px;
}

QFrame#hudContainer[state="listening"] {
    border: 2px solid #00e5ff;
}

QFrame#hudContainer[state="processing"] {
    border: 2px solid #a855f7;
}

QFrame#hudContainer[state="speaking"] {
    border: 2px solid #10b981;
}

/* Typography Hierarchy */
QLabel.headingLarge {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.3px;
}

QLabel.headingMedium {
    color: #f1f5f9;
    font-size: 15px;
    font-weight: 600;
}

QLabel.metricValue {
    color: #00e5ff;
    font-size: 26px;
    font-weight: 800;
}

QLabel.metricLabel {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel.subtext {
    color: #8b949e;
    font-size: 12px;
}

QLabel.badgeTag {
    background-color: rgba(0, 229, 255, 0.12);
    color: #00e5ff;
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* Buttons */
QPushButton.primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4d8, stop:1 #7209b7);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096c7, stop:1 #560bad);
}

QPushButton.secondaryButton {
    background-color: rgba(30, 41, 59, 0.7);
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton.secondaryButton:hover {
    background-color: rgba(51, 65, 85, 0.8);
    border-color: rgba(0, 229, 255, 0.4);
    color: #ffffff;
}

/* Form Inputs & Controls */
QLineEdit, QComboBox, QSpinBox {
    background-color: rgba(15, 23, 42, 0.9);
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #00e5ff;
    background-color: rgba(15, 23, 42, 1);
}

QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.08);
    background-color: #0b0f17;
    border-radius: 10px;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: rgba(15, 23, 42, 0.6);
    color: #94a3b8;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #121826;
    color: #00e5ff;
    border-bottom: 2px solid #00e5ff;
}

QTabBar::tab:hover:!selected {
    background-color: rgba(30, 41, 59, 0.7);
    color: #f1f5f9;
}

/* Data Tables */
QTableWidget {
    background-color: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    gridline-color: rgba(255, 255, 255, 0.05);
    color: #e2e8f0;
}

QHeaderView::section {
    background-color: #111827;
    color: #94a3b8;
    padding: 6px;
    font-weight: 600;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

QScrollBar:vertical {
    background: #0b0f17;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""
