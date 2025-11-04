# 📊 Configuración de Base de Datos - BaucherMatch

## 🎯 Resumen

Se ha implementado un sistema de persistencia de datos usando **SQLite** (mediante Rust/rusqlite) para almacenar los estados de cuenta procesados con información de mes, año e ingresos.

> **⚠️ ACTUALIZACIÓN:** Este proyecto ahora usa **SQLite nativo** en lugar de LocalStorage. Para documentación completa de SQLite, ver `SQLITE_SETUP.md`

## 🏗️ Arquitectura

### Servicio de Base de Datos (`src/services/database.ts`)

El servicio de base de datos proporciona las siguientes funcionalidades usando comandos Tauri que se comunican con Rust:

#### 📦 Estructura de Datos

```typescript
interface ProcessedStatement {
  id?: number;            // ID único auto-generado por SQLite
  filename: string;        // Nombre del archivo CSV procesado
  month: string;          // Mes en formato "Ene", "Feb", "Mar", etc.
  year: number;           // Año (ejemplo: 2024, 2025)
  ingreso: number;        // Ingreso total del mes
  totalCount: number;     // Número de transacciones detectadas
  processedAt: string;    // Timestamp ISO del procesamiento
}
```

### 🗄️ Base de Datos SQLite

La base de datos se almacena en un archivo real en el sistema:

- **macOS**: `~/Library/Application Support/com.baucher-match-frontend.app/baucher_match.db`
- **Windows**: `C:\Users\<usuario>\AppData\Roaming\com.baucher-match-frontend.app\baucher_match.db`
- **Linux**: `~/.local/share/com.baucher-match-frontend.app/baucher_match.db`

### 🔧 Métodos Disponibles

Todos los métodos son **asíncronos** y retornan Promesas:

#### `getAllStatements(): Promise<ProcessedStatement[]>`
Obtiene todas las declaraciones guardadas en la base de datos.

```typescript
const statements = await db.getAllStatements();
console.log(statements);
// [{ id: 1, filename: "ESTADO_MARZO_2024.csv", month: "Mar", year: 2024, ... }]
```

#### `addStatement(statement): Promise<ProcessedStatement>`
Agrega una nueva declaración a la base de datos.

```typescript
const newStatement = await db.addStatement({
  filename: "ESTADO_MARZO_2024.csv",
  month: "Mar",
  year: 2024,
  ingreso: 15000.50,
  totalCount: 45,
  processedAt: new Date().toISOString()
});
```

#### `getStatementsByYear(year): Promise<ProcessedStatement[]>`
Filtra declaraciones por año específico.

```typescript
const statements2024 = await db.getStatementsByYear(2024);
```

#### `getMonthlyTotals(): Promise<Array<{ month, year, ingreso, totalCount }>>`
Obtiene el total de ingresos agrupados por mes y año.

```typescript
const totals = await db.getMonthlyTotals();
// [
//   { month: "Ene", year: 2024, ingreso: 12000, totalCount: 30 },
//   { month: "Feb", year: 2024, ingreso: 15000, totalCount: 35 },
//   ...
// ]
```

#### `getAvailableYears(): Promise<number[]>`
Obtiene lista de años únicos disponibles (ordenados descendentemente).

```typescript
const years = await db.getAvailableYears();
// [2025, 2024, 2023]
```

#### `deleteStatement(id): Promise<boolean>`
Elimina una declaración por su ID.

```typescript
await db.deleteStatement(1);
```

#### `clearAll(): Promise<boolean>`
Limpia toda la base de datos.

```typescript
await db.clearAll();
```

#### `getDatabasePath(): Promise<string>`
Obtiene la ruta completa del archivo de base de datos.

```typescript
const path = await db.getDatabasePath();
console.log('Base de datos en:', path);
```

## 🔄 Flujo de Datos

### 1. Usuario Carga un PDF

```
UploadStatement.tsx
    ↓
handleUpload() → Procesa PDF con Backend
    ↓
Extrae: mes, año, ingreso, totalCount
    ↓
db.addStatement({...}) → Guarda en LocalStorage
    ↓
onFileProcessed() → Notifica a Sidebar
    ↓
Sidebar actualiza processedFiles
    ↓
Dashboard recibe nueva data
```

### 2. Dashboard Visualiza Datos

```
Dashboard.tsx
    ↓
useEffect() → Se monta el componente
    ↓
db.getAvailableYears() → Obtiene años [2025, 2024, ...]
    ↓
db.getMonthlyTotals() → Obtiene totales por mes/año
    ↓
Filtra por año seleccionado
    ↓
setChartData() → Actualiza gráfico
    ↓
Recharts renderiza BarChart
```

## 📝 Cambios Implementados

### `src/services/database.ts` (NUEVO)
- ✅ Servicio de base de datos completo con LocalStorage
- ✅ Métodos CRUD (Create, Read, Update, Delete)
- ✅ Agrupación y filtrado por mes/año
- ✅ Cálculo de totales mensuales
- ✅ Extracción automática de año desde nombre de archivo

### `src/component/UploadStatement.tsx` (MODIFICADO)
- ✅ Importa servicio de base de datos
- ✅ Extrae año del nombre del archivo usando `db.extractYearFromFilename()`
- ✅ Guarda datos en DB después de procesar: `db.addStatement({...})`
- ✅ Mantiene funcionalidad existente (descarga CSV, historial, etc.)

