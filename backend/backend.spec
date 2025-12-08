# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para empaquetar el backend FastAPI
"""

import sys
from pathlib import Path
import os

block_cipher = None

# Obtener el directorio del backend
backend_dir = Path.cwd()

# Encontrar la ubicación de pdftotext en el entorno virtual (multiplataforma)
import platform
venv_path = backend_dir.parent / '.venv'

# Crear lista de binarios
binaries_list = []

# Detectar sistema operativo y buscar pdftotext
system = platform.system()
if system == 'Darwin':  # macOS
    lib_path = venv_path / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
    pdftotext_so = str(lib_path / f'pdftotext.cpython-{sys.version_info.major}{sys.version_info.minor}-darwin.so')
    if os.path.exists(pdftotext_so):
        binaries_list.append((pdftotext_so, '.'))
        print(f"OK Incluyendo pdftotext desde: {pdftotext_so}")
elif system == 'Windows':  # Windows
    lib_path = venv_path / 'Lib' / 'site-packages'
    pdftotext_pyd = str(lib_path / f'pdftotext.cp{sys.version_info.major}{sys.version_info.minor}-win_amd64.pyd')
    if os.path.exists(pdftotext_pyd):
        binaries_list.append((pdftotext_pyd, '.'))
        print(f"OK Incluyendo pdftotext desde: {pdftotext_pyd}")
    else:
        print(f"WARNING No se encontro pdftotext en: {pdftotext_pyd}")
elif system == 'Linux':  # Linux
    lib_path = venv_path / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
    pdftotext_so = str(lib_path / f'pdftotext.cpython-{sys.version_info.major}{sys.version_info.minor}-x86_64-linux-gnu.so')
    if os.path.exists(pdftotext_so):
        binaries_list.append((pdftotext_so, '.'))
        print(f"OK Incluyendo pdftotext desde: {pdftotext_so}")

# Analizar el archivo principal
a = Analysis(
    ['main.py'],
    pathex=[str(backend_dir)],
    binaries=binaries_list,
    datas=[
        # Incluir todo el directorio app
        ('app', 'app'),
        # Incluir archivos de configuración si existen
        ('temp', 'temp'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'pydantic',
        'starlette',
        'fitz',  # PyMuPDF
        'multipart',
        'pdftotext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='backend-api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Cambiar a False si no quieres consola en producción
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
