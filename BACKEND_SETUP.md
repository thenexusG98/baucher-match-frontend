# 🎯 Guía de Integración Backend - Pasos Siguientes

## ✅ Integración Completada

Tu proyecto ahora tiene el backend FastAPI completamente integrado con Tauri. Todos los archivos necesarios han sido creados y configurados.

## 📋 Antes de Empezar

### Instalar Dependencias del Backend

```bash
# Instalar poppler (requerido por pdftotext en macOS)
brew install poppler

# Instalar dependencias Python
cd backend
pip3 install -r requeriments.txt
cd ..
```

**Nota para macOS:** Si no tienes Homebrew instalado, descárgalo de https://brew.sh

**Nota para Linux:**
```bash
sudo apt-get install poppler-utils  # Ubuntu/Debian
sudo yum install poppler-utils       # CentOS/RHEL
```

**Nota para Windows:**
Descarga e instala poppler desde https://github.com/oschwartz10612/poppler-windows/releases/

## 🚀 Probar en Desarrollo

### Opción 1: Backend Standalone + Frontend Tauri (Recomendado)

**Terminal 1:**
```bash
npm run dev:backend
```

**Terminal 2:**
```bash
npm run tauri:dev
```

### Opción 2: Backend Empaquetado

```bash
# 1. Compilar backend
npm run build:backend

# 2. Iniciar Tauri (backend se inicia automáticamente)
npm run tauri:dev
```

## 📦 Compilar para Producción

### Requisitos Previos

El backend usa `pdftotext` que requiere librerías del sistema. Estas se incluirán automáticamente en el instalador final.

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install libpoppler-cpp-dev

# Fedora/RHEL
sudo dnf install poppler-cpp-devel

# Arch
sudo pacman -S poppler
```

**Windows:**
Ver instrucciones en `WINDOWS_LIBS_SETUP.md`

### Compilar Todo

```bash
npm run build:all
```

Este comando:
1. **Compila el backend** con PyInstaller → `src-tauri/binaries/backend-api-*`
2. **Copia las librerías de Poppler** → `src-tauri/libs/*.dylib` (o .so/.dll)
3. **Compila el frontend** con Vite → `dist/`
4. **Empaqueta todo** con Tauri → Instalador final

### ¿Qué incluye el instalador final?

El instalador resultante es **completamente autónomo** e incluye:

✅ **Python runtime embebido** (NO requiere Python instalado)
✅ **Todas las dependencias Python** (FastAPI, uvicorn, PyMuPDF, etc.)
✅ **Librerías del sistema** (Poppler para pdftotext)
✅ **Frontend React compilado**
✅ **Base de datos SQLite**

### El usuario final NO necesita instalar:

❌ Python
❌ pip
❌ Node.js
❌ Poppler
❌ Ninguna dependencia

**Todo está empaquetado en el instalador.**

Los instaladores estarán en:
- macOS: `src-tauri/target/release/bundle/dmg/`
- Windows: `src-tauri/target/release/bundle/msi/`
- Linux: `src-tauri/target/release/bundle/appimage/`

## 🧪 Verificar que Todo Funciona

### 1. Probar Backend Standalone

```bash
cd backend
python3 main.py
```

Abre http://127.0.0.1:8000/api/v1/health - deberías ver:
```json
{
  "status": "ok",
  "message": "Backend FastAPI está funcionando correctamente",
  "service": "baucher-match-backend"
}
```

### 2. Probar Aplicación Completa

```bash
npm run build:backend
npm run tauri:dev
```

Deberías ver:
1. 🔄 Pantalla de carga "Iniciando Baucher Match"
2. ✅ Backend se inicia automáticamente
3. 🎉 Aplicación principal se muestra

## 📁 Archivos Creados

### Backend
- ✅ `backend/main.py` - Punto de entrada
- ✅ `backend/backend.spec` - Config PyInstaller
- ✅ `backend/app/api/routes_transacciones.py` - Endpoint `/health`

### Frontend  
- ✅ `src/services/backend.ts` - Servicio de control
- ✅ `src/App.tsx` - Inicialización automática

### Tauri
- ✅ `src-tauri/src/lib.rs` - Comandos Rust
- ✅ `src-tauri/tauri.conf.json` - Config sidecar
- ✅ `src-tauri/capabilities/default.json` - Permisos

### Scripts & Docs
- ✅ `build-backend.sh` - Script de compilación
- ✅ `BACKEND_INTEGRATION.md` - Documentación completa

## 🎯 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm run dev:backend` | Backend Python en desarrollo |
| `npm run tauri:dev` | Tauri en desarrollo |
| `npm run build:backend` | Compilar backend |
| `npm run build:all` | Compilar todo y empaquetar |

## 🐛 Solución Rápida de Problemas

**"ModuleNotFoundError"**
```bash
cd backend && pip3 install -r requeriments.txt
```

**"El ejecutable no existe"**
```bash
npm run build:backend
```

**"Backend no pudo iniciarse"**
```bash
# Probar standalone
cd backend && python3 main.py

# Verificar puerto
lsof -i :8000
```

## 📚 Documentación

- `BACKEND_INTEGRATION.md` - Guía técnica completa
- `README.md` - Información general del proyecto

## 🎉 ¡Listo para Usar!

Tu aplicación ahora:
- ✅ Inicia/detiene el backend automáticamente
- ✅ Muestra pantallas de carga y error
- ✅ Maneja el ciclo de vida correctamente
- ✅ Se puede empaquetar en un instalador único
