# Baucher Match Frontend - Integración Backend FastAPI + Tauri

Este proyecto integra un backend FastAPI empaquetado dentro de una aplicación Tauri.

## 🏗️ Estructura del Proyecto

```
baucher-match-frontend/
├── backend/                    # Backend FastAPI
│   ├── app/                   # Código de la aplicación
│   │   ├── api/              # Rutas de la API
│   │   ├── services/         # Servicios de negocio
│   │   └── utils/            # Utilidades
│   ├── main.py               # Punto de entrada del backend
│   ├── backend.spec          # Configuración de PyInstaller
│   └── requeriments.txt      # Dependencias Python
├── src/                       # Frontend React
│   ├── services/
│   │   └── backend.ts        # Servicio para controlar el backend
│   └── App.tsx               # Componente principal
├── src-tauri/                 # Aplicación Tauri
│   ├── binaries/             # Ejecutables del backend
│   ├── capabilities/         # Permisos de Tauri
│   └── src/
│       └── lib.rs            # Código Rust con comandos Tauri
└── build-backend.sh           # Script para compilar el backend
```

## 🚀 Desarrollo

### Modo Desarrollo (Backend y Frontend separados)

**Terminal 1 - Backend:**
```bash
npm run dev:backend
```

**Terminal 2 - Frontend:**
```bash
npm run tauri:dev
```

### Modo Desarrollo (Solo Frontend, sin backend empaquetado)

Si solo quieres desarrollar el frontend y el backend ya está corriendo:
```bash
npm run tauri dev
```

## 📦 Compilación para Producción

### 1. Instalar PyInstaller (si no lo tienes)

```bash
pip3 install pyinstaller
```

### 2. Compilar el Backend

```bash
npm run build:backend
```

Esto ejecutará `build-backend.sh` que:
- Detecta tu sistema operativo y arquitectura
- Compila el backend con PyInstaller
- Genera el ejecutable en `src-tauri/binaries/`
- El binario se nombrará según tu plataforma:
  - macOS (Intel): `backend-api-x86_64-apple-darwin`
  - macOS (M1/M2): `backend-api-aarch64-apple-darwin`
  - Windows: `backend-api-x86_64-pc-windows-msvc.exe`
  - Linux: `backend-api-x86_64-unknown-linux-gnu`

### 3. Compilar Todo (Backend + Frontend + Empaquetar)

```bash
npm run build:all
```

Esto:
1. Compila el backend con PyInstaller
2. Compila el frontend con Vite
3. Empaqueta todo en una aplicación Tauri

Los instaladores se generarán en:
- macOS: `src-tauri/target/release/bundle/dmg/`
- Windows: `src-tauri/target/release/bundle/msi/`
- Linux: `src-tauri/target/release/bundle/appimage/`

## 🔧 Cómo Funciona

### Flujo de Inicio

1. **Usuario abre la aplicación**
2. **App.tsx** muestra pantalla de carga
3. **backendService.initialize()** invoca comando Tauri `start_backend`
4. **lib.rs** ejecuta el binario del backend desde `src-tauri/binaries/`
5. **Backend FastAPI** inicia en `http://127.0.0.1:8000`
6. **backendService.waitForReady()** hace polling al endpoint `/api/v1/health`
7. **Cuando el backend responde**, se oculta la pantalla de carga
8. **Sidebar** se muestra y la aplicación está lista

### Flujo de Cierre

1. **Usuario cierra la ventana**
2. **lib.rs** detecta el evento `CloseRequested`
3. **stop_backend()** mata el proceso del backend
4. **Aplicación se cierra**

## 🛠️ Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Inicia solo Vite (desarrollo web) |
| `npm run dev:backend` | Inicia el backend Python en modo desarrollo |
| `npm run tauri:dev` | Inicia Tauri en modo desarrollo |
| `npm run build:backend` | Compila el backend con PyInstaller |
| `npm run build` | Compila solo el frontend |
| `npm run build:all` | Compila backend + frontend + empaqueta todo |
| `npm run tauri build` | Compila y empaqueta Tauri (sin backend) |

## 🐛 Debugging

### Ver logs del backend

Los logs del backend se muestran en la consola de Tauri:

**macOS/Linux:**
```bash
# Desde la aplicación compilada
./target/release/baucher-match-frontend

# O en modo desarrollo
npm run tauri:dev
```

**Windows:**
```bash
.\target\release\baucher-match-frontend.exe
```

### Verificar que el backend está corriendo

El servicio `backendService` incluye varios métodos útiles:

```typescript
// Verificar estado
const isRunning = await backendService.checkStatus();

// Health check
const isHealthy = await backendService.healthCheck();

// Obtener URL base
const url = backendService.getBaseUrl();
```

### Errores comunes

**Error: "El ejecutable del backend no existe"**
- Solución: Ejecuta `npm run build:backend` primero

**Error: "Backend no pudo iniciarse"**
- Verifica que Python 3 esté instalado
- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa los logs de la consola

**Error: "Backend no responde después de 30 intentos"**
- El backend puede estar tardando en iniciar
- Aumenta el timeout en `backendService.waitForReady(60)` (60 intentos)
- Verifica que el puerto 8000 no esté ocupado

## 📝 Configuración

### Cambiar el puerto del backend

1. Edita `backend/main.py`:
```python
uvicorn.run(app, host="127.0.0.1", port=9000)  # Cambiar 8000 por 9000
```

2. Edita `src/services/backend.ts`:
```typescript
private readonly baseUrl = 'http://127.0.0.1:9000';
```

### Agregar más endpoints

1. Agrega rutas en `backend/app/api/routes_transacciones.py`
2. Registra el router en `backend/app/app.py` si es necesario
3. Recompila el backend: `npm run build:backend`

## 🔒 Seguridad

- El backend solo acepta conexiones desde `localhost` (127.0.0.1)
- CORS configurado solo para orígenes de Tauri
- El backend se ejecuta como proceso hijo de Tauri
- Se detiene automáticamente al cerrar la aplicación

## 📦 Tamaño del Binario

El ejecutable del backend puede ser grande (~50-100MB) debido a:
- Python runtime empaquetado
- Dependencias de FastAPI
- Bibliotecas de procesamiento de PDF (PyMuPDF, pdftotext)

Para reducir el tamaño:
- Usa `--exclude-module` en PyInstaller para módulos innecesarios
- Considera UPX compression (ya habilitado en `backend.spec`)
- Revisa las dependencias en `requirements.txt`

## 🎯 Resultado Final

Una vez compilado, obtendrás un instalador único que:
- ✅ Instala la aplicación completa
- ✅ Incluye el backend Python
- ✅ No requiere instalación de Python
- ✅ Funciona offline
- ✅ Inicia/detiene el backend automáticamente

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en la consola de Tauri
2. Verifica que el binario del backend existe en `src-tauri/binaries/`
3. Prueba el backend standalone: `cd backend && python3 main.py`
4. Revisa los issues del repositorio
