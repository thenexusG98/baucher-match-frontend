# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para empaquetar el backend FastAPI
"""

import sys
from pathlib import Path

block_cipher = None

# Obtener el directorio del backend
backend_dir = Path.cwd()

# Analizar el archivo principal
a = Analysis(
    ['main.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=[
        # Incluir todo el directorio app
        ('app', 'app'),
    ],
        # Incluir todo el directorio app
        ('app', 'app'),
    ],
    hiddenimports=[
        # Uvicorn y sus dependencias
        'uvicorn',
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
        'uvicorn.server',
        'uvicorn.config',
        'uvicorn.main',
        # FastAPI y dependencias
        'fastapi',
        'fastapi.routing',
        'fastapi.encoders',
        'fastapi.exceptions',
        'fastapi.dependencies',
        'fastapi.security',
        # Pydantic
        'pydantic',
        'pydantic.fields',
        'pydantic.main',
        'pydantic.types',
        'pydantic_core',
        # Starlette
        'starlette',
        'starlette.applications',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.responses',
        'starlette.requests',
        'starlette.exceptions',
        # Otros módulos necesarios
        'multipart',
        'python_multipart',
        'email.mime',
        'email.mime.multipart',
        'email.mime.text',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        'sniffio',
        'h11',
        'click',
        # PyMuPDF y pdftotext
        'fitz',
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
