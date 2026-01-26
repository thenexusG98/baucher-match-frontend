"""
Punto de entrada principal para el backend FastAPI
Este archivo es usado por PyInstaller para empaquetar la aplicación
"""
import sys
import signal
import uvicorn
import logging
from pathlib import Path
from datetime import datetime
import os

# Agregar el directorio app al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from app.app import app

# Configuración de logging para producción
def setup_logging():
    """Configura el sistema de logging para desarrollo y producción"""
    
    # Determinar si estamos en producción (ejecutable empaquetado)
    if getattr(sys, 'frozen', False):
        # Estamos en producción (PyInstaller)
        if sys.platform == 'darwin':  # macOS
            log_dir = Path.home() / 'Library' / 'Logs' / 'BaucherMatch'
        elif sys.platform == 'win32':  # Windows
            log_dir = Path(os.getenv('APPDATA')) / 'BaucherMatch' / 'logs'
        else:  # Linux
            log_dir = Path.home() / '.local' / 'share' / 'BaucherMatch' / 'logs'
    else:
        # Estamos en desarrollo
        log_dir = Path(__file__).parent / 'logs'
    
    # Crear directorio de logs si no existe
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Archivo de log con fecha
    log_file = log_dir / f"backend_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configurar formato de logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar logging tanto a archivo como a consola
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Sistema de logging inicializado. Archivo: {log_file}")
    logger.info(f"Modo: {'Produccion' if getattr(sys, 'frozen', False) else 'Desarrollo'}")
    
    return logger

# Inicializar logging
logger = setup_logging()

def signal_handler(sig, frame):
    """Manejador de senales para cerrar el servidor correctamente"""
    logger.info('[SHUTDOWN] Cerrando backend...')
    sys.exit(0)

# Registrar manejadores de señales
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        logger.info("[START] Iniciando backend FastAPI en http://127.0.0.1:8000")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error fatal al iniciar el backend: {str(e)}", exc_info=True)
        sys.exit(1)
