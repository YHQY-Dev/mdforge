# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for MdForge — lean bundle (Qt widgets only + markitdown PDF)."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_root = Path(SPECPATH)
src_path = project_root / "src"

block_cipher = None

# MdForge only uses QtCore / QtGui / QtWidgets — drop the rest (WebEngine ~400 MB alone).
QT_EXCLUDES = [
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtWebEngine",
    "PySide6.QtDesigner",
    "PySide6.QtDesignerComponents",
    "PySide6.QtQuick",
    "PySide6.QtQuick3D",
    "PySide6.QtQuickControls2",
    "PySide6.QtQuickWidgets",
    "PySide6.QtQml",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtLocation",
    "PySide6.QtPositioning",
    "PySide6.QtBluetooth",
    "PySide6.QtNfc",
    "PySide6.QtSensors",
    "PySide6.QtSerialPort",
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtGraphs",
    "PySide6.QtGraphsWidgets",
    "PySide6.QtRemoteObjects",
    "PySide6.QtScxml",
    "PySide6.QtStateMachine",
    "PySide6.QtWebChannel",
    "PySide6.QtWebSockets",
    "PySide6.QtHttpServer",
    "PySide6.QtNetworkAuth",
    "PySide6.QtSpatialAudio",
    "PySide6.QtTextToSpeech",
    "PySide6.Qt3DAnimation",
    "PySide6.Qt3DCore",
    "PySide6.Qt3DExtras",
    "PySide6.Qt3DInput",
    "PySide6.Qt3DLogic",
    "PySide6.Qt3DRender",
    "PySide6.QtOpenGLWidgets",
    "PySide6.QtSvgWidgets",
    "PySide6.QtHelp",
    "PySide6.QtUiTools",
    # markitdown[all] extras — not needed for PDF-only
    "speech_recognition",
    "pydub",
    "pandas",
    "openpyxl",
    "xlrd",
    "pptx",
    "mammoth",
    "olefile",
    "youtube_transcript_api",
    "azure",
    "azure.ai",
    "azure.identity",
]

BINARY_SKIP_FRAGMENTS = (
    "WebEngine",
    "Designer",
    "Quick3D",
    "Qt6Quick",
    "Qt6Qml",
    "Qt6Pdf",
    "avcodec",
    "avformat",
    "avutil",
    "swresample",
    "swscale",
    "opengl32sw",
    "Qt6Shader",
    "Qt6QuickControls2",
)

DATA_SKIP_FRAGMENTS = (
    "qtwebengine",
    "WebEngine",
    "designer",
    "quick3d",
)


def _filter_binaries(items):
    out = []
    for item in items:
        name = item[0] if item else ""
        if any(fragment in name for fragment in BINARY_SKIP_FRAGMENTS):
            continue
        out.append(item)
    return out


def _filter_datas(items):
    out = []
    for dest, src, kind in items:
        joined = f"{dest}/{src}".replace("\\", "/").lower()
        if any(fragment in joined for fragment in DATA_SKIP_FRAGMENTS):
            continue
        out.append((dest, src, kind))
    return out


hiddenimports = [
    "mdforge",
    *collect_submodules("mdforge"),
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "shiboken6",
    "httpx",
    "httpcore",
    "h11",
    "certifi",
    "idna",
    "anyio",
    "sniffio",
    "markitdown",
    "magika",
    "loguru",
    "dotenv",
]

datas = collect_data_files("markitdown")

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(src_path)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=QT_EXCLUDES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a.binaries = _filter_binaries(a.binaries)
a.datas = _filter_datas(a.datas)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MdForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MdForge",
)
