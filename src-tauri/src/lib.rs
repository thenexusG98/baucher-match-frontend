use serde::{Deserialize, Serialize};
use rusqlite::{Connection, Result as SqlResult};
use std::sync::Mutex;
use tauri::{State, Manager};
use std::path::PathBuf;
use std::process::{Command, Child};
use std::fs::{OpenOptions, create_dir_all};
use std::io::Write;
use chrono::Local;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ProcessedStatement {
    pub id: Option<i64>,
    pub filename: String,
    pub month: String,
    pub year: i32,
    pub ingreso: f64,
    pub total_count: i32,
    pub processed_at: String,
}

pub struct DbState {
    conn: Mutex<Connection>,
}

pub struct BackendProcess {
    child: Mutex<Option<Child>>,
}

// Función para escribir logs
fn log_to_file(message: &str) {
    if let Some(log_path) = get_log_path() {
        if let Ok(mut file) = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&log_path)
        {
            let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S");
            let _ = writeln!(file, "[{}] {}", timestamp, message);
        }
    }
    // También imprimir en consola
    println!("{}", message);
}

// Obtener la ruta del archivo de log
fn get_log_path() -> Option<PathBuf> {
    #[cfg(target_os = "macos")]
    let log_dir = dirs::home_dir()?.join("Library").join("Logs").join("BaucherMatch");
    
    #[cfg(target_os = "windows")]
    let log_dir = dirs::data_dir()?.join("BaucherMatch").join("logs");
    
    #[cfg(target_os = "linux")]
    let log_dir = dirs::home_dir()?.join(".local").join("share").join("BaucherMatch").join("logs");
    
    let _ = create_dir_all(&log_dir);
    
    let today = Local::now().format("%Y%m%d");
    Some(log_dir.join(format!("tauri_{}.log", today)))
}

fn get_db_path(app_handle: &tauri::AppHandle) -> Result<PathBuf, String> {
    let app_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    
    std::fs::create_dir_all(&app_dir)
        .map_err(|e| format!("Failed to create app data dir: {}", e))?;
    
    Ok(app_dir.join("baucher_match.db"))
}

fn init_database(conn: &Connection) -> SqlResult<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS processed_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            month TEXT NOT NULL,
            year INTEGER NOT NULL,
            ingreso REAL NOT NULL,
            total_count INTEGER NOT NULL,
            processed_at TEXT NOT NULL
        )",
        [],
    )?;
    
    // Crear índices para mejorar rendimiento
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_year ON processed_statements(year)",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_month_year ON processed_statements(month, year)",
        [],
    )?;
    
    Ok(())
}

#[tauri::command]
fn add_statement(
    state: State<DbState>,
    filename: String,
    month: String,
    year: i32,
    ingreso: f64,
    total_count: i32,
    processed_at: String,
) -> Result<ProcessedStatement, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    
    conn.execute(
        "INSERT INTO processed_statements (filename, month, year, ingreso, total_count, processed_at)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        [&filename, &month, &year.to_string(), &ingreso.to_string(), &total_count.to_string(), &processed_at],
    )
    .map_err(|e| e.to_string())?;
    
    let id = conn.last_insert_rowid();
    
    Ok(ProcessedStatement {
        id: Some(id),
        filename,
        month,
        year,
        ingreso,
        total_count,
        processed_at,
    })
}

#[tauri::command]
fn get_all_statements(state: State<DbState>) -> Result<Vec<ProcessedStatement>, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    
    let mut stmt = conn
        .prepare("SELECT id, filename, month, year, ingreso, total_count, processed_at FROM processed_statements ORDER BY year DESC, id DESC")
        .map_err(|e| e.to_string())?;
    
    let statements = stmt
        .query_map([], |row| {
            Ok(ProcessedStatement {
                id: Some(row.get(0)?),
                filename: row.get(1)?,
                month: row.get(2)?,
                year: row.get(3)?,
                ingreso: row.get(4)?,
                total_count: row.get(5)?,
                processed_at: row.get(6)?,
            })
        })
        .map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| e.to_string())?;
    
    Ok(statements)
}

#[tauri::command]
fn get_statements_by_year(state: State<DbState>, year: i32) -> Result<Vec<ProcessedStatement>, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    
    let mut stmt = conn
        .prepare("SELECT id, filename, month, year, ingreso, total_count, processed_at FROM processed_statements WHERE year = ?1 ORDER BY id DESC")
        .map_err(|e| e.to_string())?;
    
    let statements = stmt
        .query_map([year], |row| {
            Ok(ProcessedStatement {
                id: Some(row.get(0)?),
                filename: row.get(1)?,
                month: row.get(2)?,
                year: row.get(3)?,
                ingreso: row.get(4)?,
                total_count: row.get(5)?,
                processed_at: row.get(6)?,
            })
        })
        .map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| e.to_string())?;
    
    Ok(statements)
}

