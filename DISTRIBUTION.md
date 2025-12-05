# 📦 Guía de Distribución - Baucher Match

## 🎯 Resumen

El instalador final de Baucher Match es **completamente autónomo** y no requiere que el usuario instale ninguna dependencia.

## ✅ ¿Qué INCLUYE el instalador?

Cuando ejecutas `npm run build:all`, el instalador resultante contiene:

### 1. **Python Runtime Embebido**
- ✅ Intérprete de Python completo
- ✅ Biblioteca estándar de Python
- ✅ **NO requiere** Python instalado en la máquina del usuario

### 2. **Todas las Dependencias Python**
- ✅ FastAPI
- ✅ Uvicorn
- ✅ Pydantic
- ✅ PyMuPDF (fitz)
- ✅ pdftotext
- ✅ Y todas las sub-dependencias

### 3. **Librerías del Sistema (Poppler)**
- ✅ `libpoppler.dylib` / `.so` / `.dll`
- ✅ `libpoppler-cpp.dylib` / `.so` / `.dll`
- ✅ Todas las dependencias de Poppler
- ✅ **NO requiere** instalación manual de Poppler

### 4. **Frontend React**
- ✅ Aplicación web compilada
- ✅ Assets optimizados
- ✅ Estilos CSS

### 5. **Base de Datos SQLite**
- ✅ Motor de base de datos embebido
- ✅ Se crea automáticamente en la primera ejecución

## 🖥️ Instaladores Generados

### macOS
**Ubicación:** `src-tauri/target/release/bundle/dmg/`
**Archivo:** `baucher-match-frontend_0.1.0_aarch64.dmg` (Apple Silicon) o `x86_64.dmg` (Intel)

**Instalación:**
1. Abrir el `.dmg`
2. Arrastrar la app a Aplicaciones
3. Ejecutar la aplicación

**Tamaño aproximado:** ~50-80 MB

### Linux
**Ubicación:** `src-tauri/target/release/bundle/appimage/`
**Archivo:** `baucher-match-frontend_0.1.0_amd64.AppImage`

**Instalación:**
1. Dar permisos de ejecución: `chmod +x baucher-match-frontend_*.AppImage`
2. Ejecutar: `./baucher-match-frontend_*.AppImage`

**Tamaño aproximado:** ~60-90 MB

### Windows
**Ubicación:** `src-tauri/target/release/bundle/msi/` o `nsis/`
**Archivo:** `baucher-match-frontend_0.1.0_x64.msi` o `.exe`

**Instalación:**
1. Ejecutar el instalador `.msi` o `.exe`
2. Seguir el asistente de instalación
3. Ejecutar desde el menú de inicio

**Tamaño aproximado:** ~70-100 MB

## 🚀 Proceso de Compilación

### Para el Desarrollador

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd baucher-match-frontend

# 2. Instalar dependencias de desarrollo
npm install

# 3. Configurar entorno Python (solo para compilar)
# macOS: brew install poppler
# Linux: sudo apt-get install libpoppler-cpp-dev
# Windows: Ver WINDOWS_LIBS_SETUP.md

# 4. Crear entorno virtual y dependencias Python
python3 -m venv .venv
.venv/bin/pip install -r backend/requeriments.txt

# 5. Compilar todo
npm run build:all
```

### Comandos Individuales

```bash
# Solo compilar backend
npm run build:backend

# Solo copiar librerías del sistema
npm run build:libs

# Solo compilar frontend + empaquetar
npm run tauri build
```

## 📝 Requisitos del Sistema del Usuario Final

### macOS
- macOS 10.15 (Catalina) o superior
- 100 MB de espacio en disco
- **NO requiere** Python, Homebrew, ni nada adicional

### Linux
- Distribución moderna (Ubuntu 20.04+, Fedora 34+, etc.)
- libc 2.31 o superior
- 100 MB de espacio en disco
- **NO requiere** Python ni dependencias adicionales

### Windows
- Windows 10 versión 1809 o superior
- 100 MB de espacio en disco
- **NO requiere** Python ni dependencias adicionales

## ⚠️ Notas Importantes

### 1. Firma de Código (Code Signing)

Los instaladores **no están firmados** por defecto. En producción, deberías:

**macOS:**
- Firmar con certificado de desarrollador de Apple
- Notarizar la aplicación

**Windows:**
- Firmar con certificado Authenticode

Sin firma, los usuarios verán advertencias de seguridad.

### 2. Tamaño del Instalador

El instalador es relativamente grande (~50-100 MB) porque incluye:
- Python runtime completo (~20 MB)
- Todas las librerías Python (~30 MB)
- Librerías nativas (Poppler, etc.) (~10 MB)
- Frontend y assets (~5 MB)

### 3. Primera Ejecución

La primera vez que el usuario ejecuta la app:
1. Se crea la base de datos SQLite automáticamente
2. El backend inicia (toma ~3-5 segundos)
3. Aparece la pantalla principal

Ejecuciones posteriores son más rápidas.

### 4. Actualizaciones

Para distribuir actualizaciones:
1. Incrementar versión en `package.json` y `src-tauri/tauri.conf.json`
2. Recompilar: `npm run build:all`
3. Distribuir el nuevo instalador

Para auto-actualizaciones, considera usar Tauri Updater (requiere configuración adicional).

## 🧪 Pruebas Antes de Distribuir

### 1. Probar en Máquina Limpia

Idealmente, prueba el instalador en una máquina virtual o limpia que **NO tenga**:
- Python instalado
- Node.js instalado  
- Poppler instalado
- Ninguna dependencia de desarrollo

### 2. Verificaciones

✅ La aplicación se instala sin errores
✅ La aplicación inicia correctamente
✅ El backend responde (probar subir un PDF)
✅ La base de datos se crea automáticamente
✅ La aplicación se cierra correctamente

### 3. Logs

Si hay problemas, los logs están en:

**macOS:**
```
~/Library/Logs/baucher-match-frontend/
```

**Linux:**
```
~/.local/share/baucher-match-frontend/logs/
```

**Windows:**
```
%APPDATA%\baucher-match-frontend\logs\
```

## 📚 Documentación Adicional

- `BACKEND_INTEGRATION.md` - Arquitectura técnica detallada
- `BACKEND_SETUP.md` - Guía de desarrollo
- `WINDOWS_LIBS_SETUP.md` - Instrucciones específicas para Windows

## 🆘 Problemas Comunes

### "La aplicación no abre"

**Causa:** Permisos en macOS
**Solución:** Clic derecho → Abrir (la primera vez)

### "El backend no inicia"

**Causa:** Puerto 8000 ocupado
**Solución:** Cerrar otros programas que usen el puerto 8000

### "Error al procesar PDF"

**Causa:** Archivo PDF corrupto o no estándar
**Solución:** Intentar con otro PDF

## 📞 Soporte

Para issues técnicos, revisa:
1. Logs de la aplicación
2. Issues en el repositorio de GitHub
3. Documentación de Tauri: https://tauri.app
