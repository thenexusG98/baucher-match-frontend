# Depuración del Workflow de GitHub Actions

# Depuración del Workflow de GitHub Actions

## Problema Identificado

El workflow de GitHub Actions no está generando el ejecutable del backend (`backend-api.exe`) correctamente, lo que resulta en un directorio `binaries` vacío cuando la aplicación se instala en Windows.

### Actualización: Error de PowerShell ✅ RESUELTO. 

**Problema encontrado**: PowerShell estaba interpretando el output normal de PyInstaller (que va a stderr) como un error, causando que el workflow fallara prematuramente.

**Solución implementada**: Cambiar `Tee-Object` por `Out-File` con `$ErrorActionPreference = "Continue"` para que PowerShell no trate stderr como error fatal.

### Actualización: Simplificación del Build

**Cambio**: Se cambió de usar `backend.spec` a usar PyInstaller directamente con `--onefile` para simplificar el debugging.

**Comando anterior**:
```powershell
pyinstaller --clean --log-level DEBUG backend.spec
```

**Comando actual**:
```powershell
pyinstaller --clean --onefile --log-level DEBUG --name backend-api main.py
```

**Ventajas**:
- Más simple y directo
- Menos puntos de fallo
- Output más predecible (`dist/backend-api.exe`)

### Actualización: Versión de Python

**Cambio**: Se actualizó de Python 3.9 a Python 3.11 para coincidir con el entorno de desarrollo.

## Cambios Implementados

### 1. Mejoras en el paso "Build backend"

Se agregaron las siguientes verificaciones y logs para identificar el problema:

#### Verificación de PyInstaller
```powershell
pyinstaller --version
```
- **Propósito**: Confirmar que PyInstaller está instalado correctamente

#### Verificación de archivos de entrada
```powershell
Test-Path "backend\backend.spec"
Test-Path "backend\main.py"
```
- **Propósito**: Asegurar que los archivos necesarios existen antes de compilar

#### Compilación con logging detallado
```powershell
pyinstaller --log-level DEBUG backend.spec 2>&1 | Tee-Object -FilePath "pyinstaller-build.log"
```
- **Propósito**: Capturar todo el output de PyInstaller para análisis
- **Output**: Se guarda en `pyinstaller-build.log`

#### Verificación del directorio dist
```powershell
Get-ChildItem "backend\dist" -Recurse | Select-Object FullName, Length | Format-Table
```
- **Propósito**: Listar todos los archivos generados por PyInstaller

#### Búsqueda inteligente del ejecutable
Se busca el ejecutable en múltiples ubicaciones posibles:
- `backend\dist\backend-api\backend-api.exe`
- `backend\dist\backend-api.exe`
- `backend\dist\main\main.exe`
- `backend\dist\main.exe`

#### Copia de binarios
Si se encuentra el ejecutable, se copia con ambos nombres:
- `backend-api-x86_64-pc-windows-msvc.exe` (para producción)
- `backend-api.exe` (para desarrollo)

### 2. Manejo de errores mejorado

Si no se encuentra el ejecutable:
1. Se muestra la estructura completa de `backend\dist`
2. Se imprime el log completo de PyInstaller
3. El workflow falla con código de salida 1

## Qué Buscar en los Logs del Workflow

Cuando ejecutes el workflow nuevamente, verifica lo siguiente en los logs:

### ✅ Paso 1: Verificación de PyInstaller
```
PyInstaller: X.X.X
```
- Debe mostrar la versión instalada (típicamente 5.x o 6.x)

### ✅ Paso 2: Verificación de archivos
```
✅ backend.spec existe
✅ main.py existe
```

### ✅ Paso 3: Output de PyInstaller
Busca en los logs:
- `Building EXE from...` - Indica que está construyendo el ejecutable
- `Building PKG...` - Indica empaquetado
- `Building EXE completed successfully` - Éxito

### ❌ Errores Comunes a Buscar

#### Error: Módulos faltantes
```
ModuleNotFoundError: No module named 'xxx'
```
**Solución**: Agregar el módulo a `hiddenimports` en `backend.spec`

#### Error: Archivo pdftotext no encontrado
```
WARNING No se encontro pdftotext en: ...
```
**Solución**: Verificar instalación de Poppler y pdftotext

#### Error: Dependencias de Windows
```
Error loading Python DLL
```
**Solución**: Problema con compilador de C o Visual Studio Build Tools

### ✅ Paso 4: Estructura de dist
Debe mostrar algo como:
```
FullName                                    Length
--------                                    ------
backend\dist\backend-api\backend-api.exe    XXXXXX
backend\dist\backend-api\...otros archivos...
```

### ✅ Paso 5: Binarios copiados
```
✅ Backend copiado a: backend-api-x86_64-pc-windows-msvc.exe
✅ Backend copiado a: backend-api.exe
```

## Archivos de Log Generados

1. **pyinstaller-build.log**: Log completo de PyInstaller
2. **GitHub Actions logs**: Output del workflow completo

## Próximos Pasos

1. **Commit y push** de estos cambios
2. **Ejecutar el workflow** en GitHub Actions
3. **Revisar los logs** según las indicaciones anteriores
4. **Identificar el punto de fallo** exacto

Si PyInstaller falla:
- Revisar `pyinstaller-build.log` para el error específico
- Modificar `backend.spec` según sea necesario
- Agregar módulos faltantes a `hiddenimports`

Si PyInstaller tiene éxito pero no copia:
- Verificar que el ejecutable está en la ubicación correcta
- Ajustar las rutas de búsqueda en el workflow

## Comandos Útiles para Testing Local (Windows)

```powershell
# Compilar backend localmente
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --log-level DEBUG backend.spec

# Verificar resultado
ls dist\backend-api\
```

## Configuración Actual

### backend.spec
- **Nombre del ejecutable**: `backend-api`
- **Modo**: Un solo archivo (`onefile=True` implícito en EXE)
- **Consola**: Habilitada (`console=True`)
- **UPX**: Habilitado para comprimir

### tauri.conf.json
- **externalBin**: `["binaries/backend-api"]`
- Tauri agrega automáticamente el sufijo de plataforma

### GitHub Actions
- **OS**: Windows Latest
- **Python**: 3.11
- **Node**: 20
- **Rust**: Stable
- **Poppler**: Instalado vía choco

## Contacto para Soporte

Si el problema persiste después de estos cambios:
1. Compartir el output completo de `pyinstaller-build.log`
2. Compartir los logs del workflow de GitHub Actions
3. Indicar si la compilación local funciona en Windows
