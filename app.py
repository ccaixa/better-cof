# code in beta state, dont use it for production

import os
import sys
import subprocess
import math
import shlex
import winreg
import urllib.request
 
from PyQt5 import QtWidgets, QtCore, QtGui

DEFAULT_DIR = r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Cry of Fear"
BASE_RAW = "https://raw.githubusercontent.com/ccaixa/better-cof-bucket/refs/heads/main/"
RINPUT_EXE_URL = BASE_RAW + "RInput.exe"
RINPUT_DLL_URL = BASE_RAW + "RInput.dll"
REBUILTSIMON_DLL_URL = BASE_RAW + "RebuiltSimon Build 112.dll"
CRASHRPT_DLL_URL = BASE_RAW + "CrashRpt.dll"


def dir_exists(path: str) -> bool:
    return os.path.isdir(path)


def file_exists(path: str) -> bool:
    return os.path.isfile(path)


class Launcher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BetterCof – Launcher")
        self.setFixedSize(720, 900)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        self._apply_styles()
        self._set_icon()
        self._build_ui()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QtWidgets.QHBoxLayout()
        header.setSpacing(10)
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base, "Cof_simon.ico")
        icon_lbl = QtWidgets.QLabel()
        if os.path.isfile(icon_path):
            pm = QtGui.QPixmap(icon_path)
            icon_lbl.setPixmap(pm.scaled(36, 36, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        title = QtWidgets.QLabel("BetterCof")
        title.setObjectName("AppTitle")
        subtitle = QtWidgets.QLabel("Cry of Fear Launcher")
        subtitle.setObjectName("AppSubtitle")
        title_box = QtWidgets.QVBoxLayout()
        title_box.setSpacing(0)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch(1)
        root.addLayout(header)

        tabs = QtWidgets.QTabWidget()
        root.addWidget(tabs)

        tab_main = QtWidgets.QWidget()
        main_v = QtWidgets.QVBoxLayout(tab_main)

        gb_dir = QtWidgets.QGroupBox("Game Directory")
        dir_layout = QtWidgets.QHBoxLayout(gb_dir)
        self.edit_dir = QtWidgets.QLineEdit(DEFAULT_DIR)
        self.edit_dir.setPlaceholderText("Path to Cry of Fear folder")
        self.btn_browse = QtWidgets.QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.on_browse)
        dir_layout.addWidget(self.edit_dir)
        dir_layout.addWidget(self.btn_browse)
        self._apply_shadow(gb_dir)
        main_v.addWidget(gb_dir)

        gb_res = QtWidgets.QGroupBox("Resolution")
        res_grid = QtWidgets.QGridLayout(gb_res)
        self.cmb_presets = QtWidgets.QComboBox()
        self.cmb_presets.addItems([
            "600 x 400", "800 x 600", "1024 x 768", "1280 x 960",
            "1280 x 720", "1366 x 768", "1600 x 900",
            "1920 x 1080", "2560 x 1440", "3840 x 2160"
        ])
        self.cmb_presets.setCurrentText("1920 x 1080")
        self.cmb_presets.currentTextChanged.connect(self.on_preset_changed)
        res_grid.addWidget(QtWidgets.QLabel("Preset"), 0, 0)
        res_grid.addWidget(self.cmb_presets, 0, 1, 1, 2)

        self.edit_w = QtWidgets.QLineEdit("1920")
        self.edit_w.setValidator(QtGui.QIntValidator(1, 10000, self))
        self.edit_h = QtWidgets.QLineEdit("1080")
        self.edit_h.setValidator(QtGui.QIntValidator(1, 10000, self))
        res_grid.addWidget(QtWidgets.QLabel("Width"), 1, 0)
        res_grid.addWidget(self.edit_w, 1, 1)
        res_grid.addWidget(QtWidgets.QLabel("Height"), 1, 2)
        res_grid.addWidget(self.edit_h, 1, 3)

        self.chk_windowed = QtWidgets.QCheckBox("Windowed")
        self.chk_windowed.setChecked(True)
        res_grid.addWidget(self.chk_windowed, 2, 0, 1, 2)
        self._apply_shadow(gb_res)
        main_v.addWidget(gb_res)

        gb_gfx = QtWidgets.QGroupBox("Graphics")
        gfx_v = QtWidgets.QVBoxLayout(gb_gfx)
        self.chk_gl = QtWidgets.QCheckBox("Enable GL Rendering")
        self.chk_16bit = QtWidgets.QCheckBox("Enable 16-bit (BPP)")
        self.chk_gl.setEnabled(True)
        self.chk_16bit.setChecked(False)
        gfx_v.addWidget(self.chk_gl)
        gfx_v.addWidget(self.chk_16bit)
        self._apply_shadow(gb_gfx)
        main_v.addWidget(gb_gfx)

        gb_misc = QtWidgets.QGroupBox("Miscellaneous")
        misc_grid = QtWidgets.QGridLayout(gb_misc)
        misc_grid.addWidget(QtWidgets.QLabel("Heapsize"), 0, 0)
        self.spin_heap = QtWidgets.QSpinBox()
        self.spin_heap.setRange(256000, 8192000)
        self.spin_heap.setSingleStep(128000)
        self.spin_heap.setValue(1536000)
        misc_grid.addWidget(self.spin_heap, 0, 1)

        self.chk_nointro = QtWidgets.QCheckBox("No Intro Video")
        self.chk_2dmenu = QtWidgets.QCheckBox("2D Menu")
        self.chk_2dmenu.setChecked(True)
        self.chk_rawinput = QtWidgets.QCheckBox("Enable Raw Input")
        self.chk_nointro.setEnabled(False)
        self.chk_rawinput.setEnabled(True)
        misc_grid.addWidget(self.chk_nointro, 1, 0, 1, 2)
        misc_grid.addWidget(self.chk_2dmenu, 2, 0, 1, 2)
        misc_grid.addWidget(self.chk_rawinput, 3, 0, 1, 2)
        self._apply_shadow(gb_misc)
        main_v.addWidget(gb_misc)

        tools = QtWidgets.QToolBar()
        act_reset_saves = QtWidgets.QAction("Reset Saves", self)
        act_reset_stats = QtWidgets.QAction("Reset Unlocks", self)
        act_reset_saves.triggered.connect(lambda: self.on_reset(True))
        act_reset_stats.triggered.connect(lambda: self.on_reset(False))
        tools.addAction(act_reset_saves)
        tools.addAction(act_reset_stats)
        main_v.addWidget(tools)

        gb_args = QtWidgets.QGroupBox("Arguments")
        args_v = QtWidgets.QVBoxLayout(gb_args)
        self.preview_args = QtWidgets.QLineEdit()
        self.preview_args.setReadOnly(True)
        self.preview_args.setPlaceholderText("cof.exe -game cryoffear -w 1920 -h 1080 ...")
        self.edit_custom = QtWidgets.QLineEdit()
        self.edit_custom.setPlaceholderText("Custom arguments (e.g., -novid -console -someflag=value)")
        args_v.addWidget(QtWidgets.QLabel("Preview (CMD-style, no path):"))
        args_v.addWidget(self.preview_args)
        args_v.addWidget(QtWidgets.QLabel("Add custom arguments:"))
        args_v.addWidget(self.edit_custom)
        self._apply_shadow(gb_args)
        main_v.addWidget(gb_args)

        btns = QtWidgets.QHBoxLayout()
        self.btn_run = QtWidgets.QPushButton("Run")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_quit = QtWidgets.QPushButton("Quit")
        self.btn_quit.setObjectName("GhostButton")
        self.btn_run.clicked.connect(self.on_launch)
        self.btn_quit.clicked.connect(self.close)
        btns.addWidget(self.btn_run)
        btns.addWidget(self.btn_quit)
        main_v.addLayout(btns)

        tabs.addTab(tab_main, "Main")

        tab_adv = QtWidgets.QWidget()
        adv_v = QtWidgets.QVBoxLayout(tab_adv)
        self.chk_adv_enabled = QtWidgets.QCheckBox("Use advanced settings (+exec bc_advancedsettings.cfg)")
        self.chk_adv_enabled.setChecked(False)
        self.chk_adv_enabled.toggled.connect(lambda _: self._update_preview())
        adv_v.addWidget(self.chk_adv_enabled)

        adv_grid = QtWidgets.QGridLayout()
        row = 0
        adv_grid.addWidget(QtWidgets.QLabel("Co-op name"), row, 0)
        self.adv_name = QtWidgets.QLineEdit()
        adv_grid.addWidget(self.adv_name, row, 1); row += 1

        adv_grid.addWidget(QtWidgets.QLabel("Co-op language (0-7)"), row, 0)
        self.adv_language = QtWidgets.QSpinBox()
        self.adv_language.setRange(0, 7)
        adv_grid.addWidget(self.adv_language, row, 1); row += 1

        adv_grid.addWidget(QtWidgets.QLabel("Brightness boost"), row, 0)
        self.adv_brightness = QtWidgets.QDoubleSpinBox()
        self.adv_brightness.setRange(0.0, 5.0); self.adv_brightness.setSingleStep(0.1)
        adv_grid.addWidget(self.adv_brightness, row, 1); row += 1

        adv_grid.addWidget(QtWidgets.QLabel("Contrast"), row, 0)
        self.adv_contrast = QtWidgets.QDoubleSpinBox()
        self.adv_contrast.setRange(0.0, 5.0); self.adv_contrast.setSingleStep(0.1)
        adv_grid.addWidget(self.adv_contrast, row, 1); row += 1

        def add_chk(text):
            nonlocal row
            chk = QtWidgets.QCheckBox(text)
            adv_grid.addWidget(chk, row, 0, 1, 2); row += 1
            return chk
        self.adv_screenblur = add_chk("Screen blur (gl_screenblur)")
        self.adv_bump = add_chk("Bump maps (gl_bump)")
        self.adv_specular = add_chk("Specular maps (gl_specular)")
        self.adv_highspecular = add_chk("High quality specular (gl_highspecular)")
        self.adv_cg_water = add_chk("Water shader (cg_water)")
        self.adv_weather = add_chk("Weather effects (r_weather)")
        self.adv_ripples = add_chk("Water ripples (cl_ripples)")
        self.adv_subtitles = add_chk("Subtitles (cl_subtitles)")
        self.adv_cheapweaponsmoke = add_chk("Cheap gunsmoke (cl_cheapweaponsmoke)")
        self.adv_noiseeffect = add_chk("Screen grain effect (cl_noiseeffect)")
        self.adv_vignette = add_chk("Vignette effect (cl_vignette)")
        self.adv_propdistance = add_chk("Prop fade distance (cl_propdistance)")
        self.adv_nodoubletapdodge = add_chk("Double-tap dodging (cl_nodoubletapdodge)")
        self.adv_bloodeffects = add_chk("Blood particles (cl_bloodeffects)")
        self.adv_posteffects = add_chk("Black and white effect (gl_posteffects)")
        self.adv_cameraeffect = add_chk("Camera and scope effect (cl_cameraeffect)")

        adv_grid.addWidget(QtWidgets.QLabel("Max gunsmoke particles (cl_smokeparticlelimit)"), row, 0)
        self.adv_smokeparticlelimit = QtWidgets.QSpinBox(); self.adv_smokeparticlelimit.setRange(0, 10000)
        self.adv_smokeparticlelimit.setValue(100)
        adv_grid.addWidget(self.adv_smokeparticlelimit, row, 1); row += 1

        adv_grid.addWidget(QtWidgets.QLabel("Screen grain amount (0.0-1.0) (cl_noiseamount)"), row, 0)
        self.adv_noiseamount = QtWidgets.QDoubleSpinBox(); self.adv_noiseamount.setRange(0.0, 1.0)
        self.adv_noiseamount.setSingleStep(0.05); self.adv_noiseamount.setValue(0.0)
        adv_grid.addWidget(self.adv_noiseamount, row, 1); row += 1

        adv_v.addLayout(adv_grid)
        tabs.addTab(tab_adv, "Advanced Settings")

        tab_cfg = QtWidgets.QWidget()
        cfg_v = QtWidgets.QVBoxLayout(tab_cfg)
        self.btn_save_cfg = QtWidgets.QPushButton("Save launcher configuration")
        self.btn_reset_cfg = QtWidgets.QPushButton("Reset to defaults")
        self.btn_save_cfg.clicked.connect(self._save_settings)
        self.btn_reset_cfg.clicked.connect(self._reset_defaults)
        cfg_v.addWidget(self.btn_save_cfg)
        cfg_v.addWidget(self.btn_reset_cfg)
        cfg_v.addStretch(1)
        credits = QtWidgets.QLabel("developed by caixa — special thanks to ntxn")
        credits.setAlignment(QtCore.Qt.AlignRight)
        cfg_v.addWidget(credits)
        tabs.addTab(tab_cfg, "Configuration")

        tab_plugins = QtWidgets.QWidget()
        pl_v = QtWidgets.QVBoxLayout(tab_plugins)
        info = QtWidgets.QLabel("Plugins: detect, install, enable or disable.")
        pl_v.addWidget(info)
        grid = QtWidgets.QGridLayout()
        rowp = 0
        grid.addWidget(QtWidgets.QLabel("RInput"), rowp, 0)
        self.lbl_rinput_status = QtWidgets.QLabel("Status: Unknown")
        grid.addWidget(self.lbl_rinput_status, rowp, 1)
        self.btn_rinput_toggle = QtWidgets.QPushButton("Enable")
        self.btn_rinput_toggle.clicked.connect(lambda: self.on_plugin_action("rinput_toggle"))
        grid.addWidget(self.btn_rinput_toggle, rowp, 2)
        self.btn_rinput_install = QtWidgets.QPushButton("Install")
        self.btn_rinput_install.clicked.connect(lambda: self.on_plugin_action("rinput_install"))
        grid.addWidget(self.btn_rinput_install, rowp, 3); rowp += 1
        grid.addWidget(QtWidgets.QLabel("RebuiltSimon"), rowp, 0)
        self.lbl_rebuilt_status = QtWidgets.QLabel("Status: Unknown")
        grid.addWidget(self.lbl_rebuilt_status, rowp, 1)
        self.btn_rebuilt_toggle = QtWidgets.QPushButton("Enable")
        self.btn_rebuilt_toggle.clicked.connect(lambda: self.on_plugin_action("rebuilt_toggle"))
        grid.addWidget(self.btn_rebuilt_toggle, rowp, 2)
        self.btn_rebuilt_install = QtWidgets.QPushButton("Install")
        self.btn_rebuilt_install.clicked.connect(lambda: self.on_plugin_action("rebuilt_install"))
        grid.addWidget(self.btn_rebuilt_install, rowp, 3); rowp += 1
        pl_v.addLayout(grid)
        detect_all = QtWidgets.QPushButton("Detect")
        detect_all.clicked.connect(self._refresh_plugin_states)
        pl_v.addWidget(detect_all)
        pl_v.addStretch(1)
        tabs.addTab(tab_plugins, "Plugins")

        footer_container = QtWidgets.QWidget()
        footer_container.setObjectName("FooterContainer")
        footer_container.setMaximumHeight(14)
        footer = QtWidgets.QHBoxLayout(footer_container)
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(0)
        footer_lbl = QtWidgets.QLabel("BetterCof — Beta 0.1 — developed by caixa — special thanks to ntxn")
        footer_lbl.setObjectName("FooterLabel")
        footer_lbl.setAlignment(QtCore.Qt.AlignRight)
        footer.addWidget(footer_lbl)
        root.addWidget(footer_container)

        self.cmb_presets.currentTextChanged.connect(lambda _: self._update_preview())
        self.edit_w.textChanged.connect(lambda _: self._update_preview())
        self.edit_h.textChanged.connect(lambda _: self._update_preview())
        self.chk_windowed.toggled.connect(lambda _: self._update_preview())
        self.chk_2dmenu.toggled.connect(lambda _: self._update_preview())
        self.chk_16bit.toggled.connect(lambda _: self._update_preview())
        self.chk_gl.toggled.connect(lambda _: self._update_preview())
        self.chk_rawinput.toggled.connect(self.on_rawinput_toggled)
        self.chk_rawinput.toggled.connect(lambda _: self._update_preview())
        self.spin_heap.valueChanged.connect(lambda _: self._update_preview())
        self.edit_custom.textChanged.connect(lambda _: self._update_preview())

        self.adv_enabled = False
        self.adv_name.setText("")
        self.adv_language.setValue(0)
        self.adv_brightness.setValue(0.0)
        self.adv_contrast.setValue(0.0)
        for chk in [
            self.adv_screenblur, self.adv_bump, self.adv_specular, self.adv_highspecular, self.adv_cg_water,
            self.adv_weather, self.adv_ripples, self.adv_subtitles, self.adv_cheapweaponsmoke, self.adv_noiseeffect,
            self.adv_vignette, self.adv_propdistance, self.adv_nodoubletapdodge, self.adv_bloodeffects,
            self.adv_posteffects, self.adv_cameraeffect
        ]:
            chk.setChecked(False)
        self.adv_smokeparticlelimit.setValue(100)
        self.adv_noiseamount.setValue(0.0)

        self.chk_adv_enabled.setChecked(self.adv_enabled)

        self._update_preview()
        self._load_settings()
        self._update_preview()
        self._first_run_check()
        try:
            self._refresh_plugin_states()
        except Exception:
            pass

    def on_browse(self):
        start_dir = self.edit_dir.text().strip() or DEFAULT_DIR
        if not dir_exists(start_dir):
            start_dir = DEFAULT_DIR
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select cof.exe",
            start_dir,
            "Executable (*.exe)"
        )
        if fn:
            if fn.lower().endswith("cof.exe"):
                self.edit_dir.setText(os.path.dirname(fn))
            else:
                self.edit_dir.setText(os.path.dirname(fn))

    def on_preset_changed(self, text: str):
        try:
            parts = text.replace(" ", "").split("x")
            w = int(parts[0]); h = int(parts[1])
            self.edit_w.setText(str(w))
            self.edit_h.setText(str(h))
        except Exception:
            pass

    def on_launch(self):
        dir_path = self.edit_dir.text().strip() or DEFAULT_DIR
        if not dir_exists(dir_path):
            QtWidgets.QMessageBox.critical(self, "Error", "Game directory does not exist.")
            return
        cof_path = os.path.join(dir_path, "cof.exe")
        if not file_exists(cof_path):
            QtWidgets.QMessageBox.critical(self, "Error", "cof.exe not found in selected directory.")
            return
        try:
            w = int(self.edit_w.text()) if self.edit_w.text() else 1920
            h = int(self.edit_h.text()) if self.edit_h.text() else 1080
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid resolution.")
            return
        self._write_cfg(dir_path)
        self._save_settings()
        flags = self._collect_flags(w, h)
        rinput_exe = None
        for name in ("RInput.exe", "rinput.exe"):
            p = os.path.join(dir_path, name)
            if file_exists(p):
                rinput_exe = p
                break
        rinput_dll_candidates = [os.path.join(dir_path, "RInput.dll"), os.path.join(dir_path, "rinput.dll")]
        rinput_ok = bool(rinput_exe) and any(file_exists(p) for p in rinput_dll_candidates)
        args_main = [cof_path] + flags
        custom = self._parse_custom_args()
        if custom:
            args_main.extend(custom)
        try:
            subprocess.Popen(args_main, cwd=dir_path)
            if getattr(self, "pl_rinput_enabled", False) and rinput_ok:
                subprocess.Popen([rinput_exe, "cof.exe"], cwd=dir_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start the game.\n{e}")

    def on_reset(self, reset_saves: bool):
        dir_path = self.edit_dir.text().strip() or DEFAULT_DIR
        if not dir_exists(dir_path):
            QtWidgets.QMessageBox.critical(self, "Error", "Game directory does not exist.")
            return
        stats_dir = os.path.join(dir_path, "cryoffear")
        if not dir_exists(stats_dir):
            QtWidgets.QMessageBox.critical(self, "Error", "'cryoffear' folder not found.")
            return
        exe = os.path.join(stats_dir, "StatsReset.exe")
        if not file_exists(exe):
            QtWidgets.QMessageBox.critical(self, "Error", "StatsReset.exe not found.")
            return
        msg = "This will reset ALL saves." if reset_saves else "This will reset ALL unlocks/extras."
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Reset",
            msg + "\nAre you sure?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Cancel
        )
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        args = [exe, "-save" if reset_saves else "-stats"]
        try:
            subprocess.Popen(args, cwd=stats_dir)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to run StatsReset.exe.\n{e}")

    def _apply_styles(self):
        base = """
        * { font-family: 'Segoe UI', Tahoma, Arial; }
        QWidget { background-color: #0d0f12; color: #e8e8ea; }

        QLabel#AppTitle { font-size: 26px; font-weight: 700; color: #ffffff; }
        QLabel#AppSubtitle { font-size: 12px; color: #b9c0c8; }

        QGroupBox { border: 1px solid #24262b; border-radius: 10px; margin-top: 12px; background: #111318; }
        QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #85d3ff; }

        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background: #151821; border: 1px solid #2c3240; padding: 8px; border-radius: 6px; color: #e8e8ea;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border: 1px solid #57b5ff; }
        QComboBox QAbstractItemView { background: #151821; selection-background-color: #1b202b; }

        QCheckBox { spacing: 8px; }
        QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 1px solid #2c3240; background: #1a1d26; }
        QCheckBox::indicator:checked { background: #57b5ff; border-color: #57b5ff; }

        QToolBar { background: #0f1116; border: 0; padding: 6px; }
        QToolBar QToolButton { color: #e8e8ea; border: 1px solid #2c3240; background: #161923; padding: 6px 10px; border-radius: 6px; }
        QToolBar QToolButton:hover { border-color: #57b5ff; }

        QPushButton { background: #171a23; border: 1px solid #2c3240; padding: 10px 18px; border-radius: 8px; color: #e8e8ea; }
        QPushButton:hover { border-color: #57b5ff; }
        QPushButton:pressed { background: #131620; }

        QPushButton#PrimaryButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b89ff, stop:1 #2468d9);
            border: 1px solid #2b89ff; color: #ffffff; font-weight: 600;
        }
        QPushButton#PrimaryButton:hover { filter: brightness(1.06); }
        QPushButton#GhostButton { background: transparent; border: 1px solid #2c3240; color: #c7cbd2; }

        QLabel#FooterLabel { font-size: 10px; color: #8c95a0; font-weight: 400; padding: 0; margin: 0; }

        /* Tabs styling to match launcher palette */
        QTabWidget::pane { border: 1px solid #24262b; top: -1px; background: #0f1116; }
        QTabBar::tab { background: #141720; color: #c7cbd2; border: 1px solid #24262b; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
        QTabBar::tab:hover { color: #e8e8ea; border-color: #3a4152; }
        QTabBar::tab:selected { background: #171a23; color: #ffffff; border: 1px solid #2b89ff; }
        QTabBar::tab:!selected { margin-top: 2px; }
        """
        self.setStyleSheet(base)

    def _collect_flags(self, w: int, h: int):
        renderer_flag = "-gl" if self.chk_gl.isChecked() else "-hw"
        flags = [
            "-basedir", "cryoffear",
            "-game", "cryoffear",
            renderer_flag,
            "-heapsize", str(self.spin_heap.value()),
            "-w", str(w),
            "-h", str(h)
        ]
        flags.append("-windowed" if self.chk_windowed.isChecked() else "-fullscreen")
        if self.chk_2dmenu.isChecked():
            flags.append("-no3dmenu")
        flags.append("-16bpp" if self.chk_16bit.isChecked() else "-32bpp")
        if self.chk_rawinput.isChecked():
            flags.append("-noforcemparms")
        else:
            flags.append("-noforcemaccel")
        # removed -widescreen argument because it doesn't exist
        flags += ["+exec", "bc_advancedsettings.cfg"]
        return flags

    def _parse_custom_args(self):
        text = (self.edit_custom.text() or "").strip()
        if not text:
            return []
        try:
            return shlex.split(text)
        except Exception:
            return [p for p in text.split(" ") if p]

    def _update_preview(self):
        try:
            w = int(self.edit_w.text()) if self.edit_w.text() else 1920
            h = int(self.edit_h.text()) if self.edit_h.text() else 1080
        except Exception:
            w, h = 1920, 1080
        flags = self._collect_flags(w, h)
        custom = self._parse_custom_args()
        dir_path = self.edit_dir.text().strip() or DEFAULT_DIR
        targets = self._plugin_targets(dir_path)
        rinput_exe = None
        for p in targets["rinput_exe"]:
            if file_exists(p):
                rinput_exe = os.path.basename(p)
                break
        rinput_dll_present = any(file_exists(p) for p in targets["rinput_dll_candidates"])
        parts = ["cof.exe"] + flags + custom
        use_rinput = bool(getattr(self, "pl_rinput_enabled", False)) and bool(rinput_exe) and rinput_dll_present
        if use_rinput:
            parts += [rinput_exe, "cof.exe"]
        self.preview_args.setText(" ".join(parts))

    def _first_run_check(self):
        try:
            dir_path = self.edit_dir.text().strip() or DEFAULT_DIR
            if not dir_exists(dir_path) or not file_exists(os.path.join(dir_path, "cof.exe")):
                QtWidgets.QMessageBox.information(self, "First Run", "Select your Cry of Fear folder (cof.exe).")
                self.on_browse()
        except Exception:
            pass

    def on_rawinput_toggled(self, checked: bool):
        try:
            self._update_preview()
        except Exception:
            pass

    def _apply_shadow(self, widget: QtWidgets.QWidget):
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(16)
        effect.setOffset(0, 4)
        effect.setColor(QtGui.QColor(0, 0, 0, 120))
        widget.setGraphicsEffect(effect)

    def _plugin_targets(self, dir_path: str):
        addons_dir = os.path.join(dir_path, "cryoffear", "addons")
        cl_dlls_dir = os.path.join(dir_path, "cryoffear", "cl_dlls")
        return {
            "rinput_exe": [os.path.join(dir_path, "RInput.exe"), os.path.join(dir_path, "rinput.exe")],
            "rinput_dll_candidates": [
                os.path.join(dir_path, "RInput.dll"),
                os.path.join(dir_path, "rinput.dll")
            ],
            "rebuilt_dll_candidates": [
                os.path.join(addons_dir, "RebuiltSimon Build 112.dll"),
                os.path.join(addons_dir, "RebuiltSimon.dll"),
                os.path.join(addons_dir, "rebuiltsimon.dll")
            ],
            "addons_dir": addons_dir,
            "cl_dlls_dir": cl_dlls_dir,
            "crashrpt_dll": os.path.join(cl_dlls_dir, "CrashRpt.dll"),
        }

    def _safe_download(self, url: str, dest: str):
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            urllib.request.urlretrieve(url, dest)
            return True
        except Exception:
            return False

    def _refresh_plugin_states(self):
        dir_path = self.edit_dir.text().strip() or DEFAULT_DIR
        targets = self._plugin_targets(dir_path)
        rinput_exe_present = any(file_exists(p) for p in targets["rinput_exe"])
        rinput_dll_present = any(file_exists(p) for p in targets["rinput_dll_candidates"])
        rinput_installed = rinput_exe_present and rinput_dll_present
        self.lbl_rinput_status.setText("Status: Installed" if rinput_installed else "Status: Missing")
        self.btn_rinput_install.setText("Installed" if rinput_installed else "Install")
        self.btn_rinput_install.setEnabled(not rinput_installed)
        if getattr(self, "pl_rinput_enabled", False):
            self.btn_rinput_toggle.setText("Disable")
        else:
            self.btn_rinput_toggle.setText("Enable")
        os.makedirs(targets["addons_dir"], exist_ok=True)
        os.makedirs(targets["cl_dlls_dir"], exist_ok=True)
        rebuilt_present = any(file_exists(p) for p in targets["rebuilt_dll_candidates"]) or (
            dir_exists(targets["addons_dir"]) and any(
                ("rebuild" in fn.lower() and "simon" in fn.lower() and fn.lower().endswith(".dll"))
                for fn in os.listdir(targets["addons_dir"]) )
        )
        crash_present = file_exists(targets["crashrpt_dll"]) or (
            dir_exists(targets["cl_dlls_dir"]) and any(fn.lower() == "crashrpt.dll" for fn in os.listdir(targets["cl_dlls_dir"]))
        )
        rebuilt_installed = rebuilt_present and crash_present
        self.lbl_rebuilt_status.setText("Status: Installed" if rebuilt_installed else "Status: Missing")
        self.btn_rebuilt_install.setText("Installed" if rebuilt_installed else "Install")
        self.btn_rebuilt_install.setEnabled(not rebuilt_installed)
        if getattr(self, "pl_rebuilt_enabled", False):
            self.btn_rebuilt_toggle.setText("Disable")
        else:
            self.btn_rebuilt_toggle.setText("Enable")

    def on_plugin_action(self, which: str):
        dir_path = self.edit_dir.text().strip() or DEFAULT_DIR
        targets = self._plugin_targets(dir_path)
        if which == "rinput_install":
            self._safe_download(RINPUT_EXE_URL, targets["rinput_exe"][0])
            dll_dest = targets["rinput_dll_candidates"][0]
            self._safe_download(RINPUT_DLL_URL, dll_dest)
        elif which == "rebuilt_install":
            os.makedirs(targets["addons_dir"], exist_ok=True)
            os.makedirs(targets["cl_dlls_dir"], exist_ok=True)
            rebuilt_dest = os.path.join(targets["addons_dir"], "RebuiltSimon.dll")
            self._safe_download(REBUILTSIMON_DLL_URL, rebuilt_dest)
            self._safe_download(CRASHRPT_DLL_URL, targets["crashrpt_dll"])
        elif which == "rinput_toggle":
            self.pl_rinput_enabled = not getattr(self, "pl_rinput_enabled", False)
            try:
                self._save_settings()
            except Exception:
                pass
        elif which == "rebuilt_toggle":
            self.pl_rebuilt_enabled = not getattr(self, "pl_rebuilt_enabled", False)
            try:
                self._save_settings()
            except Exception:
                pass
        self._refresh_plugin_states()

    def _set_icon(self):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base, "Cof_simon.ico")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

    def _reg_path(self):
        return r"Software\\BetterCof"

    def _load_settings(self):
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._reg_path())
        except OSError:
            return
        def get(name, default, type_="str"):
            try:
                v, _ = winreg.QueryValueEx(k, name)
                if type_ == "int":
                    return int(v)
                if type_ == "bool":
                    return bool(int(v))
                if type_ == "float":
                    try:
                        return float(v)
                    except Exception:
                        return float(default)
                return str(v)
            except Exception:
                return default
        self.edit_dir.setText(get("dir", self.edit_dir.text()))
        self.edit_w.setText(str(get("w", int(self.edit_w.text()), "int")))
        self.edit_h.setText(str(get("h", int(self.edit_h.text()), "int")))
        self.chk_windowed.setChecked(get("windowed", self.chk_windowed.isChecked(), "bool"))
        self.chk_gl.setChecked(get("gl", self.chk_gl.isChecked(), "bool"))
        self.chk_16bit.setChecked(get("bpp16", self.chk_16bit.isChecked(), "bool"))
        self.chk_2dmenu.setChecked(get("menu2d", self.chk_2dmenu.isChecked(), "bool"))
        self.chk_rawinput.setChecked(get("raw", self.chk_rawinput.isChecked(), "bool"))
        self.spin_heap.setValue(get("heap", self.spin_heap.value(), "int"))
        self.edit_custom.setText(get("custom", self.edit_custom.text()))
        try:
            self.pl_rinput_enabled = get("pl_rinput", False, "bool")
            self.pl_rebuilt_enabled = get("pl_rebuilt", False, "bool")
        except Exception:
            self.pl_rinput_enabled = False
            self.pl_rebuilt_enabled = False
        self.adv_enabled = get("adv_enabled", self.adv_enabled, "bool")
        self.adv_name.setText(get("adv_name", self.adv_name.text()))
        self.adv_language.setValue(get("adv_language", self.adv_language.value() if hasattr(self.adv_language, 'value') else 0, "int"))
        self.adv_brightness.setValue(get("adv_brightness", self.adv_brightness.value(), "float"))
        self.adv_contrast.setValue(get("adv_contrast", self.adv_contrast.value(), "float"))
        self.adv_screenblur.setChecked(get("adv_screenblur", self.adv_screenblur.isChecked(), "bool"))
        self.adv_bump.setChecked(get("adv_bump", self.adv_bump.isChecked(), "bool"))
        self.adv_specular.setChecked(get("adv_specular", self.adv_specular.isChecked(), "bool"))
        self.adv_highspecular.setChecked(get("adv_highspecular", self.adv_highspecular.isChecked(), "bool"))
        self.adv_cg_water.setChecked(get("adv_cg_water", self.adv_cg_water.isChecked(), "bool"))
        self.adv_weather.setChecked(get("adv_weather", self.adv_weather.isChecked(), "bool"))
        self.adv_ripples.setChecked(get("adv_ripples", self.adv_ripples.isChecked(), "bool"))
        self.adv_subtitles.setChecked(get("adv_subtitles", self.adv_subtitles.isChecked(), "bool"))
        self.adv_cheapweaponsmoke.setChecked(get("adv_cheapweaponsmoke", self.adv_cheapweaponsmoke.isChecked(), "bool"))
        self.adv_smokeparticlelimit.setValue(get("adv_smokeparticlelimit", self.adv_smokeparticlelimit.value(), "int"))
        self.adv_noiseeffect.setChecked(get("adv_noiseeffect", self.adv_noiseeffect.isChecked(), "bool"))
        self.adv_noiseamount.setValue(get("adv_noiseamount", self.adv_noiseamount.value(), "float"))
        self.adv_vignette.setChecked(get("adv_vignette", self.adv_vignette.isChecked(), "bool"))
        self.adv_propdistance.setChecked(get("adv_propdistance", self.adv_propdistance.isChecked(), "bool"))
        self.adv_nodoubletapdodge.setChecked(get("adv_nodoubletapdodge", self.adv_nodoubletapdodge.isChecked(), "bool"))
        self.adv_bloodeffects.setChecked(get("adv_bloodeffects", self.adv_bloodeffects.isChecked(), "bool"))
        self.adv_posteffects.setChecked(get("adv_posteffects", self.adv_posteffects.isChecked(), "bool"))
        self.adv_cameraeffect.setChecked(get("adv_cameraeffect", self.adv_cameraeffect.isChecked(), "bool"))
        self.chk_adv_enabled.setChecked(self.adv_enabled)
        try:
            winreg.CloseKey(k)
        except Exception:
            pass

    def _save_settings(self):
        try:
            k = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self._reg_path())
        except Exception:
            return
        def set(name, value):
            try:
                if isinstance(value, bool):
                    winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, int(value))
                elif isinstance(value, int):
                    winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, int(value))
                else:
                    winreg.SetValueEx(k, name, 0, winreg.REG_SZ, str(value))
            except Exception:
                pass
        set("dir", self.edit_dir.text().strip())
        set("w", int(self.edit_w.text() or "1920"))
        set("h", int(self.edit_h.text() or "1080"))
        set("windowed", self.chk_windowed.isChecked())
        set("gl", self.chk_gl.isChecked())
        set("bpp16", self.chk_16bit.isChecked())
        set("menu2d", self.chk_2dmenu.isChecked())
        set("raw", self.chk_rawinput.isChecked())
        set("heap", int(self.spin_heap.value()))
        set("custom", self.edit_custom.text())
        try:
            set("pl_rinput", bool(getattr(self, "pl_rinput_enabled", False)))
            set("pl_rebuilt", bool(getattr(self, "pl_rebuilt_enabled", False)))
        except Exception:
            pass
        self.adv_enabled = bool(self.chk_adv_enabled.isChecked())
        set("adv_enabled", self.adv_enabled)
        set("adv_name", self.adv_name.text())
        set("adv_language", int(self.adv_language.value()))
        set("adv_brightness", self.adv_brightness.value())
        set("adv_contrast", self.adv_contrast.value())
        set("adv_screenblur", self.adv_screenblur.isChecked())
        set("adv_bump", self.adv_bump.isChecked())
        set("adv_specular", self.adv_specular.isChecked())
        set("adv_highspecular", self.adv_highspecular.isChecked())
        set("adv_cg_water", self.adv_cg_water.isChecked())
        set("adv_weather", self.adv_weather.isChecked())
        set("adv_ripples", self.adv_ripples.isChecked())
        set("adv_subtitles", self.adv_subtitles.isChecked())
        set("adv_cheapweaponsmoke", self.adv_cheapweaponsmoke.isChecked())
        set("adv_smokeparticlelimit", int(self.adv_smokeparticlelimit.value()))
        set("adv_noiseeffect", self.adv_noiseeffect.isChecked())
        set("adv_noiseamount", self.adv_noiseamount.value())
        set("adv_vignette", self.adv_vignette.isChecked())
        set("adv_propdistance", self.adv_propdistance.isChecked())
        set("adv_nodoubletapdodge", self.adv_nodoubletapdodge.isChecked())
        set("adv_bloodeffects", self.adv_bloodeffects.isChecked())
        set("adv_posteffects", self.adv_posteffects.isChecked())
        set("adv_cameraeffect", self.adv_cameraeffect.isChecked())
        try:
            winreg.CloseKey(k)
        except Exception:
            pass

    def _reset_defaults(self):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self._reg_path())
        except Exception:
            pass
        self.edit_dir.setText(DEFAULT_DIR)
        self.cmb_presets.setCurrentText("1920 x 1080")
        self.edit_w.setText("1920")
        self.edit_h.setText("1080")
        self.chk_windowed.setChecked(True)
        self.chk_gl.setChecked(True)
        self.chk_16bit.setChecked(False)
        self.chk_2dmenu.setChecked(True)
        self.chk_rawinput.setChecked(True)
        self.spin_heap.setValue(1536000)
        self.edit_custom.setText("")
        self.chk_adv_enabled.setChecked(False)
        self.adv_name.setText("")
        if hasattr(self.adv_language, 'setValue'):
            self.adv_language.setValue(0)
        self.adv_brightness.setValue(0.0)
        self.adv_contrast.setValue(0.0)
        for chk in [
            self.adv_screenblur, self.adv_bump, self.adv_specular, self.adv_highspecular, self.adv_cg_water,
            self.adv_weather, self.adv_ripples, self.adv_subtitles, self.adv_cheapweaponsmoke, self.adv_noiseeffect,
            self.adv_vignette, self.adv_propdistance, self.adv_nodoubletapdodge, self.adv_bloodeffects,
            self.adv_posteffects, self.adv_cameraeffect
        ]:
            chk.setChecked(False)
        self.adv_smokeparticlelimit.setValue(100)
        self.adv_noiseamount.setValue(0.0)
        self._update_preview()
        self._save_settings()

    def _write_cfg(self, dir_path: str):
        try:
            cfg_path = os.path.join(dir_path, "bc_advancedsettings.cfg")
            lines = []
            if self.chk_adv_enabled.isChecked():
                nm = (self.adv_name.text() or "").strip()
                if nm:
                    safe_nm = nm.replace('""', '\\"')
                    lines.append(f'name "{safe_nm}"')
                lines.append(f"cl_coop_language {int(self.adv_language.value())}")
                lines.append(f"gl_brightness {self.adv_brightness.value():.2f}")
                lines.append(f"gl_contrast {self.adv_contrast.value():.2f}")
                lines.append(f"gl_screenblur {1 if self.adv_screenblur.isChecked() else 0}")
                lines.append(f"gl_bump {1 if self.adv_bump.isChecked() else 0}")
                lines.append(f"gl_specular {1 if self.adv_specular.isChecked() else 0}")
                lines.append(f"gl_highspecular {1 if self.adv_highspecular.isChecked() else 0}")
                lines.append(f"cg_water {1 if self.adv_cg_water.isChecked() else 0}")
                lines.append(f"r_weather {1 if self.adv_weather.isChecked() else 0}")
                lines.append(f"cl_ripples {1 if self.adv_ripples.isChecked() else 0}")
                lines.append(f"cl_subtitles {1 if self.adv_subtitles.isChecked() else 0}")
                lines.append(f"cl_cheapweaponsmoke {1 if self.adv_cheapweaponsmoke.isChecked() else 0}")
                lines.append(f"cl_smokeparticlelimit {int(self.adv_smokeparticlelimit.value())}")
                lines.append(f"cl_noiseeffect {1 if self.adv_noiseeffect.isChecked() else 0}")
                lines.append(f"cl_noiseamount {self.adv_noiseamount.value():.2f}")
                lines.append(f"cl_vignette {1 if self.adv_vignette.isChecked() else 0}")
                lines.append(f"cl_propdistance {1 if self.adv_propdistance.isChecked() else 0}")
                lines.append(f"cl_nodoubletapdodge {1 if self.adv_nodoubletapdodge.isChecked() else 0}")
                lines.append(f"cl_bloodeffects {1 if self.adv_bloodeffects.isChecked() else 0}")
                lines.append(f"gl_posteffects {1 if self.adv_posteffects.isChecked() else 0}")
                lines.append(f"cl_cameraeffect {1 if self.adv_cameraeffect.isChecked() else 0}")
                lines.append("r_dynamic 1")
                lines.append("gl_overbright 0")
            else:
                lines = ["r_dynamic 1", "gl_overbright 0"]
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except Exception:
            pass

    def on_open_adv(self):
        dlg = AdvancedSettingsDialog(
            enabled=self.adv_enabled,
            vsync=self.adv_vsync,
            decals=self.adv_decals,
            dynamic=self.adv_dynamic,
            fps_max=self.adv_fps_max,
            parent=self
        )
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_values()
            self.adv_enabled = data["enabled"]
            self.adv_vsync = data["vsync"]
            self.adv_decals = data["decals"]
            self.adv_dynamic = data["dynamic"]
            self.adv_fps_max = data["fps_max"]
            self._save_settings()
            self._update_preview()

    def closeEvent(self, event):
        try:
            self._save_settings()
        finally:
            super().closeEvent(event)


