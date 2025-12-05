# Instrucciones para Incluir Librerías de Poppler en Windows

## Para el desarrollador que compila en Windows:

### 1. Descargar Poppler para Windows

Ve a: https://github.com/oschwartz10612/poppler-windows/releases/latest

Descarga el archivo: `Release-XX.XX.X-0.zip` (la versión más reciente)

### 2. Extraer los archivos

Extrae el ZIP descargado a una carpeta temporal.

### 3. Copiar las DLLs necesarias

Del directorio extraído, copia **TODAS** las DLLs de la carpeta `Library/bin/` a:

```
src-tauri/libs/
```

Las DLLs principales que necesitas incluir son:
- `libpoppler.dll`
- `libpoppler-cpp.dll`
- `libpoppler-glib.dll`
- `freetype.dll`
- `jpeg62.dll`
- `libpng16.dll`
- `libtiff.dll`
- `openjp2.dll`
- `zlib1.dll`
- `liblzma.dll`
- Y cualquier otra DLL que esté en la carpeta `Library/bin/`

### 4. Verificar la estructura

Tu proyecto debe tener esta estructura:

```
baucher-match-frontend/
├── src-tauri/
│   ├── libs/
│   │   ├── libpoppler.dll
│   │   ├── libpoppler-cpp.dll
│   │   ├── freetype.dll
│   │   └── ... (otras DLLs)
│   └── binaries/
│       └── backend-api-x86_64-pc-windows-msvc.exe
```

### 5. Compilar

Una vez copiadas las DLLs:

```bash
npm run build:all
```

## Notas Importantes

- ⚠️ **NO** uses el script `bundle-libs.sh` en Windows (es solo para macOS/Linux)
- ✅ Las DLLs deben estar en `src-tauri/libs/` antes de compilar
- ✅ Tauri empaquetará automáticamente las DLLs con el instalador
- ✅ El instalador final incluirá todo lo necesario, el usuario NO necesitará instalar nada

## Alternativa: Compilación Cruzada

Si estás en macOS/Linux y quieres compilar para Windows, necesitarás:
1. Configurar Wine o una VM de Windows
2. Seguir los pasos anteriores dentro del entorno Windows
3. O usar GitHub Actions para compilación automática en Windows

## Verificación

Para verificar que las DLLs están incluidas correctamente:

1. Después de `npm run build:all`
2. Navega a `src-tauri/target/release/bundle/msi/` o `nsis/`
3. Instala el programa
4. Ejecuta la aplicación
5. Prueba subir un PDF - si funciona, las DLLs están correctamente incluidas
