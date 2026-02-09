from fastapi import FastAPI
from app.api.routes_transacciones import router as transacciones_router # type: ignore
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",      # Desarrollo Tauri
        "http://127.0.0.1:1420",      # Desarrollo Tauri (127.0.0.1)
        "tauri://localhost",           # Producción Tauri
        "https://tauri.localhost",     # Producción Tauri alternativo
        "http://localhost:8000",       # Peticiones locales al mismo servidor
        "http://127.0.0.1:8000",       # Peticiones locales 127.0.0.1
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Execution-Time", "X-Total-Count", "X-Json"],
)

app.include_router(transacciones_router, prefix="/api/v1", tags=["Transacciones"])

# Endpoint de health en la raiz para debugging
@app.get("/")
async def root():
    """Endpoint raiz - confirma que el servidor esta funcionando"""
    return {"message": "Backend FastAPI funcionando", "version": "1.0.0"}

@app.get("/health")
async def health_root():
    """Endpoint de health en la raiz (sin prefijo)"""
    return {"status": "ok", "message": "Backend activo", "service": "baucher-match-backend"}

#   & 'c:\Users\TheNex\anaconda3\envs\bautcher-match-env\python.exe' 'c:\Users\TheNex\.vscode\extensions\ms-python.debugpy-2025.6.0-win32-x64\bundled\libs\debugpy\launcher' '55071' '--' '-m' 'uvicorn' 'app.app:app' '--reload' 