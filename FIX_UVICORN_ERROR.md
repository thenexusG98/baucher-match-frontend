# Fix: ModuleNotFoundError uvicorn

## Problema
El backend falla con: `ModuleNotFoundError: No module named 'uvicorn'`

## Causa
PyInstaller no incluía uvicorn y otros módulos necesarios en el ejecutable.

## Solución Implementada

### 1. Actualizado `backend/backend.spec`
- ✅ Agregado `'uvicorn'` en hiddenimports (faltaba el módulo base)
- ✅ Agregados todos los submódulos necesarios de uvicorn, fastapi, pydantic, starlette
- ✅ Agregadas dependencias: anyio, sniffio, h11, click, python_multipart

### 2. Actualizado `.github/workflows/build-release.yml`
- ✅ Cambiado de `pyinstaller --onefile main.py` a `pyinstaller backend.spec`
- ✅ Agregada verificación del contenido de backend.spec antes de compilar
- ✅ Mejorado logging para confirmar que se usa el .spec

### 3. Actualizado PATH para DLLs
- ✅ Agregado directorio del backend al PATH (donde están las DLLs)
- ✅ Agregado directorio libs como respaldo
- ✅ Mejorado logging en lib.rs para mostrar qué se agrega al PATH

## Pasos para Aplicar el Fix

1. **Commit y push de los cambios**:
   ```bash
   git add .
   git commit -m "Fix: Agregar uvicorn y dependencias a PyInstaller spec"
   git push
   ```

2. **Esperar GitHub Actions**:
   - Ve a: https://github.com/thenexusG98/baucher-match-frontend/actions
   - Espera a que el workflow "Build Tauri App" complete (~10-15 minutos)
   - Verifica que el workflow muestre: "Ejecutando PyInstaller con backend.spec..."

3. **Descargar nuevo instalador**:
   - Ve a la sección "Releases" o "Artifacts" del workflow
   - Descarga el nuevo MSI generado

4. **Instalar y probar**:
   - Desinstala la versión anterior
   - Instala el nuevo MSI
   - Ejecuta la aplicación

## Logs Esperados

Después del fix, los logs deberían mostrar:

```
✅ Backend iniciado con PID: XXXX
✓ Backend corriendo correctamente con PID: XXXX
✓ Backend sigue activo después de 5 segundos - uvicorn probablemente iniciado correctamente
```

**Sin errores** de `ModuleNotFoundError`.

## Si Aún Falla

Si después de aplicar estos cambios sigue fallando, compartir:
1. Log completo de Tauri (AppData\Roaming\com.baucher-match-frontend.app\logs\)
2. Log del backend (AppData\Roaming\BaucherMatch\logs\)
3. El error específico que aparece en "Error del backend (stderr)"

## Archivos Modificados

- `backend/backend.spec` - Hiddenimports completos
- `.github/workflows/build-release.yml` - Usa backend.spec
- `src-tauri/src/lib.rs` - PATH mejorado y captura de stderr
- `src-tauri/tauri.conf.json` - Incluye binaries/*.dll
