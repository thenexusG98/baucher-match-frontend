# 🐛 Guía de Debugging en Producción

Esta guía explica cómo diagnosticar y solucionar errores en la aplicación BaucherMatch cuando está compilada y empaquetada.

## 📍 Ubicación de Archivos de Log

### macOS

**Frontend (Tauri):**
```
~/Library/Logs/BaucherMatch/tauri_YYYYMMDD.log
```

**Backend (FastAPI):**
```
~/Library/Logs/BaucherMatch/backend_YYYYMMDD.log
```

Ejemplo:
```bash
# Ver logs del frontend
cat ~/Library/Logs/BaucherMatch/tauri_20260123.log

# Ver logs del backend
cat ~/Library/Logs/BaucherMatch/backend_20260123.log

# Ver logs en tiempo real
tail -f ~/Library/Logs/BaucherMatch/*.log
```

### Windows

**Frontend (Tauri):**
```
%APPDATA%\BaucherMatch\logs\tauri_YYYYMMDD.log
```

**Backend (FastAPI):**
```
%APPDATA%\BaucherMatch\logs\backend_YYYYMMDD.log
```

Ejemplo (PowerShell):
```powershell
# Ver logs del frontend
Get-Content "$env:APPDATA\BaucherMatch\logs\tauri_20260123.log"

# Ver logs del backend
Get-Content "$env:APPDATA\BaucherMatch\logs\backend_20260123.log"
```

### Linux

**Frontend (Tauri):**
```
~/.local/share/BaucherMatch/logs/tauri_YYYYMMDD.log
```

**Backend (FastAPI):**
```
~/.local/share/BaucherMatch/logs/backend_YYYYMMDD.log
```

Ejemplo:
```bash
# Ver logs del frontend
cat ~/.local/share/BaucherMatch/logs/tauri_20260123.log

# Ver logs del backend
cat ~/.local/share/BaucherMatch/logs/backend_20260123.log
```

## 🔍 Cómo Interpretar los Logs

### Formato de Logs

**Backend (Python):**
```
2026-01-23 10:30:45 - __main__ - INFO - 🚀 Iniciando backend FastAPI
2026-01-23 10:30:46 - __main__ - ERROR - Error fatal al iniciar el backend: [descripción]
```

**Frontend (Rust/Tauri):**
```
[2026-01-23 10:30:45] === Iniciando aplicación BaucherMatch ===
[2026-01-23 10:30:46] Error al iniciar backend: [descripción]
```

### Errores Comunes

#### 1. Backend no inicia

**Síntoma en logs:**
```
Error al iniciar backend: No such file or directory
```

**Solución:**
- Verificar que el ejecutable `backend-api` existe en `binaries/`
- Reconstruir el backend: `./build-backend.sh`

#### 2. Error de dependencias en macOS

**Síntoma en logs:**
```
ImportError: dlopen(...pdftotext...): Symbol not found
```

**Solución:**
```bash
# Reinstalar pdftotext con las bibliotecas correctas
brew install poppler
pip uninstall pdftotext
pip install pdftotext
```

#### 3. Base de datos no se puede abrir

**Síntoma en logs:**
```
Failed to open database: unable to open database file
```

**Solución:**
- Verificar permisos del directorio de datos
- Eliminar archivo corrupto y reiniciar app

#### 4. Puerto 8000 ya en uso

**Síntoma en logs:**
```
[Errno 48] Address already in use
```

**Solución:**
```bash
# macOS/Linux: Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F
```

## 🛠️ Herramientas de Debugging

### 1. Visor de Logs Integrado

Dentro de la aplicación:
1. Ve a la sección "Configuración" o "Ayuda"
2. Haz clic en "Ver Logs"
3. Copia las rutas de los archivos

### 2. Modo Verbose

Para obtener más información, ejecuta desde terminal:

```bash
# macOS
/Applications/BaucherMatch.app/Contents/MacOS/BaucherMatch

# La salida aparecerá en la terminal
```

### 3. DevTools en Producción

Si necesitas abrir DevTools en producción:

**Método 1: Modificar tauri.conf.json antes de compilar**
```json
{
  "app": {
    "withGlobalTauri": true
  },
  "bundle": {
    "windows": {
      "allowDowngrade": false
    }
  }
}
```

**Método 2: Shortcut**
- macOS: `Cmd + Option + I`
- Windows: `Ctrl + Shift + I`

## 📊 Recolectar Información para Reportar Bugs

Al reportar un error, incluye:

### 1. Información del Sistema
```bash
# macOS
sw_vers
python3 --version

# Windows
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
python --version

# Linux
lsb_release -a
python3 --version
```

### 2. Logs Completos
- Último archivo de log del frontend (tauri_*.log)
- Último archivo de log del backend (backend_*.log)

### 3. Pasos para Reproducir
1. Qué estabas haciendo cuando ocurrió el error
2. Archivo PDF que causó el problema (si aplica)
3. Capturas de pantalla

### 4. Versión de la Aplicación
Visible en: Configuración → Acerca de

## 🚨 Solución Rápida de Problemas

### Reinicio Completo

1. **Cerrar aplicación completamente**
   ```bash
   # macOS
   pkill -9 BaucherMatch
   pkill -9 backend-api
   
   # Windows
   taskkill /IM "BaucherMatch.exe" /F
   taskkill /IM "backend-api.exe" /F
   ```

2. **Limpiar caché**
   ```bash
   # macOS
   rm -rf ~/Library/Application\ Support/BaucherMatch/
   
   # Windows
   rd /s /q "%APPDATA%\BaucherMatch"
   
   # Linux
   rm -rf ~/.local/share/BaucherMatch/
   ```

3. **Reiniciar aplicación**

### Reinstalación Limpia

1. Desinstalar aplicación
2. Eliminar directorios de datos:
   - macOS: `~/Library/Application Support/BaucherMatch/`
   - Windows: `%APPDATA%\BaucherMatch`
   - Linux: `~/.local/share/BaucherMatch/`
3. Reinstalar desde instalador

## 📞 Obtener Ayuda

Si los logs no son suficientes para resolver el problema:

1. **Crear un Issue en GitHub** con:
   - Descripción del problema
   - Logs adjuntos
   - Información del sistema
   - Pasos para reproducir

2. **Modo Desarrollo** (para desarrolladores):
   ```bash
   # Clonar repositorio
   git clone [repo-url]
   cd baucher-match-frontend
   
   # Ejecutar en modo desarrollo
   npm run tauri dev
   
   # Backend en otra terminal
   cd backend
   source venv/bin/activate
   python main.py
   ```

## 📝 Notas Adicionales

- Los archivos de log se crean automáticamente con la fecha del día
- Los logs antiguos NO se eliminan automáticamente
- Para limpiar logs manualmente, elimina los archivos `.log` antiguos
- Los logs contienen información sensible, revisa antes de compartir

---

**Última actualización:** Enero 2026  
**Versión:** 1.0.0
