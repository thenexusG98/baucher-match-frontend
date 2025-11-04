# ✅ Verificación de SQLite - Checklist

## 🎯 Pasos para Verificar la Implementación

### 1. ✅ Compilación Exitosa

- [x] Backend Rust compilado sin errores
- [x] Frontend TypeScript compilado sin errores
- [x] Aplicación ejecutándose con `npm run tauri dev`

### 2. 🔍 Verificar Conexión a SQLite

Abre DevTools (F12) y ejecuta:

```javascript
// Importar servicio
import { db } from './services/database';

// Verificar ruta de DB
const path = await db.getDatabasePath();
console.log('✅ Base de datos ubicada en:', path);
// Debe mostrar: /Users/.../Application Support/com.baucher-match-frontend.app/baucher_match.db
```

**Resultado Esperado:**
```
✅ Base de datos ubicada en: /Users/uriel.gonzalez/Library/Application Support/com.baucher-match-frontend.app/baucher_match.db
```

---

### 3. 📝 Probar Inserción de Datos

```javascript
// Agregar un registro de prueba
const testData = await db.addStatement({
  filename: "TEST_ENERO_2025.csv",
  month: "Ene",
  year: 2025,
  ingreso: 99999.99,
  totalCount: 999,
  processedAt: new Date().toISOString()
});

console.log('✅ Dato insertado:', testData);
```

**Resultado Esperado:**
```javascript
{
  id: 1,
  filename: "TEST_ENERO_2025.csv",
  month: "Ene",
  year: 2025,
  ingreso: 99999.99,
  totalCount: 999,
  processedAt: "2025-11-04T19:00:00.000Z"
}
```

---

### 4. 📊 Verificar Obtención de Datos

```javascript
// Obtener todos los registros
const all = await db.getAllStatements();
console.table(all);
```

**Resultado Esperado:**
```
┌─────────┬────┬──────────────────────┬───────┬──────┬──────────┬────────────┐
│ (index) │ id │      filename        │ month │ year │ ingreso  │ totalCount │
├─────────┼────┼──────────────────────┼───────┼──────┼──────────┼────────────┤
│    0    │ 1  │ TEST_ENERO_2025.csv  │  Ene  │ 2025 │ 99999.99 │    999     │
└─────────┴────┴──────────────────────┴───────┴──────┴──────────┴────────────┘
```

---

### 5. 🔢 Verificar Totales Mensuales

```javascript
// Obtener totales agrupados
const totals = await db.getMonthlyTotals();
console.table(totals);
```

**Resultado Esperado:**
```
┌─────────┬───────┬──────┬──────────┬────────────┐
│ (index) │ month │ year │ ingreso  │ totalCount │
├─────────┼───────┼──────┼──────────┼────────────┤
│    0    │  Ene  │ 2025 │ 99999.99 │    999     │
└─────────┴───────┴──────┴──────────┴────────────┘
```

---

### 6. 📅 Verificar Años Disponibles

```javascript
// Obtener años
const years = await db.getAvailableYears();
console.log('✅ Años disponibles:', years);
```

**Resultado Esperado:**
```
✅ Años disponibles: [2025]
```

---

### 7. 🗑️ Verificar Eliminación

```javascript
// Eliminar el registro de prueba
const deleted = await db.deleteStatement(1);
console.log('✅ Registro eliminado:', deleted);

// Verificar que se eliminó
const remaining = await db.getAllStatements();
console.log('✅ Registros restantes:', remaining.length);
```

**Resultado Esperado:**
```
✅ Registro eliminado: true
✅ Registros restantes: 0
```

---

### 8. 🎨 Verificar UI Dashboard

1. **Ir a "Inicio"** en el menú lateral
2. **Verificar selector de año**:
   - Debe mostrar años desde 2020 hasta 2027
   - Debe poder seleccionar cualquier año

3. **Gráfico**:
   - Debe mostrar 12 meses (Ene-Dic)
   - Si no hay datos, todos los meses deben estar en $0

---

### 9. 📤 Probar Flujo Completo

#### Paso A: Cargar un Archivo PDF

1. Ve a **"Cargar estado de cuenta"**
2. Selecciona un PDF de estado de cuenta
3. Haz clic en **"Subir y Procesar"**
4. Verifica que:
   - ✅ El CSV se descarga
   - ✅ Muestra "Transacciones detectadas"
   - ✅ Muestra "Archivo analizado" con nombre y tiempo

#### Paso B: Verificar en DevTools

```javascript
// Verificar que se guardó en SQLite
const all = await db.getAllStatements();
console.log('✅ Total de archivos procesados:', all.length);
console.table(all);
```

#### Paso C: Verificar Dashboard

1. Ve a **"Inicio"**
2. Selecciona el año del archivo que cargaste
3. Verifica que:
   - ✅ El gráfico muestra el ingreso en el mes correcto
   - ✅ El tooltip muestra el mes y año
   - ✅ El valor del ingreso es correcto

---

### 10. 🔁 Verificar Persistencia

#### Paso A: Cerrar y Reabrir la App

1. Cierra la aplicación completamente
2. Vuelve a ejecutar: `npm run tauri dev`
3. Ve a **"Inicio"**

#### Paso B: Verificar Datos

