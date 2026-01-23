# 🔧 Solución: Error de Binarios en GitHub Actions

## ❌ Problema Original

```
resource path `binaries\backend-api-aarch64-apple-darwin-x86_64-pc-windows-msvc.exe` doesn't exist
```

Este error ocurría porque Tauri estaba concatenando incorrectamente los nombres de los binarios especificados en `externalBin`.

## ✅ Solución Implementada

### 1. Cambio en `tauri.conf.json`

**❌ INCORRECTO (versión anterior):**
```json
"externalBin": [
  "binaries/backend-api-aarch64-apple-darwin",
  "binaries/backend-api-x86_64-apple-darwin",
  "binaries/backend-api-x86_64-unknown-linux-gnu",
  "binaries/backend-api-x86_64-pc-windows-msvc"
]
```

**✅ CORRECTO (versión actual):**
```json
"externalBin": [
  "binaries/backend-api"
]
```

### 2. Cómo Funciona Tauri con Binarios Externos

Tauri **automáticamente** agrega el sufijo de la plataforma al nombre base del binario:

| Plataforma | Nombre Base | Binario Buscado |
|------------|-------------|-----------------|
| Windows x64 | `backend-api` | `backend-api-x86_64-pc-windows-msvc.exe` |
| macOS ARM (M1/M2) | `backend-api` | `backend-api-aarch64-apple-darwin` |
| macOS Intel | `backend-api` | `backend-api-x86_64-apple-darwin` |
| Linux x64 | `backend-api` | `backend-api-x86_64-unknown-linux-gnu` |

### 3. Estructura de Archivos Correcta

```
src-tauri/
├── binaries/
│   ├── backend-api.exe                              # Para desarrollo en Windows
│   ├── backend-api-x86_64-pc-windows-msvc.exe       # Para build en Windows
│   ├── backend-api                                  # Para desarrollo en macOS/Linux
│   ├── backend-api-aarch64-apple-darwin             # Para build en macOS ARM
│   ├── backend-api-x86_64-apple-darwin              # Para build en macOS Intel
│   └── backend-api-x86_64-unknown-linux-gnu         # Para build en Linux
```

### 4. Scripts de Build Actualizados

#### Windows: `build-backend.bat`

```batch
REM Copia el binario con ambos nombres
copy /Y "dist\backend-api.exe" "..\src-tauri\binaries\backend-api-x86_64-pc-windows-msvc.exe"
copy /Y "dist\backend-api.exe" "..\src-tauri\binaries\backend-api.exe"
```

#### macOS/Linux: `build-backend.sh`

```bash
# Copia el binario con nombre específico de plataforma
cp "dist/backend-api" "../src-tauri/binaries/$BINARY_NAME"
# También copia con nombre base para desarrollo
cp "dist/backend-api" "../src-tauri/binaries/backend-api"
```

### 5. Código Rust Simplificado

**❌ ANTES (complejo, específico por plataforma):**
```rust
let binary_name = if cfg!(target_os = "macos") {
    if cfg!(target_arch = "aarch64") {
        "backend-api-aarch64-apple-darwin"
    } else {
        "backend-api-x86_64-apple-darwin"
    }
} else if cfg!(target_os = "windows") {
    "backend-api-x86_64-pc-windows-msvc"
} else {
    "backend-api-x86_64-unknown-linux-gnu"
};
```

**✅ AHORA (simple, deja que Tauri maneje la plataforma):**
```rust
let binary_name = "backend-api";
let backend_path = app_handle
    .path()
    .resolve(format!("binaries/{}", binary_name), tauri::path::BaseDirectory::Resource)?;
```

## 🚀 Cómo Compilar Ahora

### Compilación Local

#### Windows:
```powershell
# 1. Compilar backend
.\build-backend.bat

# 2. Verificar que se crearon los binarios
dir src-tauri\binaries\backend-api*.exe

# 3. Compilar aplicación
npm run tauri build
```

#### macOS/Linux:
```bash
# 1. Compilar backend
./build-backend.sh

# 2. Verificar que se creó el binario
ls -lh src-tauri/binaries/backend-api*

# 3. Compilar aplicación
npm run tauri build
```

### GitHub Actions

El workflow ahora:
1. ✅ Compila el backend con PyInstaller
2. ✅ Copia el binario a `backend-api-x86_64-pc-windows-msvc.exe`
3. ✅ También copia a `backend-api.exe` (nombre base)
4. ✅ Tauri encuentra automáticamente el binario correcto
5. ✅ Empaqueta todo en el instalador

## 📋 Checklist de Verificación

Antes de hacer push, verifica:

- [ ] Ejecutaste el script de build del backend (`build-backend.bat` o `build-backend.sh`)
- [ ] Existe el archivo `src-tauri/binaries/backend-api-[PLATAFORMA]`
- [ ] Existe el archivo `src-tauri/binaries/backend-api` (sin sufijo)
- [ ] El archivo `tauri.conf.json` tiene solo `"binaries/backend-api"` en `externalBin`
- [ ] La compilación local funciona correctamente
- [ ] Los logs muestran la ruta correcta del binario

## 🐛 Debugging

Si sigues teniendo problemas:

### 1. Ver qué archivos busca Tauri

En los logs de compilación de Rust, busca:
```
resource path `binaries\...` doesn't exist
```

Esto te dirá exactamente qué archivo está buscando Tauri.

### 2. Listar archivos en binaries

**Windows:**
```powershell
Get-ChildItem src-tauri\binaries -Recurse | Format-Table Name, Length
```

**macOS/Linux:**
```bash
ls -lah src-tauri/binaries/
```

### 3. Verificar en runtime

Los logs de la aplicación ahora muestran:
```
Buscando binario: backend-api
Ruta resuelta del backend: "C:\...\binaries\backend-api-x86_64-pc-windows-msvc.exe"
Listando archivos en: "C:\...\binaries"
  - backend-api.exe
  - backend-api-x86_64-pc-windows-msvc.exe
```

## 📚 Referencias

- [Tauri Sidecar Documentation](https://tauri.app/v1/guides/building/sidecar)
- [Tauri External Binary](https://tauri.app/v1/api/config/#bundleconfig.externalbin)
- [GitHub Actions - Build Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)

## ✅ Resultado Esperado

Después de estos cambios:

✅ **Compilación local**: Funciona en Windows, macOS y Linux  
✅ **GitHub Actions**: Compila correctamente sin errores  
✅ **Instaladores**: Se generan con el backend incluido  
✅ **Logs**: Muestran claramente qué está pasando  
✅ **Debugging**: Fácil identificar problemas  

---

**Última actualización:** 23 de Enero de 2026  
**Problema resuelto:** Error de concatenación de nombres de binarios en Tauri
