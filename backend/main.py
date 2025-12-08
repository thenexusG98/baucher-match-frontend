"""
Punto de entrada principal para el backend FastAPI
Este archivo es usado por PyInstaller para empaquetar la aplicación
"""
import sys
import signal
import uvicorn
from pathlib import Path

# Agregar el directorio app al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from app.app import app

def signal_handler(sig, frame):
    """Manejador de señales para cerrar el servidor correctamente"""
    print('🛑 Cerrando backend...')
    sys.exit(0)

# Registrar manejadores de señales
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("🚀 Iniciando backend FastAPI en http://127.0.0.1:8000")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
