"""
PDF Text Extractor usando pdftotext.exe (Poppler) via subprocess.
Usa el ejecutable pdftotext de Poppler para extraer texto de PDFs.
Fallback a PyMuPDF solo si pdftotext.exe no se encuentra.
"""
import logging
import subprocess
import tempfile
import os
import sys
import shutil

logger = logging.getLogger(__name__)

# ============================================================
# Buscar pdftotext.exe en varias ubicaciones
# ============================================================
def _find_pdftotext_exe():
    """
    Busca el ejecutable pdftotext en:
    1. Directorio del ejecutable PyInstaller (_MEIPASS o junto al .exe)
    2. Subdirectorio 'poppler' junto al ejecutable
    3. PATH del sistema
    """
    candidates = []
    
    exe_name = "pdftotext.exe" if sys.platform == "win32" else "pdftotext"
    
    # 1. Dentro del bundle de PyInstaller (_MEIPASS)
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        candidates.append(os.path.join(base_dir, "poppler", exe_name))
        candidates.append(os.path.join(base_dir, exe_name))
        # También junto al ejecutable real
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "poppler", exe_name))
        candidates.append(os.path.join(exe_dir, exe_name))
    else:
        # En desarrollo, buscar en el directorio del proyecto
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates.append(os.path.join(project_dir, "poppler", exe_name))
        candidates.append(os.path.join(project_dir, "bin", exe_name))
    
    # 2. Buscar en cada candidato
    for path in candidates:
        logger.info(f"[PDF-EXTRACTOR] Buscando pdftotext en: {path}")
        if os.path.isfile(path):
            logger.info(f"[PDF-EXTRACTOR] ✓ Encontrado pdftotext en: {path}")
            return path
    
    # 3. Buscar en el PATH del sistema
    found = shutil.which(exe_name)
    if found:
        logger.info(f"[PDF-EXTRACTOR] ✓ Encontrado pdftotext en PATH: {found}")
        return found
    
    logger.warning(f"[PDF-EXTRACTOR] ✗ pdftotext NO encontrado en ninguna ubicación")
    return None


PDFTOTEXT_EXE = _find_pdftotext_exe()

if PDFTOTEXT_EXE:
    USE_PDFTOTEXT = True
    logger.info(f"[PDF-EXTRACTOR] ★ Usando pdftotext.exe como backend principal: {PDFTOTEXT_EXE}")
else:
    USE_PDFTOTEXT = False
    try:
        import fitz  # PyMuPDF
        logger.warning("[PDF-EXTRACTOR] pdftotext.exe no encontrado, usando PyMuPDF como fallback")
    except ImportError:
        logger.error("[PDF-EXTRACTOR] ¡CRITICO! Ni pdftotext.exe ni PyMuPDF están disponibles")
        raise ImportError("No se encontró pdftotext.exe ni PyMuPDF. No se pueden procesar PDFs.")


