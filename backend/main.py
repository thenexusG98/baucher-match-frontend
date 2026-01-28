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
import asyncio

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
        logger.info(f"Frozen (PyInstaller): {getattr(sys, 'frozen', False)}")
        
        # Diagnostico de asyncio ANTES de iniciar uvicorn
        logger.info("[ASYNCIO] Diagnosticando event loop...")
        try:
            # Verificar que asyncio esta disponible
            loop_policy = asyncio.get_event_loop_policy()
            logger.info(f"[ASYNCIO] Event loop policy: {type(loop_policy).__name__}")
            
            # En Windows, asyncio usa ProactorEventLoop por defecto en Python 3.8+
            if sys.platform == 'win32':
                logger.info("[ASYNCIO] Plataforma Windows detectada")
                # Verificar que el loop de Windows esta disponible
                try:
                    import asyncio.windows_events
                    logger.info("[ASYNCIO] asyncio.windows_events disponible")
                except ImportError as e:
                    logger.error(f"[ASYNCIO] ERROR: asyncio.windows_events no disponible: {e}")
            
            # Intentar crear un loop de prueba
            test_loop = asyncio.new_event_loop()
            logger.info(f"[ASYNCIO] Loop de prueba creado: {type(test_loop).__name__}")
            test_loop.close()
            logger.info("[ASYNCIO] Loop de prueba cerrado correctamente")
            
        except Exception as e:
            logger.error(f"[ASYNCIO] ERROR en diagnostico: {e}", exc_info=True)
        
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
        
        logger.info("[UVICORN] Iniciando servidor con asyncio explicito...")
        
        # Flush logs antes de iniciar
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        # IMPORTANTE: uvicorn.run() falla silenciosamente en PyInstaller
        # Usamos el servidor directamente con asyncio manual
        
        logger.info("[UVICORN] Creando configuracion del servidor...")
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True,
            use_colors=False,
            loop="asyncio",
        )
        
        logger.info("[UVICORN] Creando instancia del servidor...")
        server = uvicorn.Server(config)
        
        # Ejecutar el servidor con asyncio explicito
        logger.info("[UVICORN] Iniciando event loop manualmente...")
        
        try:
            # Obtener o crear event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            logger.info(f"[UVICORN] Event loop obtenido: {type(loop).__name__}")
            logger.info("[UVICORN] Ejecutando servidor...")
            
            # Flush antes de bloquear
            sys.stdout.flush()
            sys.stderr.flush()
            
            # Ejecutar el servidor en el loop
            loop.run_until_complete(server.serve())
            
        except KeyboardInterrupt:
            logger.info("[UVICORN] Servidor interrumpido por usuario")
        finally:
            logger.info("[UVICORN] Cerrando event loop...")
            loop.close()
        
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
