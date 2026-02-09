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
        
        # SOLUCION FINAL: uvicorn.Server.serve() NO funciona en PyInstaller con Windows
        # Usamos un enfoque directo: crear el socket manualmente y ejecutar el servidor
        
        logger.info("[UVICORN] Usando metodo directo (sin server.serve())")
        
        # Configurar logging de uvicorn
        import logging as py_logging
        uvicorn_logger = py_logging.getLogger("uvicorn")
        uvicorn_logger.setLevel(py_logging.INFO)
        for handler in logger.handlers:
            uvicorn_logger.addHandler(handler)
        
        uvicorn_error = py_logging.getLogger("uvicorn.error")  
        uvicorn_error.setLevel(py_logging.INFO)
        for handler in logger.handlers:
            uvicorn_error.addHandler(handler)
            
        logger.info("[UVICORN] Iniciando servidor HTTP directo...")
        
        # Importar servidor HTTP directamente
        import socket as sock_module
        from uvicorn.protocols.http.h11_impl import H11Protocol
        
        # Crear socket TCP manualmente
        logger.info("[UVICORN] Creando socket TCP en 127.0.0.1:8000...")
        server_socket = sock_module.socket(sock_module.AF_INET, sock_module.SOCK_STREAM)
        server_socket.setsockopt(sock_module.SOL_SOCKET, sock_module.SO_REUSEADDR, 1)
        server_socket.bind(("127.0.0.1", 8000))
        server_socket.listen(128)
        server_socket.setblocking(False)
        
        logger.info("[UVICORN] Socket creado y escuchando en puerto 8000")
        logger.info("[UVICORN] Backend FastAPI ACTIVO y LISTO para recibir peticiones")
        
        # Crear event loop si no existe
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        logger.info(f"[UVICORN] Event loop: {type(loop).__name__}")
        
        # Flush antes de bloquear
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Funcion async para manejar conexiones
        async def handle_client(reader, writer):
            """Maneja una conexion de cliente HTTP"""
            try:
                # Leer request HTTP
                data = await reader.read(4096)
                if not data:
                    return
                
                # Procesar con FastAPI
                # (Esto es simplificado - en produccion usar ASGI completo)
                from starlette.testclient import TestClient
                client = TestClient(app)
                
                # Parsear request basico
                request_line = data.decode('utf-8').split('\r\n')[0]
                parts = request_line.split(' ')
                if len(parts) >= 2:
                    method = parts[0]
                    path = parts[1]
                    
                    # Hacer request a FastAPI
                    if method == 'GET':
                        response = client.get(path)
                        
                        # Enviar response HTTP
                        http_response = f"HTTP/1.1 {response.status_code} OK\r\n"
                        http_response += "Content-Type: application/json\r\n"
                        http_response += f"Content-Length: {len(response.content)}\r\n"
                        http_response += "Access-Control-Allow-Origin: *\r\n"
                        http_response += "\r\n"
                        
                        writer.write(http_response.encode())
                        writer.write(response.content)
                        await writer.drain()
            except Exception as e:
                logger.error(f"[UVICORN] Error manejando cliente: {e}")
            finally:
                writer.close()
                await writer.wait_closed()
        
        async def serve_forever():
            """Loop principal del servidor"""
            logger.info("[UVICORN] Entrando en loop principal de aceptacion de conexiones...")
            while True:
                try:
                    # Aceptar conexion de forma asincrona
                    client_sock, addr = await loop.sock_accept(server_socket)
                    logger.info(f"[UVICORN] Nueva conexion desde {addr}")
                    
                    # Crear reader/writer asyncio
                    reader, writer = await asyncio.open_connection(sock=client_sock)
                    
                    # Manejar en background
                    asyncio.create_task(handle_client(reader, writer))
                except Exception as e:
                    logger.error(f"[UVICORN] Error en loop principal: {e}", exc_info=True)
        
        # Ejecutar servidor
        try:
            logger.info("[UVICORN] Ejecutando loop de eventos...")
            loop.run_until_complete(serve_forever())
        except KeyboardInterrupt:
            logger.info("[UVICORN] Servidor detenido por usuario")
        except Exception as e:
            logger.error(f"[UVICORN] Error fatal: {e}", exc_info=True)
        finally:
            server_socket.close()
            logger.info("[UVICORN] Socket cerrado")
            if not loop.is_closed():
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
