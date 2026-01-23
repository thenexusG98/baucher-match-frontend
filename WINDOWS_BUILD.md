# 🏗️ Guía de Compilación para Windows

Esta guía explica cómo compilar BaucherMatch en Windows paso a paso.

## 📋 Requisitos Previos

### 1. Python 3.11+
```powershell
# Verificar instalación
python --version

# Debería mostrar: Python 3.11.x o superior
```

Si no está instalado, descarga desde: https://www.python.org/downloads/

### 2. Node.js 18+
```powershell
# Verificar instalación
node --version
npm --version
```

Si no está instalado, descarga desde: https://nodejs.org/

### 3. Rust y Cargo
```powershell
# Verificar instalación
rustc --version
cargo --version
```

Si no está instalado:
```powershell
# Instalar Rust desde
# https://www.rust-lang.org/tools/install

# O usando winget
winget install Rustlang.Rust.MSVC
```

### 4. Microsoft Visual Studio Build Tools

Necesario para compilar dependencias nativas de Rust:

```powershell
# Descargar e instalar desde:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# O usando winget
winget install Microsoft.VisualStudio.2022.BuildTools
```

Durante la instalación, selecciona:
- ✅ Desarrollo para el escritorio con C++
- ✅ SDK de Windows 10/11

### 5. Poppler (para pdftotext)

**Opción A: Usando conda (Recomendado)**
```powershell
conda install -c conda-forge poppler
```

**Opción B: Manual**
1. Descargar Poppler para Windows: https://github.com/oschwartz10612/poppler-windows/releases
2. Extraer a `C:\poppler`
3. Agregar `C:\poppler\Library\bin` al PATH del sistema

**Opción C: Usando chocolatey**
```powershell
choco install poppler
```

## 🔧 Pasos de Compilación

### Paso 1: Clonar el repositorio

```powershell
git clone https://github.com/thenexusG98/baucher-match-frontend.git
cd baucher-match-frontend
```

### Paso 2: Instalar dependencias de Python

```powershell
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar PyInstaller si no está
pip install pyinstaller

cd ..
```

### Paso 3: Instalar dependencias de Node.js

```powershell
npm install
```

### Paso 4: Compilar el Backend

```powershell
# Ejecutar script de compilación
.\build-backend.bat
```

Este script:
1. Verifica que Python y PyInstaller estén instalados
2. Compila el backend usando PyInstaller
3. Copia el ejecutable a `src-tauri\binaries\backend-api-x86_64-pc-windows-msvc.exe`

**Salida esperada:**
```
Compilando backend FastAPI para Windows...
Ejecutando PyInstaller...
✓ Backend compilado exitosamente!
✓ Ejecutable copiado a: src-tauri\binaries\backend-api-x86_64-pc-windows-msvc.exe
```

### Paso 5: Compilar la Aplicación Tauri

```powershell
# Compilar en modo release
npm run tauri build
```

Este comando:
1. Compila el frontend React con Vite
2. Compila el backend Rust con Cargo
3. Empaqueta todo en un instalador Windows

**Tiempo estimado:** 5-10 minutos

### Paso 6: Encontrar el Instalador

El instalador estará en:
```
src-tauri\target\release\bundle\nsis\BaucherMatch_0.1.0_x64-setup.exe
```

También se genera un archivo MSI en:
```
src-tauri\target\release\bundle\msi\BaucherMatch_0.1.0_x64_en-US.msi
```

## ✅ Verificar la Compilación

```powershell
# Verificar que el backend fue compilado
dir src-tauri\binaries\backend-api-x86_64-pc-windows-msvc.exe

# Si existe, la compilación del backend fue exitosa
```

## 🐛 Solución de Problemas

### Error: "pdftotext no encontrado"

**Síntoma:**
```
ModuleNotFoundError: No module named 'pdftotext'
```

**Solución:**
```powershell
# Instalar poppler primero
conda install -c conda-forge poppler

# Luego reinstalar pdftotext
pip uninstall pdftotext
pip install pdftotext
```

### Error: "MSVC no encontrado"

**Síntoma:**
```
error: linker `link.exe` not found
```

**Solución:**
1. Instalar Visual Studio Build Tools
2. Reiniciar PowerShell/CMD
3. Verificar: `where link.exe`

### Error: "Rust compiler not found"

**Solución:**
```powershell
# Instalar Rust
winget install Rustlang.Rust.MSVC

# Reiniciar terminal
rustc --version
```

### Error: "Node version too old"

**Solución:**
```powershell
# Actualizar Node.js
winget upgrade OpenJS.NodeJS
```

### Error: "Access denied" al compilar

**Solución:**
Ejecutar PowerShell como Administrador:
1. Botón derecho en PowerShell
2. "Ejecutar como administrador"
3. Volver a ejecutar los comandos

## 📦 Distribución

### Instalador NSIS (Recomendado)

El archivo `.exe` generado es un instalador que:
- ✅ Instala la aplicación en `C:\Program Files\BaucherMatch`
- ✅ Crea acceso directo en el menú inicio
- ✅ Incluye desinstalador
- ✅ Tamaño aproximado: 50-80 MB

### Instalador MSI

Alternativa para entornos empresariales:
- ✅ Compatible con Group Policy
- ✅ Puede desplegarse remotamente
- ✅ Registro en Windows Installer

## 🔄 Recompilar después de cambios

```powershell
# Si modificaste el backend
.\build-backend.bat

# Si modificaste el frontend
npm run tauri build

# Si modificaste ambos
.\build-backend.bat
npm run tauri build
```

## 📊 Tamaños de Archivo

| Componente | Tamaño Aproximado |
|------------|-------------------|
| Backend compilado | 15-25 MB |
| Frontend compilado | 5-10 MB |
| Instalador final | 50-80 MB |
| Aplicación instalada | 100-150 MB |

## 🎯 Compilación para Distribución

Para compilar una versión para distribuir a usuarios:

```powershell
# 1. Limpiar builds anteriores
Remove-Item -Recurse -Force src-tauri\target\release\bundle -ErrorAction SilentlyContinue

# 2. Recompilar backend limpio
cd backend
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
cd ..
.\build-backend.bat

# 3. Compilar aplicación
npm run tauri build

# 4. El instalador estará en:
dir src-tauri\target\release\bundle\nsis\*.exe
```

## 📝 Notas Adicionales

- El primer build puede tardar 10-15 minutos
- Builds subsecuentes son más rápidos (3-5 minutos)
- Se recomienda tener al menos 5 GB de espacio libre
- La compilación puede usar hasta 4 GB de RAM

## 🆘 Obtener Ayuda

Si encuentras problemas:

1. Revisa los logs en:
   ```
   %APPDATA%\BaucherMatch\logs\
   ```

2. Crea un issue en GitHub con:
   - Versión de Windows: `winver`
   - Versión de Python: `python --version`
   - Versión de Node: `node --version`
   - Versión de Rust: `rustc --version`
   - Mensaje de error completo
   - Logs de compilación

---

**Última actualización:** Enero 2026  
**Versión:** 1.0.0
