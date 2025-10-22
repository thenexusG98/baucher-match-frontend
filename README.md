# 🏦 BaucherMatch Frontend

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![React](https://img.shields.io/badge/React-18.3.1-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-3178C6?logo=typescript)
![Tauri](https://img.shields.io/badge/Tauri-2.x-FFC131?logo=tauri)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.1.3-38B2AC?logo=tailwind-css)

Aplicación de escritorio para procesar y analizar estados de cuenta bancarios en formato PDF, convirtiendo automáticamente la información en archivos CSV estructurados con visualización de datos mediante gráficos interactivos.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Prerequisitos](#-prerequisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura](#-arquitectura)
- [API Backend](#-api-backend)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Scripts Disponibles](#-scripts-disponibles)
- [Configuración IDE](#-configuración-ide)
- [Despliegue](#-despliegue)

## ✨ Características

### 🎯 Funcionalidades Principales

- **📄 Procesamiento de PDF**: Carga y procesamiento automático de estados de cuenta en formato PDF
- **💾 Exportación CSV**: Conversión automática de datos extraídos a formato CSV
- **📊 Dashboard Interactivo**: Visualización de ingresos mensuales mediante gráficos de barras
- **⏱️ Timestamps Dinámicos**: Sistema de tiempo relativo que muestra cuándo fue procesado cada archivo
- **📈 Análisis en Tiempo Real**: Contador de transacciones detectadas y métricas de rendimiento
- **📂 Historial de Archivos**: Registro completo de archivos procesados con timestamps
- **🎨 UI/UX Moderna**: Interfaz responsiva con Tailwind CSS y componentes personalizados
- **🖥️ Aplicación de Escritorio**: Construida con Tauri para rendimiento nativo

### 🔧 Características Técnicas

- **Gestión de Estado**: React Hooks (useState, useEffect) para manejo eficiente del estado
- **Comunicación con Backend**: Integración con API REST usando Fetch API
- **Headers Personalizados**: Manejo de headers HTTP personalizados (X-Execution-Time, X-Total-Count, X-json)
- **Responsive Design**: Layout adaptativo con sistema de grids CSS
- **Tooltips Personalizados**: Formateo de datos con símbolos de moneda y separadores de miles
- **Manejo de Errores**: Sistema robusto de captura y visualización de errores

## 🛠️ Tecnologías

### Frontend
- **React 18.3.1** - Biblioteca de UI con componentes funcionales
- **TypeScript 5.6.2** - Tipado estático para JavaScript
- **Vite 6.0.3** - Build tool de nueva generación
- **Tailwind CSS 4.1.3** - Framework CSS utility-first

### Desktop Framework
- **Tauri 2.x** - Framework para aplicaciones de escritorio con Rust

### Visualización de Datos
- **Recharts 2.15.3** - Biblioteca de gráficos para React
- **Lucide React 0.487.0** - Iconos SVG personalizables
- **React Icons 5.5.0** - Biblioteca de iconos

### UI Components
- **Flowbite 3.1.2** - Componentes UI basados en Tailwind

## 📦 Prerequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Node.js**: Versión 14.x o superior (recomendado: 18.x LTS)
- **npm**: Versión 6.x o superior
- **Rust**: Última versión estable (para Tauri)
- **Backend**: Servidor FastAPI corriendo en `http://localhost:8000`

### Verificar Versiones

```bash
node --version  # v18.x.x o superior
npm --version   # v6.x.x o superior
rustc --version # 1.70.0 o superior
```

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd baucher-match-frontend-main
```

### 2. Instalar dependencias

```bash
npm install
```

### 3. Configurar Backend

Asegúrate de que tu backend FastAPI esté configurado con CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Execution-Time", "X-Total-Count", "X-json"]
)
```

### 4. Ejecutar en modo desarrollo

```bash
npm run tauri dev
```

La aplicación se abrirá como aplicación de escritorio y el frontend estará disponible en `http://localhost:1420`

## 💻 Uso

### Cargar Estado de Cuenta

1. **Seleccionar Archivo**: Haz clic en "Cargar estado de cuenta" en el menú lateral
2. **Elegir PDF**: Selecciona un archivo PDF de tu estado de cuenta bancario
3. **Procesar**: Haz clic en "Subir y Procesar"
4. **Descargar CSV**: El archivo CSV se descargará automáticamente

### Visualizar Dashboard

1. **Ver Gráficos**: Haz clic en "Inicio" para ver el dashboard
2. **Analizar Datos**: Observa los ingresos mensuales en el gráfico de barras
3. **Revisar Métricas**: Consulta las transacciones detectadas y archivos procesados

### Información Mostrada

- **Gráfico de Ingresos**: Visualización mensual de ingresos (Ene-Jun)
- **Transacciones Detectadas**: Contador en tiempo real
- **Archivo Analizado**: Nombre del último archivo con timestamp relativo
- **Historial**: Lista de todos los archivos procesados

## 🏗️ Arquitectura

### Estructura de Componentes

```
App (Raíz)
│
└── Sidebar (Navegación + Estado Global)
    │
    ├── Dashboard (Visualización de Datos)
    │   ├── Card
    │   │   └── CardContent
    │   └── BarChart (Recharts)
    │       └── CustomTooltip
    │
    ├── UploadStatement (Carga de Estados Completos)
    │   ├── Card (Transacciones)
    │   └── Card (Archivo Analizado)
    │
    └── UploadPartialStatement (Carga Parcial)
        └── Similar a UploadStatement
```

### Flujo de Datos

```
Usuario selecciona PDF
        ↓
UploadStatement maneja la carga
        ↓
POST → Backend API (/api/v1/download-csv)
        ↓
Backend procesa PDF → Extrae datos
        ↓
Response: Blob (CSV) + Headers (JSON metadata)
        ↓
Frontend parsea headers (X-json)
        ↓
Actualiza estado local + Descarga CSV
        ↓
Callback → onFileProcessed
        ↓
Sidebar actualiza processedFiles[]
        ↓
Dashboard recibe props y renderiza gráfico
```

### Gestión de Estado

```typescript
// Estado Global (Sidebar)
const [processedFiles, setProcessedFiles] = useState<ProcessedFile[]>([]);

// Estado Local (UploadStatement)
const [file, setFile] = useState<File | null>(null);
const [loading, setLoading] = useState(false);
const [totalCounts, setTotalCounts] = useState(0);
const [fileName, setFileName] = useState("");
const [fileProcessedTime, setFileProcessedTime] = useState<Date | null>(null);
```

## 🔌 API Backend

### Endpoint Principal

```
POST http://localhost:8000/api/v1/download-csv
```

### Request

```typescript
const formData = new FormData();
formData.append("file", pdfFile);

fetch("http://localhost:8000/api/v1/download-csv", {
  method: "POST",
  body: formData,
});
```

### Response

**Headers:**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="ESTADO_DE_CUENTA_MARZO_2024.csv"
X-Execution-Time: 2.35
X-Total-Count: 45
X-json: {"execution_time": 2.35, "total_count": 45, "income_month": 15000.50}
```

**Body:** Blob del archivo CSV

### Estructura de Datos

```typescript
interface ProcessedFile {
  month: string;        // "Mar", "Abr", etc.
  ingreso: number;      // Ingreso del mes
  totalCount?: number;  // Número de transacciones
}
```

## 📁 Estructura del Proyecto

```
baucher-match-frontend-main/
│
├── src/
│   ├── component/
│   │   ├── Dashboard.tsx              # Dashboard con gráficos
│   │   ├── Sidebar.tsx                # Navegación y estado global
│   │   ├── UploadStatement.tsx        # Carga de estados completos
│   │   ├── UploadPartialStatement.tsx # Carga parcial
│   │   └── ui/
│   │       ├── Card.tsx               # Componente Card reutilizable
│   │       └── CardContent.tsx        # Contenido de Card
│   │
│   ├── assets/
│   │   └── react.svg                  # Logo de React
│   │
│   ├── App.tsx                        # Componente raíz
│   ├── main.tsx                       # Entry point
│   ├── App.css                        # Estilos globales
│   └── vite-env.d.ts                  # Types de Vite
│
├── src-tauri/
│   ├── src/
│   │   ├── main.rs                    # Entry point de Tauri
│   │   └── lib.rs                     # Biblioteca Rust
│   │
│   ├── Cargo.toml                     # Dependencias Rust
│   ├── tauri.conf.json                # Configuración Tauri
│   └── icons/                         # Iconos de la aplicación
│
├── public/
│   ├── tauri.svg
│   └── vite.svg
│
├── package.json                       # Dependencias Node.js
├── tsconfig.json                      # Configuración TypeScript
├── vite.config.ts                     # Configuración Vite
└── README.md                          # Este archivo
```

## 📜 Scripts Disponibles

### Desarrollo

```bash
# Ejecutar aplicación de escritorio en modo desarrollo
npm run tauri dev

# Ejecutar solo frontend en navegador
npm run dev

# Compilar TypeScript + Build
npm run build
```

### Producción

```bash
# Preview de build de producción
npm run preview

# Construir aplicación de escritorio
npm run tauri build
```

### Comandos Tauri

```bash
# Inicializar proyecto Tauri
npm run tauri init

# Información del proyecto
npm run tauri info

# Iconos de la aplicación
npm run tauri icon
```

## 🎨 Configuración IDE

### Visual Studio Code (Recomendado)

Extensiones recomendadas:

- [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode)
- [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)
- [ES7+ React/Redux/React-Native snippets](https://marketplace.visualstudio.com/items?itemName=dsznajder.es7-react-js-snippets)
- [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)
- [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin)

### Configuración VSCode

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "typescript.tsdk": "node_modules/typescript/lib",
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

## 📦 Despliegue

### Build de Producción

```bash
npm run tauri build
```

Esto generará ejecutables nativos en:
- **Windows**: `src-tauri/target/release/baucher-match-frontend.exe`
- **macOS**: `src-tauri/target/release/bundle/macos/`
- **Linux**: `src-tauri/target/release/baucher-match-frontend`

### Configuración de Build

Edita `src-tauri/tauri.conf.json` para personalizar:

```json
{
  "productName": "BaucherMatch",
  "version": "0.1.0",
  "identifier": "com.bauchmatch.app",
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": ["icons/icon.png"]
  }
}
```

## 🐛 Solución de Problemas

### Error: npm install falla

**Problema**: Node.js versión antigua (< 14.x)

**Solución**:
```bash
# Actualizar Node.js a v18 LTS
nvm install 18
nvm use 18
npm install
```

### Error: Backend no responde

**Problema**: CORS no configurado

**Solución**: Verificar que el backend exponga los headers:
```python
expose_headers=["X-Execution-Time", "X-Total-Count", "X-json"]
```

### Error: CSV no descarga

**Problema**: Response no es Blob

**Solución**: Verificar que el backend retorne `FileResponse`, no JSON:
```python
return FileResponse(
    path=csv_path,
    filename=filename,
    media_type="text/csv",
    headers={
        "X-Execution-Time": str(execution_time),
        "X-Total-Count": str(total_count),
        "X-json": json.dumps(metadata)
    }
)
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado y propietario.

## 👨‍💻 Autor

**BaucherMatch Team**

## 🙏 Agradecimientos

- React Team por la excelente biblioteca
- Tauri Team por el framework de aplicaciones de escritorio
- Recharts por la biblioteca de gráficos
- Tailwind CSS por el framework de estilos

---

**Versión**: 0.1.0  
**Última actualización**: Octubre 2025