class AdvancedSettingsDialog(QtWidgets.QDialog):
    def __init__(self, enabled, vsync, decals, dynamic, fps_max, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.setModal(True)
        v = QtWidgets.QVBoxLayout(self)
        self.chk_enabled = QtWidgets.QCheckBox("Use advanced settings (+exec bc_advancedsettings.cfg)")
        self.chk_enabled.setChecked(bool(enabled))
        self.chk_vsync = QtWidgets.QCheckBox("VSync")
        self.chk_vsync.setChecked(bool(vsync))
        self.chk_decals = QtWidgets.QCheckBox("Decals")
        self.chk_decals.setChecked(bool(decals))
        self.chk_dynamic = QtWidgets.QCheckBox("Dynamic lights")
        self.chk_dynamic.setChecked(bool(dynamic))
        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(QtWidgets.QLabel("FPS max"))
        self.spin_fps = QtWidgets.QSpinBox()
        self.spin_fps.setRange(30, 1000)
        self.spin_fps.setValue(int(fps_max))
        hl.addWidget(self.spin_fps)
        v.addWidget(self.chk_enabled)
        v.addWidget(self.chk_vsync)
        v.addWidget(self.chk_decals)
        v.addWidget(self.chk_dynamic)
        v.addLayout(hl)
        preset = QtWidgets.QPushButton("Disable Everything")
        preset.clicked.connect(self._apply_disable_all)
        v.addWidget(preset)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)

    def _apply_disable_all(self):
        self.chk_enabled.setChecked(True)
        self.chk_vsync.setChecked(False)
        self.chk_decals.setChecked(False)
        self.chk_dynamic.setChecked(False)
        self.spin_fps.setValue(120)

    def get_values(self):
        return {
            "enabled": self.chk_enabled.isChecked(),
            "vsync": self.chk_vsync.isChecked(),
            "decals": self.chk_decals.isChecked(),
            "dynamic": self.chk_dynamic.isChecked(),
            "fps_max": int(self.spin_fps.value()),
        }



def main():
    app = QtWidgets.QApplication(sys.argv)
    w = Launcher()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()