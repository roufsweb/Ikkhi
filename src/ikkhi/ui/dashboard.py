"""
Settings & Token Analytics Dashboard for Ikkhi Desktop Assistant.
Delivers real-time token economy visualization, profile inspection, and hardware controls.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QFrame, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QPushButton, QHeaderView, QMessageBox
)
from ikkhi.core.config import AppConfig
from ikkhi.core.paths import get_profiles_dir, resolve_config_path
from ikkhi.automation.profiles import ProfileManager
from ikkhi.ui.theme import DARK_THEME_QSS


class MetricCard(QFrame):
    """Visual metric display card with accent glowing value and descriptive label."""

    def __init__(self, title: str, initial_value: str, unit: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "glassCard")
        self.setObjectName("glassCard")
        self.setStyleSheet(
            "QFrame#glassCard { background-color: #0d121d; "
            "border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; }"
            "QFrame#glassCard:hover { border: 1px solid rgba(0, 229, 255, 0.35); background-color: #101624; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(4)

        self.label_title = QLabel(title.upper(), self)
        self.label_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 0.8px;")

        self.label_val = QLabel(initial_value, self)
        self.label_val.setStyleSheet("color: #00e5ff; font-family: 'JetBrains Mono', 'Segoe UI Variable', monospace; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;")

        layout.addWidget(self.label_title)
        layout.addWidget(self.label_val)

        if unit:
            self.label_unit = QLabel(unit, self)
            self.label_unit.setStyleSheet("color: #64748b; font-size: 11px;")
            layout.addWidget(self.label_unit)

    def set_value(self, val: str) -> None:
        self.label_val.setText(val)


class DashboardWindow(QMainWindow):
    """
    Main Administration and Analytics Dashboard window for Ikkhi.
    """

    config_updated = pyqtSignal(dict)

    def __init__(self, config: AppConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config = config
        self.profile_mgr = ProfileManager(config.universal_automation.profiles_directory)

        # In-memory execution analytics counters
        self.stats = {
            "fast_path_count": 0,
            "cloud_count": 0,
            "tokens_saved": 0,
            "cost_saved_usd": 0.0,
        }

        self.setWindowTitle("Ikkhi Control Panel & Token Analytics")
        self.resize(820, 580)
        self.setStyleSheet(DARK_THEME_QSS)

        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        central_widget.setObjectName("rootWindow")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(16)

        # Header bar
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        title = QLabel("IKKHI DESKTOP CONTROL PANEL", self)
        title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 800; letter-spacing: 0.5px;")

        subtitle = QLabel("ইক্ষি • Local Intelligence & Resource-Conscious Automation", self)
        subtitle.setStyleSheet("color: #00e5ff; font-size: 12px; font-weight: 600;")

        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        # Badge
        badge = QLabel("RTX 3070 CUDA • ONLINE", self)
        badge.setStyleSheet(
            "background-color: rgba(16, 185, 129, 0.15); color: #34d399; "
            "border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; "
            "padding: 4px 10px; font-size: 11px; font-weight: 700;"
        )
        header_layout.addWidget(badge)
        root_layout.addLayout(header_layout)

        # Tabs container
        self.tabs = QTabWidget(self)
        self.tabs.addTab(self._build_analytics_tab(), "⚡ Token Analytics")
        self.tabs.addTab(self._build_profiles_tab(), "📁 Adaptive Profiles")
        self.tabs.addTab(self._build_settings_tab(), "⚙️ Hardware & Settings")
        root_layout.addWidget(self.tabs)

    def _build_analytics_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(16)

        # Metric cards deck
        deck = QHBoxLayout()
        deck.setSpacing(12)

        self.card_fastpath = MetricCard("Local Fast-Path", "0", "0-token queries (<2ms)")
        self.card_cloud = MetricCard("Cloud Multimodal", "0", "Gemini 2.0 fallback")
        self.card_tokens = MetricCard("Tokens Saved", "0", "Estimated conserved")
        self.card_savings = MetricCard("Savings ($)", "$0.00", "Cloud API offset")

        deck.addWidget(self.card_fastpath)
        deck.addWidget(self.card_cloud)
        deck.addWidget(self.card_tokens)
        deck.addWidget(self.card_savings)
        layout.addLayout(deck)

        # Activity log table
        log_label = QLabel("Recent Command Execution Stream", widget)
        log_label.setStyleSheet("color: #e2e8f0; font-weight: 700; font-size: 13px;")
        layout.addWidget(log_label)

        self.history_table = QTableWidget(0, 4, widget)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Voice Utterance", "Tier / Engine", "Response / Action"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)

        return widget

    def _build_profiles_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(14)

        intro = QLabel("Learned Applications & Cached Windows UI Automation Trees", widget)
        intro.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(intro)

        # Profiles list
        self.profiles_table = QTableWidget(0, 3, widget)
        self.profiles_table.setHorizontalHeaderLabels(["App Identifier", "Learned Controls", "Last Updated"])
        self.profiles_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.profiles_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.profiles_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.profiles_table)

        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("Refresh Learned Profiles", widget)
        btn_refresh.setProperty("class", "secondaryButton")
        btn_refresh.clicked.connect(self.refresh_profiles_list)

        btn_open_folder = QPushButton("Open Storage Directory", widget)
        btn_open_folder.setProperty("class", "secondaryButton")
        btn_open_folder.clicked.connect(self._open_storage_dir)

        btn_row.addWidget(btn_refresh)
        btn_row.addWidget(btn_open_folder)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.refresh_profiles_list()
        return widget

    def _build_settings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Hotkey
        row1 = QHBoxLayout()
        lbl1 = QLabel("Push-to-Talk Hotkey:", widget)
        lbl1.setFixedWidth(160)
        self.input_hotkey = QLineEdit(self.config.audio.push_to_talk_key, widget)
        row1.addWidget(lbl1)
        row1.addWidget(self.input_hotkey)
        layout.addLayout(row1)

        # Wake-Word Phrase
        row_wake = QHBoxLayout()
        lbl_wake = QLabel("Wake-Word Phrase:", widget)
        lbl_wake.setFixedWidth(160)
        self.input_wakeword = QLineEdit(self.config.audio.wake_word, widget)
        row_wake.addWidget(lbl_wake)
        row_wake.addWidget(self.input_wakeword)
        layout.addLayout(row_wake)

        # Whisper Model
        row2 = QHBoxLayout()
        lbl2 = QLabel("Whisper STT Model:", widget)
        lbl2.setFixedWidth(160)
        self.combo_whisper = QComboBox(widget)
        self.combo_whisper.addItems(["tiny.en", "base.en", "small.en", "medium.en"])
        self.combo_whisper.setCurrentText(self.config.audio.whisper_model)
        row2.addWidget(lbl2)
        row2.addWidget(self.combo_whisper)
        layout.addLayout(row2)

        # Whisper Device
        row3 = QHBoxLayout()
        lbl3 = QLabel("Whisper Compute Device:", widget)
        lbl3.setFixedWidth(160)
        self.combo_device = QComboBox(widget)
        self.combo_device.addItems(["cuda", "cpu"])
        self.combo_device.setCurrentText(self.config.audio.whisper_device)
        row3.addWidget(lbl3)
        row3.addWidget(self.combo_device)
        layout.addLayout(row3)

        # Gemini API Key
        row4 = QHBoxLayout()
        lbl4 = QLabel("Gemini API Key:", widget)
        lbl4.setFixedWidth(160)
        self.input_apikey = QLineEdit(self.config.ai_tier.gemini_api_key, widget)
        self.input_apikey.setEchoMode(QLineEdit.EchoMode.Password)
        row4.addWidget(lbl4)
        row4.addWidget(self.input_apikey)
        layout.addLayout(row4)

        # Gemini Project ID
        row_proj = QHBoxLayout()
        lbl_proj = QLabel("Gemini Project ID:", widget)
        lbl_proj.setFixedWidth(160)
        self.input_project_id = QLineEdit(self.config.ai_tier.gemini_project_id, widget)
        row_proj.addWidget(lbl_proj)
        row_proj.addWidget(self.input_project_id)
        layout.addLayout(row_proj)

        # Proxy
        row5 = QHBoxLayout()
        lbl5 = QLabel("SOCKS5 Proxy:", widget)
        lbl5.setFixedWidth(160)
        self.input_proxy = QLineEdit(self.config.network.proxy, widget)
        row5.addWidget(lbl5)
        row5.addWidget(self.input_proxy)
        layout.addLayout(row5)

        layout.addStretch()

        btn_save = QPushButton("Save & Apply Settings", widget)
        btn_save.setProperty("class", "primaryButton")
        btn_save.clicked.connect(self._save_settings)
        layout.addWidget(btn_save)

        return widget

    def refresh_profiles_list(self) -> None:
        """Scan profiles directory and populate table."""
        profiles_dir = get_profiles_dir()
        json_files = list(profiles_dir.glob("*.json"))
        self.profiles_table.setRowCount(len(json_files))

        for idx, p in enumerate(json_files):
            try:
                prof = self.profile_mgr.get_or_create_profile(p.stem)
                self.profiles_table.setItem(idx, 0, QTableWidgetItem(prof.app_identifier))
                self.profiles_table.setItem(idx, 1, QTableWidgetItem(f"{len(prof.controls)} UI controls"))
                self.profiles_table.setItem(idx, 2, QTableWidgetItem(prof.last_updated))
            except Exception:
                self.profiles_table.setItem(idx, 0, QTableWidgetItem(p.stem))
                self.profiles_table.setItem(idx, 1, QTableWidgetItem("Unknown"))
                self.profiles_table.setItem(idx, 2, QTableWidgetItem("-"))

    def _open_storage_dir(self) -> None:
        profiles_dir = get_profiles_dir()
        os.startfile(str(profiles_dir))

    def _save_settings(self) -> None:
        """Persist modified settings back to configuration."""
        self.config.audio.push_to_talk_key = self.input_hotkey.text().strip().lower()
        self.config.audio.wake_word = self.input_wakeword.text().strip().lower()
        self.config.audio.whisper_model = self.combo_whisper.currentText()
        self.config.audio.whisper_device = self.combo_device.currentText()
        self.config.ai_tier.gemini_api_key = self.input_apikey.text().strip()
        self.config.ai_tier.gemini_project_id = self.input_project_id.text().strip()
        self.config.network.proxy = self.input_proxy.text().strip()

        QMessageBox.information(self, "Settings Saved", "Preferences have been updated successfully.")

    def log_command(self, timestamp: str, utterance: str, tier: str, response: str) -> None:
        """Add record to recent activity stream and update metric cards."""
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.history_table.setItem(row, 1, QTableWidgetItem(utterance))
        self.history_table.setItem(row, 2, QTableWidgetItem(tier))
        self.history_table.setItem(row, 3, QTableWidgetItem(response))
        self.history_table.scrollToBottom()

        if "Tier 0" in tier or "Local" in tier:
            self.stats["fast_path_count"] += 1
            # Average 1800 visual tokens saved per local match
            self.stats["tokens_saved"] += 1800
            self.stats["cost_saved_usd"] = (self.stats["tokens_saved"] / 1_000_000) * 0.10
        else:
            self.stats["cloud_count"] += 1

        self.card_fastpath.set_value(str(self.stats["fast_path_count"]))
        self.card_cloud.set_value(str(self.stats["cloud_count"]))
        self.card_tokens.set_value(f"{self.stats['tokens_saved']:,}")
        self.card_savings.set_value(f"${self.stats['cost_saved_usd']:.4f}")
