"""
PDF Text Extractor usando pdftotext.exe (Poppler) via subprocess.
Usa el ejecutable pdftotext de Poppler para extraer texto de PDFs.
Fallback a PyMuPDF solo si pdftotext.exe no se encuentra.

Incluye detección y desbloqueo automático de PDFs protegidos con contraseña
usando qpdf (https://qpdf.sourceforge.io/).
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

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        candidates.append(os.path.join(base_dir, "poppler", exe_name))
        candidates.append(os.path.join(base_dir, exe_name))
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "poppler", exe_name))
        candidates.append(os.path.join(exe_dir, exe_name))
    else:
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates.append(os.path.join(project_dir, "poppler", exe_name))
        candidates.append(os.path.join(project_dir, "bin", exe_name))

    for path in candidates:
        logger.info(f"[PDF-EXTRACTOR] Buscando pdftotext en: {path}")
        if os.path.isfile(path):
            logger.info(f"[PDF-EXTRACTOR] ✓ Encontrado pdftotext en: {path}")
            return path

    found = shutil.which(exe_name)
    if found:
        logger.info(f"[PDF-EXTRACTOR] ✓ Encontrado pdftotext en PATH: {found}")
        return found

    logger.warning(f"[PDF-EXTRACTOR] ✗ pdftotext NO encontrado en ninguna ubicación")
    return None


PDFTOTEXT_EXE = _find_pdftotext_exe()


# ============================================================
# Buscar qpdf para desbloquear PDFs protegidos con contraseña
# ============================================================
def _find_qpdf_exe():
    """
    Busca el ejecutable qpdf en:
    1. Directorio del ejecutable PyInstaller (_MEIPASS o junto al .exe)
    2. Subdirectorio 'poppler' junto al ejecutable
    3. PATH del sistema
    """
    exe_name = "qpdf.exe" if sys.platform == "win32" else "qpdf"
    candidates = []

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        exe_dir = os.path.dirname(sys.executable)
        candidates += [
            os.path.join(base_dir, exe_name),
            os.path.join(base_dir, "poppler", exe_name),
            os.path.join(exe_dir, exe_name),
            os.path.join(exe_dir, "poppler", exe_name),
        ]
    else:
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates += [
            os.path.join(project_dir, "poppler", exe_name),
            os.path.join(project_dir, "bin", exe_name),
        ]

    for path in candidates:
        if os.path.isfile(path):
            logger.info(f"[PDF-EXTRACTOR] ✓ Encontrado qpdf en: {path}")
            return path

    found = shutil.which(exe_name)
    if found:
        logger.info(f"[PDF-EXTRACTOR] ✓ Encontrado qpdf en PATH: {found}")
        return found

    logger.warning("[PDF-EXTRACTOR] qpdf NO encontrado — no se podrán desbloquear PDFs protegidos")
    return None


QPDF_EXE = _find_qpdf_exe()


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


# ============================================================
# Detección y desbloqueo de PDFs protegidos con contraseña
# ============================================================
_PASSWORD_STDERR_KEYWORDS = ("incorrect password", "encrypted", "password", "damaged")


def _is_password_error(stderr_text):
    """Detecta si el stderr de pdftotext indica error por contraseña."""
    lower = stderr_text.lower()
    return any(kw in lower for kw in _PASSWORD_STDERR_KEYWORDS)


def _pdf_is_encrypted(pdf_file_path):
    """
    Comprueba rápidamente si un PDF tiene encriptación usando qpdf --check.
    Retorna True si el archivo está encriptado/protegido.
    """
    if not QPDF_EXE:
        return False
    try:
        result = subprocess.run(
            [QPDF_EXE, "--check", pdf_file_path],
            capture_output=True,
            timeout=15,
        )
        output = (result.stdout + result.stderr).decode("utf-8", errors="replace").lower()
        if "encrypted" in output or "password" in output:
            logger.info(f"[PDF-EXTRACTOR] PDF encriptado detectado: {os.path.basename(pdf_file_path)}")
            return True
        return False
    except Exception as e:
        logger.warning(f"[PDF-EXTRACTOR] No se pudo verificar encriptación con qpdf: {e}")
        return False


def _unlock_pdf(pdf_file_path):
    """
    Intenta desbloquear un PDF protegido usando qpdf --decrypt.
    Prueba primero contraseña vacía (restricción de propietario, caso más común
    en estados de cuenta bancarios) y luego algunas comunes.

    Returns:
        str | None: Ruta al archivo temporal desbloqueado, o None si no fue posible.
        El llamante es responsable de eliminar el archivo temporal.
    """
    if not QPDF_EXE:
        logger.error("[PDF-EXTRACTOR] qpdf no disponible, no se puede desbloquear el PDF")
        return None

    unlocked_path = pdf_file_path + "_unlocked.pdf"
    # Contraseñas a probar: vacía primero (solo restricción de propietario),
    # luego algunas comunes en documentos bancarios mexicanos.
    passwords_to_try = ["", " ", "0000", "1234"]

    for pwd in passwords_to_try:
        # Limpiar intento anterior
        if os.path.isfile(unlocked_path):
            try:
                os.unlink(unlocked_path)
            except OSError:
                pass
        try:
            cmd = [QPDF_EXE, "--decrypt"]
            if pwd:
                cmd += [f"--password={pwd}"]
            cmd += [pdf_file_path, unlocked_path]

            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0 and os.path.isfile(unlocked_path):
                label = repr(pwd) if pwd else "'' (sin contraseña)"
                logger.info(f"[PDF-EXTRACTOR] ✓ PDF desbloqueado con contraseña {label}")
                return unlocked_path

            stderr = result.stderr.decode("utf-8", errors="replace").strip()
            logger.debug(f"[PDF-EXTRACTOR] qpdf falló con contraseña {repr(pwd)}: {stderr}")

        except subprocess.TimeoutExpired:
            logger.warning("[PDF-EXTRACTOR] qpdf timeout al intentar desbloquear")
        except Exception as exc:
            logger.warning(f"[PDF-EXTRACTOR] Error al desbloquear con qpdf: {exc}")

    # Limpiar si quedó algo
    if os.path.isfile(unlocked_path):
        try:
            os.unlink(unlocked_path)
        except OSError:
            pass

    logger.error("[PDF-EXTRACTOR] No se pudo desbloquear el PDF con ninguna contraseña conocida.")
    return None


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
    if sys.platform == "win32":
        env["PATH"] = pdftotext_dir + ";" + env.get("PATH", "")
    else:
        env["PATH"] = pdftotext_dir + ":" + env.get("PATH", "")

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

            # Detectar error por contraseña y reintentar con qpdf
            if _is_password_error(stderr) or result.returncode in (1, 2, 99):
                logger.warning(
                    "[PDF-EXTRACTOR] PDF posiblemente protegido (pdftotext falló). "
                    "Intentando desbloquear con qpdf..."
                )
                unlocked = _unlock_pdf(pdf_file_path)
                if unlocked:
                    try:
                        return _extract_with_pdftotext_exe(unlocked, physical=physical)
                    finally:
                        try:
                            os.unlink(unlocked)
                        except OSError:
                            pass
                else:
                    raise RuntimeError(
                        "El PDF está protegido con contraseña y no se pudo desbloquear "
                        "automáticamente. Por favor, elimine la contraseña manualmente "
                        "y vuelva a subirlo."
                    )

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

    Detecta y desbloquea automáticamente PDFs protegidos con contraseña.
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
                logger.info("[PDF-EXTRACTOR] Usando pdftotext.exe para extraer texto...")
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name

                unlocked_tmp = None
                try:
                    # Pre-verificar encriptación antes de llamar a pdftotext
                    if _pdf_is_encrypted(tmp_path):
                        logger.warning(
                            "[PDF-EXTRACTOR] PDF encriptado (pre-check). "
                            "Desbloqueando antes de extraer texto..."
                        )
                        unlocked_tmp = _unlock_pdf(tmp_path)
                        if not unlocked_tmp:
                            raise RuntimeError(
                                "El PDF está protegido con contraseña y no se pudo desbloquear "
                                "automáticamente. Por favor, elimine la contraseña manualmente "
                                "y vuelva a subirlo."
                            )
                        extract_path = unlocked_tmp
                    else:
                        extract_path = tmp_path

                    self.pages = _extract_with_pdftotext_exe(extract_path, physical=physical)
                finally:
                    for p in filter(None, [tmp_path, unlocked_tmp]):
                        try:
                            os.unlink(p)
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
