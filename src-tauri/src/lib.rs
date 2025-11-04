use serde::{Deserialize, Serialize};
use rusqlite::{Connection, Result as SqlResult};
use std::sync::Mutex;
use tauri::{State, Manager};
use std::path::PathBuf;

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

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let db_path = get_db_path(&app.handle())?;
            println!("Database path: {:?}", db_path);
            
            let conn = Connection::open(&db_path)
                .map_err(|e| format!("Failed to open database: {}", e))?;
            
            init_database(&conn)
                .map_err(|e| format!("Failed to initialize database: {}", e))?;
            
            app.manage(DbState {
                conn: Mutex::new(conn),
            });
            
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
            get_database_path
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