```javascript
// Los datos deben seguir ahí
const all = await db.getAllStatements();
console.log('✅ Datos persistidos:', all.length > 0);
console.table(all);
```

**Resultado Esperado:**
```
✅ Datos persistidos: true
```

---

### 11. 📁 Verificar Archivo de Base de Datos

#### macOS

```bash
# Ver el archivo
ls -lh ~/Library/Application\ Support/com.baucher-match-frontend.app/baucher_match.db

# Ver tamaño
du -h ~/Library/Application\ Support/com.baucher-match-frontend.app/baucher_match.db
```

**Resultado Esperado:**
```
-rw-r--r--  1 user  staff   12K Nov  4 19:00 baucher_match.db
```

#### Consultar con SQLite CLI

```bash
# Abrir base de datos
sqlite3 ~/Library/Application\ Support/com.baucher-match-frontend.app/baucher_match.db

# Verificar tabla
.tables
# Debe mostrar: processed_statements

# Contar registros
SELECT COUNT(*) FROM processed_statements;

# Ver todos
SELECT * FROM processed_statements;

# Salir
.exit
```

---

## ✅ Checklist de Verificación

Marca cada item cuando lo verifiques:

- [ ] **Compilación Backend**: Rust compila sin errores
- [ ] **Compilación Frontend**: TypeScript compila sin errores
- [ ] **App Ejecuta**: Se abre sin errores
- [ ] **Conexión SQLite**: `getDatabasePath()` retorna ruta válida
- [ ] **Inserción**: `addStatement()` funciona
- [ ] **Lectura**: `getAllStatements()` retorna datos
- [ ] **Totales**: `getMonthlyTotals()` agrupa correctamente
- [ ] **Años**: `getAvailableYears()` retorna lista
- [ ] **Eliminación**: `deleteStatement()` funciona
- [ ] **Dashboard UI**: Selector de año visible
- [ ] **Gráfico**: Muestra 12 meses
- [ ] **Upload**: Cargar PDF guarda en SQLite
- [ ] **Persistencia**: Datos se mantienen al cerrar/abrir
- [ ] **Archivo .db**: Existe en el sistema de archivos
- [ ] **SQLite CLI**: Puede consultar la DB

---

## 🎯 Casos de Prueba Adicionales

### Test 1: Múltiples Archivos del Mismo Mes

```javascript
// Agregar 2 archivos de Marzo 2024
await db.addStatement({
  filename: "MARZO_2024_v1.csv",
  month: "Mar",
  year: 2024,
  ingreso: 10000,
  totalCount: 50,
  processedAt: new Date().toISOString()
});

await db.addStatement({
  filename: "MARZO_2024_v2.csv",
  month: "Mar",
  year: 2024,
  ingreso: 15000,
  totalCount: 60,
  processedAt: new Date().toISOString()
});

// Verificar que suma ambos
const totals = await db.getMonthlyTotals();
const marzo = totals.find(t => t.month === 'Mar' && t.year === 2024);
console.log('✅ Total Marzo:', marzo);
// Debe mostrar: { month: 'Mar', year: 2024, ingreso: 25000, totalCount: 110 }
```

### Test 2: Múltiples Años

```javascript
// Agregar archivos de diferentes años
await db.addStatement({ filename: "2023.csv", month: "Ene", year: 2023, ingreso: 1000, totalCount: 10, processedAt: new Date().toISOString() });
await db.addStatement({ filename: "2024.csv", month: "Ene", year: 2024, ingreso: 2000, totalCount: 20, processedAt: new Date().toISOString() });
await db.addStatement({ filename: "2025.csv", month: "Ene", year: 2025, ingreso: 3000, totalCount: 30, processedAt: new Date().toISOString() });

// Verificar años
const years = await db.getAvailableYears();
console.log('✅ Años:', years);
// Debe mostrar: [2025, 2024, 2023]
```

### Test 3: Filtrar por Año

```javascript
// Obtener solo 2024
const data2024 = await db.getStatementsByYear(2024);
console.log('✅ Registros 2024:', data2024.length);
console.table(data2024);
```

---

## 🐛 Errores Comunes y Soluciones

### Error: "Cannot read properties of undefined"

**Causa**: Olvidaste importar el servicio

**Solución**:
```typescript
import { db } from './services/database';
```

### Error: "Promise <pending>"

**Causa**: Olvidaste usar `await`

**Solución**:
```typescript
// ❌ Incorrecto
const data = db.getAllStatements();

// ✅ Correcto
const data = await db.getAllStatements();
```

### Error: "Failed to invoke command"

**Causa**: Backend Rust no compiló

**Solución**:
```bash
cargo build --manifest-path=src-tauri/Cargo.toml
npm run tauri dev
```

---

## 🎊 Si Todo Funciona...

¡Felicidades! 🎉 Tu implementación de SQLite está completamente funcional.

**Ahora puedes:**
- ✅ Procesar archivos PDF y guardar en SQLite
- ✅ Visualizar datos en el Dashboard
- ✅ Cambiar de navegador sin perder datos
- ✅ Exportar/importar la base de datos
- ✅ Consultar con SQL directamente
- ✅ Hacer backups fácilmente

---

**Fecha**: 4 de noviembre de 2025  
**Estado**: ✅ Verificación Completa
