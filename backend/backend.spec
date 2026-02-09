# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para empaquetar el backend FastAPI
"""

import sys
from pathlib import Path

block_cipher = None

# Obtener el directorio del backend
backend_dir = Path.cwd()

print("="*60)
print("CONFIGURANDO PYINSTALLER SPEC")
print("="*60)
print(f"Backend dir: {backend_dir}")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Intentar importar collect_all
try:
    from PyInstaller.utils.hooks import collect_all, collect_submodules
    print("[OK] PyInstaller hooks importados correctamente")
    
    # Recolectar todos los modulos
    datas = []
    binaries = []
    hiddenimports = []
    
    print("\nRecolectando paquetes...")
    for package in ['uvicorn', 'fastapi', 'starlette', 'pydantic', 'pydantic_core', 'anyio', 'h11', 'sniffio']:
        try:
            print(f"  Recolectando {package}...")
            pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
            datas += pkg_datas
            binaries += pkg_binaries
            hiddenimports += pkg_hiddenimports
            print(f"    [OK] {package}: {len(pkg_hiddenimports)} hiddenimports, {len(pkg_datas)} datas")
        except Exception as e:
            print(f"    [ERROR] Error con {package}: {e}")
            # Si falla collect_all, al menos recolectar submodulos
            try:
                submods = collect_submodules(package)
                hiddenimports += submods
                print(f"    [RETRY] Usando collect_submodules: {len(submods)} modulos")
            except:
                print(f"    [ERROR] Tambien fallo collect_submodules")
    
    # Agregar el directorio app
    datas.append(('app', 'app'))
    
    # Hiddenimports adicionales explicitos
    additional_imports = [
        'multipart', 'python_multipart', 'email.mime', 'email.mime.multipart',
        'email.mime.text', 'click', 'fitz', 'pdftotext',
        # Modulos criticos de uvicorn que a veces PyInstaller no detecta
        'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.loops.asyncio', 'uvicorn.loops.uvloop',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl', 'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.lifespan.off',
        'uvicorn.server', 'uvicorn.config', 'uvicorn.main', 'uvicorn.importer',
        'uvicorn._handlers', 'uvicorn.supervisors', 'uvicorn.supervisors.statreload',
        'uvicorn.supervisors.multiprocess', 'uvicorn.supervisors.basereload',
        # Modulos de FastAPI
        'fastapi.routing', 'fastapi.encoders', 'fastapi.exceptions',
        # Modulos ASGI de Starlette (CRITICO para servidor HTTP directo)
        'starlette.applications', 'starlette.routing', 'starlette.requests',
        'starlette.responses', 'starlette.middleware', 'starlette.middleware.cors',
        'starlette.exceptions', 'starlette.status', 'starlette.datastructures',
        'starlette.background', 'starlette.concurrency', 'starlette.types',
        # Asyncio y dependencias CRITICAS para Windows
        'asyncio', 'asyncio.runners', 'asyncio.events', 'asyncio.base_events',
        'asyncio.windows_events', 'asyncio.windows_utils',  # Especifico para Windows
        'asyncio.proactor_events', 'asyncio.selector_events',
        'asyncio.tasks', 'asyncio.coroutines', 'asyncio.futures',
        'asyncio.locks', 'asyncio.queues', 'asyncio.streams',
        'asyncio.subprocess', 'asyncio.transports', 'asyncio.protocols',
        # Selectors para I/O
        'selectors', 'select',
        # HTTP parsers
        'h11', 'h11._connection', 'h11._readers', 'h11._writers', 'h11._state',
        'httptools', 'httptools.parser', 'httptools.parser.errors',
        # Websockets
        'websockets', 'wsproto',
        # Typing extensions
        'typing_extensions',
    ]
    hiddenimports += additional_imports
    
    print(f"\nTotal hiddenimports: {len(hiddenimports)}")
    print(f"Total datas: {len(datas)}")
    print(f"Total binaries: {len(binaries)}")
    
except ImportError as e:
    print(f"[ERROR] Error importando PyInstaller hooks: {e}")
    print("Usando configuracion minima...")
    datas = [('app', 'app')]
    binaries = []
    hiddenimports = [
        'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.server',
        'uvicorn.config', 'uvicorn.main', 'fastapi', 'starlette',
        'pydantic', 'pydantic_core', 'anyio', 'h11', 'sniffio',
        'multipart', 'python_multipart', 'click', 'fitz', 'pdftotext',
    ]

print("="*60)

# Analizar el archivo principal
a = Analysis(
    ['main.py'],
    pathex=[str(backend_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    console=True,  # Cambiar a False si no quieres consola en produccion
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