### `src/component/Dashboard.tsx` (MODIFICADO)
- ✅ Importa servicio de base de datos
- ✅ Agrega estado para año seleccionado: `useState<number>()`
- ✅ Carga años disponibles: `useEffect(() => db.getAvailableYears())`
- ✅ Filtra datos por año: `db.getMonthlyTotals().filter()`
- ✅ Selector de año en UI: `<select>` para cambiar año
- ✅ Muestra 12 meses completos (Ene-Dic) con datos reales o 0
- ✅ Tooltip actualizado con año: `{month} {year}`

## 🎨 Nuevas Características UI

### Selector de Año en Dashboard

```tsx
<select
  value={selectedYear}
  onChange={(e) => setSelectedYear(Number(e.target.value))}
>
  {availableYears.map((year) => (
    <option key={year} value={year}>{year}</option>
  ))}
</select>
```

### Gráfico con 12 Meses Completos

Ahora el gráfico muestra todos los meses del año (Ene-Dic) en lugar de solo 6 meses:

```typescript
const defaultData = [
  { month: "Ene", ingreso: 0 },
  { month: "Feb", ingreso: 0 },
  // ... hasta Dic
];
```

### Tooltip Mejorado

Ahora incluye el año seleccionado:

```
Mar 2024
Ingreso: $15,000
```

## 💾 Persistencia de Datos

Los datos se guardan automáticamente en **LocalStorage** del navegador:

- **Clave**: `baucher_match_statements`
- **Formato**: JSON array de objetos `ProcessedStatement`
- **Persistencia**: Los datos permanecen incluso después de cerrar la aplicación
- **Capacidad**: ~5-10MB (suficiente para miles de registros)

### Ver Datos en DevTools

1. Abre DevTools (F12)
2. Ve a la pestaña **Application** (Chrome) o **Storage** (Firefox)
3. Navega a **Local Storage** → `http://localhost:1420`
4. Busca la clave: `baucher_match_statements`

## 🔍 Ejemplo de Uso Completo

### 1. Cargar un Estado de Cuenta

```typescript
// Usuario sube: "ESTADO_DE_CUENTA_MARZO_2024.pdf"
// Backend procesa y devuelve headers:
{
  "X-json": {
    "income_month": 25000.75,
    "total_count": 120
  }
}

// UploadStatement guarda en DB:
db.addStatement({
  filename: "ESTADO_DE_CUENTA_MARZO_2024.csv",
  month: "Mar",
  year: 2024,  // Extraído del filename
  ingreso: 25000.75,
  totalCount: 120,
  processedAt: "2025-11-04T18:30:00.000Z"
});
```

### 2. Visualizar en Dashboard

```typescript
// Dashboard carga años disponibles
const years = db.getAvailableYears();
// [2025, 2024]

// Usuario selecciona 2024
// Dashboard carga datos del año
const data2024 = db.getMonthlyTotals().filter(item => item.year === 2024);
// [
//   { month: "Mar", year: 2024, ingreso: 25000.75, totalCount: 120 }
// ]

// Gráfico muestra:
// Ene: 0, Feb: 0, Mar: 25,000.75, Abr: 0, ..., Dic: 0
```

## 🚀 Próximas Mejoras Sugeridas

### Opcional: Migrar a SQLite con Tauri

Si en el futuro necesitas más capacidad o funcionalidades avanzadas:

1. Instalar plugin SQL de Tauri:
```bash
npm install @tauri-apps/plugin-sql
```

2. Configurar en `src-tauri/Cargo.toml`:
```toml
tauri-plugin-sql = { version = "2", features = ["sqlite"] }
```

3. Migrar servicio de base de datos a SQL:
```typescript
import Database from '@tauri-apps/plugin-sql';
const db = await Database.load('sqlite:baucher.db');
```

### Otras Mejoras

- ✨ **Exportar datos**: Botón para exportar toda la DB a CSV/JSON
- 🔍 **Búsqueda avanzada**: Filtrar por rango de fechas, montos, etc.
- 📊 **Más gráficos**: Gráfico de líneas, gráfico de pastel por categorías
- 🗑️ **Gestión de datos**: UI para eliminar registros individuales
- 📈 **Estadísticas**: Totales anuales, promedios mensuales, tendencias

## 🐛 Troubleshooting

### Datos no se guardan

**Problema**: LocalStorage puede estar bloqueado por el navegador.

**Solución**: 
- Verifica que las cookies/localStorage estén habilitados
- Revisa la consola del navegador para errores

### Datos se pierden al recompilar

**Problema**: Tauri limpia localStorage en modo desarrollo.

**Solución**:
- Los datos se mantienen entre recargas de página
- Si se pierden, es normal en desarrollo
- En producción (build) los datos persisten correctamente

### Gráfico no actualiza

**Problema**: React no detecta cambios en localStorage.

**Solución**:
- El Dashboard usa `processedFiles` como dependencia de `useEffect`
- Cada vez que se procesa un archivo, Sidebar actualiza `processedFiles`
- Esto fuerza re-render del Dashboard

## 📚 Recursos

- [LocalStorage MDN](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [Tauri SQL Plugin](https://tauri.app/v2/reference/js/sql/)
- [Recharts Documentation](https://recharts.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Fecha de implementación**: 4 de noviembre de 2025  
**Versión**: 1.0.0