#[tauri::command]
fn get_monthly_totals(state: State<DbState>) -> Result<Vec<serde_json::Value>, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    
    let mut stmt = conn
        .prepare(
            "SELECT month, year, SUM(ingreso) as total_ingreso, SUM(total_count) as total_transactions
             FROM processed_statements
             GROUP BY month, year
             ORDER BY year, 
                CASE month
                    WHEN 'Ene' THEN 1
                    WHEN 'Feb' THEN 2
                    WHEN 'Mar' THEN 3
                    WHEN 'Abr' THEN 4
                    WHEN 'May' THEN 5
                    WHEN 'Jun' THEN 6
                    WHEN 'Jul' THEN 7
                    WHEN 'Ago' THEN 8
                    WHEN 'Sep' THEN 9
                    WHEN 'Oct' THEN 10
                    WHEN 'Nov' THEN 11
                    WHEN 'Dic' THEN 12
                END"
        )
        .map_err(|e| e.to_string())?;
    
    let results = stmt
        .query_map([], |row| {
            Ok(serde_json::json!({
                "month": row.get::<_, String>(0)?,
                "year": row.get::<_, i32>(1)?,
                "ingreso": row.get::<_, f64>(2)?,
                "totalCount": row.get::<_, i32>(3)?
            }))
        })
        .map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| e.to_string())?;
    
    Ok(results)
}

#[tauri::command]
fn get_available_years(state: State<DbState>) -> Result<Vec<i32>, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    
    let mut stmt = conn
        .prepare("SELECT DISTINCT year FROM processed_statements ORDER BY year DESC")
        .map_err(|e| e.to_string())?;
    
    let years = stmt
        .query_map([], |row| row.get(0))
        .map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| e.to_string())?;
    
    Ok(years)
}

#[tauri::command]
fn delete_statement(state: State<DbState>, id: i64) -> Result<bool, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    
    conn.execute("DELETE FROM processed_statements WHERE id = ?1", [id])
        .map_err(|e| e.to_string())?;
    
    Ok(true)
}

#[tauri::command]
fn clear_all_statements(state: State<DbState>) -> Result<bool, String> {
    let conn = state.conn.lock().map_err(|e| e.to_string())?;
    
    conn.execute("DELETE FROM processed_statements", [])
        .map_err(|e| e.to_string())?;
    
    Ok(true)
}

#[tauri::command]
fn get_database_path(app_handle: tauri::AppHandle) -> Result<String, String> {
    let db_path = get_db_path(&app_handle)?;
    Ok(db_path.to_string_lossy().to_string())
}