def _extract_with_pdftotext_exe(pdf_file_path, physical=False):
    """
    Extrae texto de un PDF usando el ejecutable pdftotext de Poppler.
    
    Args:
        pdf_file_path: Ruta al archivo PDF en disco
        physical: Si True, usa -layout para mantener posiciones
    
    Returns:
        Lista de strings, uno por página
    """
    pages = []
    
    # Obtener el directorio donde está pdftotext.exe para agregar al PATH
    pdftotext_dir = os.path.dirname(PDFTOTEXT_EXE)
    env = os.environ.copy()
    # Asegurar que el directorio de pdftotext.exe esté en el PATH (para DLLs)
    if sys.platform == "win32":
        env["PATH"] = pdftotext_dir + ";" + env.get("PATH", "")
    else:
        env["PATH"] = pdftotext_dir + ":" + env.get("PATH", "")
    
    # Primero, obtener el número de páginas extrayendo todo el texto
    cmd = [PDFTOTEXT_EXE]
    if physical:
        cmd.append("-layout")
    cmd.extend(["-enc", "UTF-8", pdf_file_path, "-"])
    
    logger.info(f"[PDF-EXTRACTOR] Ejecutando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=60,
            env=env
        )
        
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace')
            logger.error(f"[PDF-EXTRACTOR] pdftotext.exe error (code {result.returncode}): {stderr}")
            raise RuntimeError(f"pdftotext falló con código {result.returncode}: {stderr}")
        
        # pdftotext separa las páginas con form-feed (\f)
        full_text = result.stdout.decode('utf-8', errors='replace')
        pages = full_text.split('\f')
        
        # Remover la última entrada vacía (pdftotext agrega \f al final)
        if pages and pages[-1].strip() == '':
            pages = pages[:-1]
        
        logger.info(f"[PDF-EXTRACTOR] pdftotext.exe extrajo {len(pages)} páginas exitosamente")
        
        for i, page in enumerate(pages):
            logger.debug(f"[PDF-EXTRACTOR] Página {i+1}: {len(page)} caracteres")
        
    except subprocess.TimeoutExpired:
        logger.error("[PDF-EXTRACTOR] pdftotext.exe timeout (60s)")
        raise RuntimeError("pdftotext tardó demasiado en procesar el PDF")
    except FileNotFoundError:
        logger.error(f"[PDF-EXTRACTOR] No se encontró el ejecutable: {PDFTOTEXT_EXE}")
        raise
    
    return pages


class PDF:
    """
    Wrapper que proporciona la misma interfaz que pdftotext.PDF
    Usa pdftotext.exe (Poppler) via subprocess como backend principal.
    Fallback a PyMuPDF si pdftotext.exe no está disponible.
    """
    
    def __init__(self, file, physical=False):
        """
        Args:
            file: file object opened in binary mode
            physical: bool - usar layout físico (mantiene posiciones)
        """
        backend_name = 'pdftotext.exe' if USE_PDFTOTEXT else 'PyMuPDF'
        logger.info(f"[PDF-EXTRACTOR] Inicializando PDF (physical={physical}, backend={backend_name})")
        self.physical = physical
        self.pages = []
        
        try:
            if USE_PDFTOTEXT:
                # Guardar el contenido del file a un archivo temporal
                logger.info("[PDF-EXTRACTOR] Usando pdftotext.exe para extraer texto...")
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name
                
                try:
                    self.pages = _extract_with_pdftotext_exe(tmp_path, physical=physical)
                finally:
                    # Limpiar archivo temporal
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
            else:
                # Fallback: Usar PyMuPDF
                logger.info("[PDF-EXTRACTOR] Usando PyMuPDF para extraer texto (fallback)...")
                import fitz
                pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
                logger.info(f"[PDF-EXTRACTOR] PyMuPDF abrió documento con {len(pdf_doc)} páginas")
                
                for page_num in range(len(pdf_doc)):
                    page = pdf_doc[page_num]
                    
                    if physical:
                        text = page.get_text("text", sort=True)
                        logger.info(f"[PDF-EXTRACTOR] Página {page_num + 1} extraída con layout físico ({len(text)} caracteres)")
                    else:
                        text = page.get_text()
                        logger.info(f"[PDF-EXTRACTOR] Página {page_num + 1} extraída modo simple ({len(text)} caracteres)")
                    
                    self.pages.append(text)
                
                pdf_doc.close()
                logger.info(f"[PDF-EXTRACTOR] PyMuPDF completó extracción de {len(self.pages)} páginas")
        except Exception as e:
            logger.error(f"[PDF-EXTRACTOR] Error durante extracción: {str(e)}", exc_info=True)
            raise
    
    def __iter__(self):
        """Permite iterar sobre las páginas"""
        return iter(self.pages)
    
    def __len__(self):
        """Retorna el número de páginas"""
        return len(self.pages)
    
    def __getitem__(self, index):
        """Permite acceder a páginas por índice"""
        return self.pages[index]


def get_pdf_backend():
    """Retorna el nombre del backend en uso"""
    return "pdftotext.exe (Poppler)" if USE_PDFTOTEXT else "PyMuPDF"
