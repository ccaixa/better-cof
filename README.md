# BetterCof — Advanced Cry of Fear Launcher

BetterCof is an advanced Windows launcher for Cry of Fear that improves the default experience: it streamlines video/input setup, provides presets with live command preview, and can generate an optional `bc_advancedsettings.cfg` with curated cvars for visual and gameplay tweaks.

## What It Does

- Launches `cof.exe` with chosen resolution, windowed/OpenGL/16‑bit menu options, raw input, and heap size.
- Provides presets and live preview of the effective command line.
- Optionally writes `bc_advancedsettings.cfg` with a focused set of cvars, then auto‑execs it on game start.
- Saves your launcher settings in the Windows registry (`HKCU\Software\BetterCof`).

### Advanced Settings (written to `bc_advancedsettings.cfg`)

- Text and numeric: `name`, `cl_coop_language`, `gl_brightness`, `gl_contrast`, `cl_smokeparticlelimit`, `cl_noiseamount`.
- Toggles: `gl_screenblur`, `gl_bump`, `gl_specular`, `gl_highspecular`, `cg_water`, `r_weather`, `cl_ripples`, `cl_subtitles`, `cl_cheapweaponsmoke`, `cl_noiseeffect`, `cl_vignette`, `cl_propdistance`, `cl_nodoubletapdodge`, `cl_bloodeffects`, `gl_posteffects`, `cl_cameraeffect`.
- When Advanced Settings are disabled, the file is created empty (no comments or placeholder lines).

## Build (Windows)

Prerequisites:

- Python 3.8+ (64‑bit) on Windows
- `pip`

Install dependencies:

```bash
pip install -r requirements.txt
```

Build the standalone executable with PyInstaller:
```bash
pyinstaller BetterCof.spec
```

The build output is placed in `dist\BetterCof.exe`.

## Run From Source

```bash
python app.py
```

## Usage

- Browse to your Cry of Fear installation and select `cof.exe`.
- Choose resolution, windowed/OpenGL/16‑bit menu, raw input, and heap size.
- Enable Advanced Settings if you want `bc_advancedsettings.cfg` generated with the options above.
- Save or reset your launcher configuration from the Configuration tab.

## Notes

- Windows‑only (uses the Windows registry).
- Credits: developed by caixa — special thanks to ntxn.