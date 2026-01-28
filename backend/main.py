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
import socket

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

def check_port_available(host, port):
    """Verifica si un puerto esta disponible"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # True si esta disponible (no se pudo conectar)
    except Exception as e:
        logger.error(f"Error verificando puerto: {e}")
        return False

# Registrar manejadores de señales
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        logger.info("[START] Iniciando backend FastAPI en http://127.0.0.1:8000")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Verificar si el puerto ya esta en uso
        if not check_port_available("127.0.0.1", 8000):
            logger.error("[ERROR] Puerto 8000 ya esta en uso!")
            logger.error("[ERROR] Verifica que no haya otra instancia del backend corriendo")
            sys.exit(1)
        else:
            logger.info("[CHECK] Puerto 8000 disponible")
        
        # Verificar que la app FastAPI se importo correctamente
        logger.info(f"[CHECK] App FastAPI cargada: {type(app)}")
        logger.info(f"[CHECK] Uvicorn version: {uvicorn.__version__}")
        
        # Verificar modulos criticos de uvicorn
        try:
            import uvicorn.server
            import uvicorn.config
            logger.info("[CHECK] Modulos de uvicorn importados correctamente")
        except ImportError as ie:
            logger.error(f"[ERROR] Falta modulo de uvicorn: {ie}")
            raise
        
        logger.info("[UVICORN] Creando configuracion del servidor...")
        
        # Crear configuracion de uvicorn manualmente para mejor control
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True,
            use_colors=False,
            loop="asyncio",  # Especificar loop explicito
        )
        
        logger.info("[UVICORN] Creando servidor...")
        server = uvicorn.Server(config)
        
        logger.info("[UVICORN] Iniciando servidor (esto bloqueara el hilo principal)...")
        logger.info("[UVICORN] Si ves este mensaje, uvicorn deberia estar escuchando en http://127.0.0.1:8000")
        
        # Flush logs antes de bloquear
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        # Esto bloqueara hasta que el servidor se detenga
        server.run()
        
        logger.info("[SHUTDOWN] Servidor detenido correctamente")
    except Exception as e:
        logger.error(f"[FATAL] Error al iniciar el backend: {str(e)}", exc_info=True)
        logger.error(f"[FATAL] Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"[FATAL] Traceback completo:\n{traceback.format_exc()}")
        
        # Flush logs antes de salir
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        sys.exit(1)