#[tauri::command]
fn get_log_path_command() -> Result<String, String> {
    match get_log_path() {
        Some(path) => Ok(path.to_string_lossy().to_string()),
        None => Err("No se pudo determinar la ruta de logs".to_string())
    }
}

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn start_backend(app_handle: tauri::AppHandle, state: State<BackendProcess>) -> Result<String, String> {
    log_to_file("Intentando iniciar backend...");
    
    let mut child_lock = state.child.lock().map_err(|e| {
        let error_msg = format!("Error al obtener lock del backend: {}", e);
        log_to_file(&error_msg);
        error_msg
    })?;
    
    if child_lock.is_some() {
        log_to_file("Backend ya está corriendo");
        return Ok("Backend ya está corriendo".to_string());
    }
    
    use tauri::Manager;
    
    log_to_file("Resolviendo ruta del backend...");
    
    // Debug: Mostrar todos los directorios base de Tauri
    if let Ok(resource_dir) = app_handle.path().resource_dir() {
        log_to_file(&format!("📁 Resource Dir: {:?}", resource_dir));
        
        // Listar contenido del resource dir
        if resource_dir.exists() {
            log_to_file("Contenido del Resource Dir:");
            if let Ok(entries) = std::fs::read_dir(&resource_dir) {
                for entry in entries.flatten() {
                    log_to_file(&format!("  - {:?}", entry.file_name()));
                }
            }
        } else {
            log_to_file("⚠️ Resource Dir NO EXISTE");
        }
    }
    
    if let Ok(app_data_dir) = app_handle.path().app_data_dir() {
        log_to_file(&format!("📁 App Data Dir: {:?}", app_data_dir));
    }
    
    if let Ok(app_local_dir) = app_handle.path().app_local_data_dir() {
        log_to_file(&format!("📁 App Local Data Dir: {:?}", app_local_dir));
    }
    
    // En Tauri 2.0, los binarios externos se empaquetan en el directorio de recursos
    // Necesitamos construir manualmente la ruta con el sufijo de plataforma correcto
    // NOTA: Tauri renombra los binarios externos a solo el nombre base + .exe en Windows
    #[cfg(target_os = "windows")]
    let binary_filename = "backend-api.exe";
    
    #[cfg(all(target_os = "macos", target_arch = "aarch64"))]
    let binary_filename = "backend-api";
    
    #[cfg(all(target_os = "macos", target_arch = "x86_64"))]
    let binary_filename = "backend-api";
    
    #[cfg(target_os = "linux")]
    let binary_filename = "backend-api";
    
    log_to_file(&format!("Buscando binario: {}", binary_filename));
    
    // Resolver la ruta completa del binario
    // Tauri coloca los external binaries directamente en el resource directory
    let backend_path = app_handle
        .path()
        .resolve(
            binary_filename,  // Buscar directamente, no en subdirectorio
            tauri::path::BaseDirectory::Resource
        )
        .map_err(|e| {
            let error_msg = format!("Error al resolver ruta del backend: {}", e);
            log_to_file(&error_msg);
            error_msg
        })?;
    
    log_to_file(&format!("🚀 Ruta del backend resuelta: {:?}", backend_path));
    
    // Verificar que el archivo existe
    if !backend_path.exists() {
        // Intentar listar los archivos en el directorio para debugging
        if let Some(parent) = backend_path.parent() {
            log_to_file(&format!("Listando archivos en: {:?}", parent));
            
            // Verificar si el directorio padre existe
            if !parent.exists() {
                log_to_file(&format!("ERROR: El directorio {:?} NO EXISTE", parent));
            } else {
                log_to_file(&format!("El directorio {:?} SI existe", parent));
                
                if let Ok(entries) = std::fs::read_dir(parent) {
                    let mut count = 0;
                    for entry in entries.flatten() {
                        count += 1;
                        let metadata = entry.metadata();
                        let size = metadata.as_ref().map(|m| m.len()).unwrap_or(0);
                        log_to_file(&format!("  [{}] Archivo: {:?} (Tamaño: {} bytes)", count, entry.file_name(), size));
                    }
                    if count == 0 {
                        log_to_file("  ⚠️ El directorio está VACÍO - no hay archivos");
                    } else {
                        log_to_file(&format!("  Total de archivos encontrados: {}", count));
                    }
                } else {
                    log_to_file("  ERROR: No se pudo leer el directorio");
                }
            }
        }
        
        let error_msg = format!(
            "El ejecutable del backend no existe en: {:?}. Asegúrate de ejecutar build-backend.bat (Windows) o ./build-backend.sh (Mac/Linux) primero.",
            backend_path
        );
        log_to_file(&error_msg);
        return Err(error_msg);
    }
    
    log_to_file(&format!("✓ Backend encontrado, iniciando proceso..."));
    
    // Obtener el directorio de libs para las DLLs de Poppler
    let libs_dir = if let Ok(resource_dir) = app_handle.path().resource_dir() {
        resource_dir.join("libs")
    } else {
        PathBuf::from("libs")
    };
    
    log_to_file(&format!("📁 Directorio de libs: {:?}", libs_dir));
    
    // En Windows, agregar el directorio de libs al PATH para que encuentre las DLLs
    #[cfg(target_os = "windows")]
    let path_var = if libs_dir.exists() {
        use std::env;
        let mut paths = vec![libs_dir.to_string_lossy().to_string()];
        if let Ok(existing_path) = env::var("PATH") {
            paths.push(existing_path);
        }
        let new_path = paths.join(";");
        log_to_file(&format!("PATH actualizado con libs: {}", new_path));
        Some(("PATH", new_path))
    } else {
        log_to_file(&format!("⚠️ Directorio de libs no existe: {:?}", libs_dir));
        None
    };
    
    // Iniciar proceso
    let mut cmd = Command::new(&backend_path);
    
    #[cfg(target_os = "windows")]
    if let Some((key, value)) = path_var {
        cmd.env(key, value);
    }
    
    let child = cmd.spawn()
        .map_err(|e| {
            let error_msg = format!("Error al iniciar backend: {}. Ruta: {:?}", e, backend_path);
            log_to_file(&error_msg);
            error_msg
        })?;
    
    let pid = child.id();
    let success_msg = format!("✅ Backend iniciado con PID: {}", pid);
    log_to_file(&success_msg);
    
    *child_lock = Some(child);
    
    // Esperar un momento para verificar que el proceso no falle inmediatamente
    std::thread::sleep(std::time::Duration::from_millis(500));
    
    // Verificar si el proceso sigue vivo
    if let Some(ref mut child) = *child_lock {
        match child.try_wait() {
            Ok(Some(status)) => {
                let error_msg = format!("⚠️ El backend terminó inmediatamente con código: {:?}", status);
                log_to_file(&error_msg);
                *child_lock = None;
                return Err(format!("El backend falló al iniciar. Código de salida: {:?}. Revisa los logs en AppData\\Roaming\\BaucherMatch\\logs", status));
            }
            Ok(None) => {
                log_to_file(&format!("✓ Backend corriendo correctamente con PID: {}", pid));
            }
            Err(e) => {
                log_to_file(&format!("⚠️ Error verificando estado del backend: {}", e));
            }
        }
    }
    
    // Segunda verificación después de 5 segundos (tiempo para que uvicorn inicie)
    std::thread::sleep(std::time::Duration::from_secs(5));
    
    if let Some(ref mut child) = *child_lock {
        match child.try_wait() {
            Ok(Some(status)) => {
                let error_msg = format!("⚠️ El backend terminó después de 5 segundos con código: {:?}", status);
                log_to_file(&error_msg);
                log_to_file("💡 Posible causa: Error al iniciar uvicorn o al cargar módulos de Python");
                *child_lock = None;
                return Err(format!("El backend falló después de iniciar. Código de salida: {:?}. Revisa los logs del backend en AppData\\Roaming\\BaucherMatch\\logs", status));
            }
            Ok(None) => {
                log_to_file("✓ Backend sigue activo después de 5 segundos - uvicorn probablemente iniciado correctamente");
            }
            Err(e) => {
                log_to_file(&format!("⚠️ Error en segunda verificación: {}", e));
            }
        }
    }
    
    Ok("Backend iniciado correctamente en http://127.0.0.1:8000".to_string())
}

