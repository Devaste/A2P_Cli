import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QGroupBox, QFileDialog, QMessageBox, QProgressBar, QStatusBar
)
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtGui import QIcon
import time
import os
from logic.convert import convert_avif_to_png
from logic.config import OPTIONS_DEFAULTS, DEFAULT_MAX_WORKERS
from logic.update_check import get_local_version, get_latest_version
from logic.options_io import save_options, load_options

class ConversionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, options):
        super().__init__()
        self.options = options

    def run(self):
        try:
            def progress_callback(current, total):
                percent = int((current / total) * 100) if total > 0 else 0
                self.progress.emit(percent)
            start_time = time.time()
            result = convert_avif_to_png(
                input_dir=self.options.get("input_dir"),
                output_dir=self.options.get("output_dir"),
                remove=self.options.get("remove", False),
                recursive=self.options.get("recursive", False),
                qb_color=self.options.get("qb_color"),
                qb_gray_color=self.options.get("qb_gray_color"),
                qb_gray=self.options.get("qb_gray"),
                method=self.options.get("method"),
                dither=self.options.get("dither"),
                max_workers=self.options.get("max_workers"),
                progress_callback=progress_callback
            )
            elapsed = time.time() - start_time
            num_files = result.get("success", 0)
            msg = f"Conversion complete in {elapsed:.2f} seconds.\n{num_files} files converted total."
            self.finished.emit(msg)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load theme from options
        opts = load_options('GUI')
        self.theme = opts.get('theme', 'light')
        self._apply_theme(self.theme)
        self.setWindowTitle("A2P")
        self.options = OPTIONS_DEFAULTS.copy()
        self.thread = None
        self._setup_ui()
        self.setFixedSize(self.sizeHint())
        # Remove status bar size grip (dotted thing in bottom right)
        self.statusBar().setSizeGripEnabled(False)
        self._load_gui_options()

    def _apply_theme(self, theme):
        qss_file = 'light-style.qss' if theme == 'light' else 'dark-style.qss'
        qss_path = os.path.join(os.path.dirname(__file__), 'resources', qss_file)
        if os.path.exists(qss_path):
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())
        self.theme = theme

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        # --- IO Section as table/grid (Bootstrap-like) ---
        io_form = QFormLayout()
        io_form.setContentsMargins(0, 0, 0, 0)
        io_form.setSpacing(4)
        # Input row
        input_field_row = QWidget()
        input_row_layout = QHBoxLayout(input_field_row)
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(2)
        self.input_edit = QLineEdit()
        input_browse = QPushButton("Browse...")
        input_browse.clicked.connect(self._select_input)
        input_row_layout.addWidget(self.input_edit, 1)
        input_row_layout.addWidget(input_browse)
        io_form.addRow(QLabel("Input:"), input_field_row)
        # Output row
        output_field_row = QWidget()
        output_row_layout = QHBoxLayout(output_field_row)
        output_row_layout.setContentsMargins(0, 0, 0, 0)
        output_row_layout.setSpacing(2)
        self.output_edit = QLineEdit()
        output_browse = QPushButton("Browse...")
        output_browse.clicked.connect(self._select_output)
        output_row_layout.addWidget(self.output_edit, 1)
        output_row_layout.addWidget(output_browse)
        io_form.addRow(QLabel("Output:"), output_field_row)
        layout.addLayout(io_form)
        # Options
        options_layout = QHBoxLayout()
        options_layout.setAlignment(Qt.AlignLeft)
        self.remove_chk = QCheckBox("Remove originals")
        self.recursive_chk = QCheckBox("Recursive")
        options_layout.addWidget(self.remove_chk)
        options_layout.addWidget(self.recursive_chk)
        layout.addLayout(options_layout)
        # --- Quantization GroupBox ---
        quant_group = QGroupBox("Quantization:")
        quant_layout = QFormLayout()
        quant_layout.setContentsMargins(8, 16, 8, 8)
        quant_choices = [("None", None)] + [(str(i), i) for i in range(1, 10)]
        # Gray
        self.qb_gray_combo = QComboBox()
        for label, value in quant_choices:
            self.qb_gray_combo.addItem(label, value)
        quant_layout.addRow(QLabel("Gray"), self.qb_gray_combo)
        # Gray+1
        self.qb_gray_color_combo = QComboBox()
        for label, value in quant_choices:
            self.qb_gray_color_combo.addItem(label, value)
        quant_layout.addRow(QLabel("Gray+1"), self.qb_gray_color_combo)
        # Color
        self.qb_color_combo = QComboBox()
        for label, value in quant_choices:
            self.qb_color_combo.addItem(label, value)
        quant_layout.addRow(QLabel("Color"), self.qb_color_combo)
        # Method (0=Median Cut, 1=Max Coverage, 2=Fast Octree)
        self.method_combo = QComboBox()
        method_choices = [("Median Cut", 0), ("Max Coverage", 1), ("Fast Octree", 2)]
        for label, value in method_choices:
            self.method_combo.addItem(label, value)
        self.method_label = QLabel("Method:")
        quant_layout.addRow(self.method_label, self.method_combo)
        # Dither (0=None, 1=Floyd-Steinberg)
        self.dither_combo = QComboBox()
        dither_choices = [("None", 0), ("Floyd-Steinberg", 1)]
        for label, value in dither_choices:
            self.dither_combo.addItem(label, value)
        self.dither_label = QLabel("Dither:")
        quant_layout.addRow(self.dither_label, self.dither_combo)
        quant_group.setLayout(quant_layout)
        layout.addWidget(quant_group)
        # --- Hide/show method/dither based on quant selection ---
        def force_resize():
            self.setMinimumSize(0, 0)
            self.resize(self.sizeHint())
            self.updateGeometry()
        def update_method_dither_visibility():
            any_qb = (
                self.qb_gray_combo.currentData() is not None or
                self.qb_gray_color_combo.currentData() is not None or
                self.qb_color_combo.currentData() is not None
            )
            self.method_label.setVisible(any_qb)
            self.method_combo.setVisible(any_qb)
            self.dither_label.setVisible(any_qb)
            self.dither_combo.setVisible(any_qb)
            force_resize()
        self.qb_gray_combo.currentIndexChanged.connect(update_method_dither_visibility)
        self.qb_gray_color_combo.currentIndexChanged.connect(update_method_dither_visibility)
        self.qb_color_combo.currentIndexChanged.connect(update_method_dither_visibility)
        update_method_dither_visibility()
        # Max Workers
        maxw_layout = QHBoxLayout()
        self.maxw_edit = QLineEdit()
        self.maxw_edit.setPlaceholderText(f"Threads (default: {DEFAULT_MAX_WORKERS})")
        maxw_layout.addWidget(QLabel("Threads:"))
        maxw_layout.addWidget(self.maxw_edit)
        layout.addLayout(maxw_layout)
        # Buttons
        btn_layout = QHBoxLayout()
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self._start_conversion)
        self.version_btn = QPushButton("Version")
        self.version_btn.clicked.connect(self._show_version)
        self.update_btn = QPushButton("Check Update")
        self.update_btn.clicked.connect(self._check_update)
        self.save_btn = QPushButton("Save Options")
        self.save_btn.clicked.connect(self._save_gui_options)
        # --- Theme Switch Button ---
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedWidth(32)
        self.theme_btn.setFixedHeight(28)
        self._update_theme_btn_icon()
        self.theme_btn.clicked.connect(self._toggle_theme)
        btn_layout.addWidget(self.convert_btn)
        btn_layout.addWidget(self.version_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.theme_btn)
        layout.addLayout(btn_layout)
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # Central Widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _select_input(self):
        path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if path:
            self.input_edit.setText(path)

    def _select_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_edit.setText(path)

    def _gather_options(self):
        opts = self.options.copy()
        opts["input_dir"] = self.input_edit.text().strip()
        opts["output_dir"] = self.output_edit.text().strip() or None
        opts["remove"] = self.remove_chk.isChecked()
        opts["recursive"] = self.recursive_chk.isChecked()
        # Quantization as int or None
        opts["qb_color"] = self.qb_color_combo.currentData()
        opts["qb_gray_color"] = self.qb_gray_color_combo.currentData()
        opts["qb_gray"] = self.qb_gray_combo.currentData()
        opts["method"] = self.method_combo.currentData()
        opts["dither"] = self.dither_combo.currentData()
        # Max workers (threads)
        try:
            mw = int(self.maxw_edit.text())
            if mw > 0:
                opts["max_workers"] = mw
            else:
                opts["max_workers"] = DEFAULT_MAX_WORKERS
        except Exception:
            opts["max_workers"] = DEFAULT_MAX_WORKERS
        return opts

    def _start_conversion(self):
        opts = self._gather_options()
        if not opts["input_dir"]:
            QMessageBox.warning(self, "Input Required", "Please select an input directory.")
            return
        self.progress.setValue(0)
        self.status_bar.showMessage("Converting...")
        self.convert_btn.setEnabled(False)
        self.thread = ConversionThread(opts)
        self.thread.finished.connect(self._on_conversion_done)
        self.thread.error.connect(self._on_conversion_error)
        self.thread.progress.connect(self._on_progress)
        self.thread.start()

    def _on_progress(self, percent):
        self.progress.setValue(percent)

    def _on_conversion_done(self, msg):
        self.progress.setValue(100)
        self.status_bar.showMessage(msg)
        QMessageBox.information(self, "Done", msg)
        self.convert_btn.setEnabled(True)

    def _on_conversion_error(self, err):
        self.status_bar.showMessage("Error: " + err)
        QMessageBox.critical(self, "Error", err)
        self.convert_btn.setEnabled(True)

    def _show_version(self):
        version = get_local_version()
        QMessageBox.information(self, "Version", f"A2P_Cli version: {version}")

    def _check_update(self):
        local = get_local_version()
        latest = get_latest_version()
        if latest == local:
            QMessageBox.information(self, "Update", f"You are running the latest version: {local}.")
        else:
            from logic.update_check import select_update_asset, get_latest_release_assets, download_and_prepare_update
            assets = get_latest_release_assets()
            asset_name, asset_url, asset_type = select_update_asset(assets)
            if not asset_url:
                QMessageBox.warning(self, "Update", "No suitable update asset found.")
                return
            reply = QMessageBox.question(self, "Update Available", f"Update available: {latest} (You have {local})\nUpdate now?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    download_and_prepare_update(asset_url=asset_url, asset_name=asset_name, asset_type=asset_type)
                    QMessageBox.information(self, "Update", "Update complete!")
                except Exception as e:
                    QMessageBox.critical(self, "Update Error", str(e))

    def _save_gui_options(self):
        opts = self._gather_options()
        opts['theme'] = self.theme
        save_options('GUI', opts)
        QMessageBox.information(self, "Saved", "Options saved to [GUI] section in options.ini.")

    def _load_gui_options(self):
        opts = load_options('GUI')
        if not opts:
            return
        # Set UI elements from loaded options
        self.input_edit.setText(opts.get("input_dir", ""))
        self.output_edit.setText(opts.get("output_dir", ""))
        self.remove_chk.setChecked(opts.get("remove", False))
        self.recursive_chk.setChecked(opts.get("recursive", False))
        # Set quantization
        self.qb_color_combo.setCurrentIndex(self.qb_color_combo.findData(opts.get("qb_color", None)))
        self.qb_gray_color_combo.setCurrentIndex(self.qb_gray_color_combo.findData(opts.get("qb_gray_color", None)))
        self.qb_gray_combo.setCurrentIndex(self.qb_gray_combo.findData(opts.get("qb_gray", None)))
        # Set method
        method = opts.get("method")
        if method is not None:
            idx = self.method_combo.findData(method)
            if idx >= 0:
                self.method_combo.setCurrentIndex(idx)
        # Set dither
        dither = opts.get("dither")
        if dither is not None:
            idx = self.dither_combo.findData(dither)
            if idx >= 0:
                self.dither_combo.setCurrentIndex(idx)
        self.maxw_edit.setText(str(opts.get("max_workers", DEFAULT_MAX_WORKERS)))
        # Set theme button state
        self._update_theme_btn_icon()

    def _update_theme_btn_icon(self):
        # Use custom SVG icons for theme button
        if self.theme == 'light':
            self.theme_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'resources', 'light-style.svg')))
            self.theme_btn.setText("")
            self.theme_btn.setToolTip("Switch to dark mode")
        else:
            self.theme_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'resources', 'dark-style.svg')))
            self.theme_btn.setText("")
            self.theme_btn.setToolTip("Switch to light mode")

    def _toggle_theme(self):
        new_theme = 'dark' if self.theme == 'light' else 'light'
        self._apply_theme(new_theme)
        self._update_theme_btn_icon()
        # Save theme to options
        opts = load_options('GUI')
        opts['theme'] = new_theme
        save_options('GUI', opts)

    def closeEvent(self, event):
        if self.thread is not None and hasattr(self.thread, "isRunning") and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        event.accept()

# Entry point for running the main window (for gui.qt_app to call)
def run_main_window():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
