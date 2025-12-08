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

# Encontrar la ubicación de pdftotext.so en el entorno virtual
venv_path = backend_dir.parent / '.venv' / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
pdftotext_so = str(venv_path / f'pdftotext.cpython-{sys.version_info.major}{sys.version_info.minor}-darwin.so')

# Crear lista de binarios
binaries_list = []
if os.path.exists(pdftotext_so):
    binaries_list.append((pdftotext_so, '.'))
    print(f"✅ Incluyendo pdftotext desde: {pdftotext_so}")
else:
    print(f"⚠️  No se encontró pdftotext en: {pdftotext_so}")

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