#[tauri::command]
fn stop_backend(state: State<BackendProcess>) -> Result<String, String> {
    log_to_file("Intentando detener backend...");
    
    let mut child_lock = state.child.lock().map_err(|e| {
        let error_msg = format!("Error al obtener lock del backend: {}", e);
        log_to_file(&error_msg);
        error_msg
    })?;
    
    if let Some(mut child) = child_lock.take() {
        child.kill().map_err(|e| {
            let error_msg = format!("Error al detener backend: {}", e);
            log_to_file(&error_msg);
            error_msg
        })?;
        log_to_file("🛑 Backend detenido correctamente");
        Ok("Backend detenido".to_string())
    } else {
        Ok("Backend no está corriendo".to_string())
    }
}

#[tauri::command]
fn check_backend_status(state: State<BackendProcess>) -> Result<bool, String> {
    let child_lock = state.child.lock().map_err(|e| e.to_string())?;
    Ok(child_lock.is_some())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    log_to_file("=== Iniciando aplicación BaucherMatch ===");
    
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            log_to_file("Configurando aplicación...");
            
            let db_path = get_db_path(&app.handle())?;
            log_to_file(&format!("Database path: {:?}", db_path));
            
            let conn = Connection::open(&db_path)
                .map_err(|e| {
                    let error_msg = format!("Failed to open database: {}", e);
                    log_to_file(&error_msg);
                    error_msg
                })?;
            
            init_database(&conn)
                .map_err(|e| {
                    let error_msg = format!("Failed to initialize database: {}", e);
                    log_to_file(&error_msg);
                    error_msg
                })?;
            
            log_to_file("Base de datos inicializada correctamente");
            
            app.manage(DbState {
                conn: Mutex::new(conn),
            });
            
            // Inicializar el estado del proceso del backend
            app.manage(BackendProcess {
                child: Mutex::new(None),
            });
            
            log_to_file("Setup completado exitosamente");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            add_statement,
            get_all_statements,
            get_statements_by_year,
            get_monthly_totals,
            get_available_years,
            delete_statement,
            clear_all_statements,
            get_database_path,
            start_backend,
            stop_backend,
            check_backend_status,
            get_log_path_command
        ])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                log_to_file("Cerrando aplicación...");
                // Detener backend al cerrar ventana
                let app = window.app_handle();
                if let Some(backend_state) = app.try_state::<BackendProcess>() {
                    let _ = stop_backend(backend_state);
                }
                log_to_file("Backend detenido");
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
