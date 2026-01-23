@echo off
REM Script para compilar el backend Python con PyInstaller en Windows

echo Compilando backend FastAPI para Windows...

cd backend

REM Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no esta instalado
    exit /b 1
)

REM Verificar que PyInstaller este instalado
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

REM Crear directorio de binarios si no existe
if not exist "..\src-tauri\binaries" mkdir "..\src-tauri\binaries"

REM Limpiar builds anteriores
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Compilar con PyInstaller
echo Ejecutando PyInstaller...
pyinstaller backend.spec

REM Copiar el ejecutable al directorio de binarios
if exist "dist\backend-api.exe" (
    copy /Y "dist\backend-api.exe" "..\src-tauri\binaries\backend-api-x86_64-pc-windows-msvc.exe"
    echo.
    echo ✓ Backend compilado exitosamente!
    echo ✓ Ejecutable copiado a: src-tauri\binaries\backend-api-x86_64-pc-windows-msvc.exe
    echo.
) else (
    echo Error: No se pudo generar el ejecutable
    exit /b 1
)

cd ..
echo Compilacion completa. Ahora puedes ejecutar: npm run tauri build
