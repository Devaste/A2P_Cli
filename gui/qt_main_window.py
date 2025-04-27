import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog,
    QHBoxLayout, QLineEdit, QCheckBox, QComboBox, QMessageBox, QProgressBar, QStatusBar
)
from PyQt5.QtCore import QThread, pyqtSignal
from logic.convert import convert_avif_to_png
from logic.config import OPTIONS_DEFAULTS, METHOD_CHOICES, DITHER_CHOICES
from logic.update_check import get_local_version, get_latest_version, download_and_prepare_update
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
            convert_avif_to_png(
                input_dir=self.options.get("input_dir"),
                output_dir=self.options.get("output_dir"),
                remove=self.options.get("remove", False),
                recursive=self.options.get("recursive", False),
                qb_color=self.options.get("qb_color"),
                qb_gray_color=self.options.get("qb_gray_color"),
                qb_gray=self.options.get("qb_gray"),
                method=self.options.get("method"),
                dither=self.options.get("dither"),
                progress_callback=progress_callback
            )
            self.finished.emit("Conversion complete!")
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A2P")
        self.setMinimumSize(700, 500)
        self.options = OPTIONS_DEFAULTS.copy()
        self.thread = None
        self._setup_ui()
        self._load_gui_options()

    def _setup_ui(self):
        layout = QVBoxLayout()
        # Input Dir
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Input directory or file")
        input_btn = QPushButton("Browse...")
        input_btn.clicked.connect(self._select_input)
        input_layout.addWidget(QLabel("Input:"))
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        # Output Dir
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Output directory (optional)")
        output_btn = QPushButton("Browse...")
        output_btn.clicked.connect(self._select_output)
        output_layout.addWidget(QLabel("Output:"))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        # Options
        options_layout = QHBoxLayout()
        self.remove_chk = QCheckBox("Remove originals")
        self.recursive_chk = QCheckBox("Recursive")
        options_layout.addWidget(self.remove_chk)
        options_layout.addWidget(self.recursive_chk)
        layout.addLayout(options_layout)
        # Quantization
        quant_layout = QHBoxLayout()
        self.qb_color_edit = QLineEdit()
        self.qb_color_edit.setPlaceholderText("QB Color (1-8)")
        self.qb_gray_color_edit = QLineEdit()
        self.qb_gray_color_edit.setPlaceholderText("QB Gray+1 (1-8)")
        self.qb_gray_edit = QLineEdit()
        self.qb_gray_edit.setPlaceholderText("QB Gray (1-8)")
        quant_layout.addWidget(QLabel("Quantization:"))
        quant_layout.addWidget(self.qb_color_edit)
        quant_layout.addWidget(self.qb_gray_color_edit)
        quant_layout.addWidget(self.qb_gray_edit)
        layout.addLayout(quant_layout)
        # Method/Dither
        method_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        for k, v in METHOD_CHOICES.items():
            self.method_combo.addItem(f"{v}", k)
        self.dither_combo = QComboBox()
        for k, v in DITHER_CHOICES.items():
            self.dither_combo.addItem(f"{v}", k)
        method_layout.addWidget(QLabel("Method:"))
        method_layout.addWidget(self.method_combo)
        method_layout.addWidget(QLabel("Dither:"))
        method_layout.addWidget(self.dither_combo)
        layout.addLayout(method_layout)
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
        btn_layout.addWidget(self.convert_btn)
        btn_layout.addWidget(self.version_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # Central Widget
        central_widget = QWidget()
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
        opts["qb_color"] = self._parse_int(self.qb_color_edit.text())
        opts["qb_gray_color"] = self._parse_int(self.qb_gray_color_edit.text())
        opts["qb_gray"] = self._parse_int(self.qb_gray_edit.text())
        opts["method"] = self.method_combo.currentData()
        opts["dither"] = self.dither_combo.currentData()
        return opts

    def _parse_int(self, val):
        try:
            return int(val)
        except Exception:
            return None

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
        self.qb_color_edit.setText(str(opts.get("qb_color", "")))
        self.qb_gray_color_edit.setText(str(opts.get("qb_gray_color", "")))
        self.qb_gray_edit.setText(str(opts.get("qb_gray", "")))
        method = opts.get("method")
        dither = opts.get("dither")
        if method is not None:
            idx = self.method_combo.findData(method)
            if idx >= 0:
                self.method_combo.setCurrentIndex(idx)
        if dither is not None:
            idx = self.dither_combo.findData(dither)
            if idx >= 0:
                self.dither_combo.setCurrentIndex(idx)

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
