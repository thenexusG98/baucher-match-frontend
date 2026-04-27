from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import Response
from app.utils.utils import pattern_date, phrases_to_ignore, partial_phrases_to_ignore
from app.utils.pdf_extractor import PDF, PDFTOTEXT_EXE

from ..services.statement_processor import process_pdf_file, extract_transactions_partial_from_pdf
import shutil
import os
import time
import json
import csv
import re
import logging
import traceback
import asyncio
import subprocess
import sys
import tempfile


def _pdftotext_run(pdf_path: str, password: str = "", physical: bool = False) -> subprocess.CompletedProcess:
    """Ejecuta pdftotext con los argumentos dados y retorna el CompletedProcess."""
    if not PDFTOTEXT_EXE:
        raise RuntimeError("pdftotext no está disponible en el sistema.")
    pdftotext_dir = os.path.dirname(PDFTOTEXT_EXE)
    env = os.environ.copy()
    sep = ";" if sys.platform == "win32" else ":"
    env["PATH"] = pdftotext_dir + sep + env.get("PATH", "")
    cmd = [PDFTOTEXT_EXE]
    if password:
        cmd.extend(["-upw", password])
    if physical:
        cmd.append("-layout")
    cmd.extend(["-enc", "UTF-8", pdf_path, "-"])
    return subprocess.run(cmd, capture_output=True, timeout=60, env=env)


def _is_pdf_locked(pdf_path: str) -> bool:
    """Devuelve True si el PDF requiere contraseña (pdftotext retorna error con mensaje de password)."""
    result = _pdftotext_run(pdf_path)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").lower()
        if "password" in stderr or "encrypted" in stderr or "incorrect" in stderr:
            return True
    return False


def _check_pdf_password(pdf_path: str, password: str) -> bool:
    """Devuelve True si la contraseña es correcta para el PDF protegido."""
    result = _pdftotext_run(pdf_path, password=password)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").lower()
        if "password" in stderr or "incorrect" in stderr:
            return False
    return True

logger = logging.getLogger(__name__)
router  = APIRouter()

def cleanup_files(*file_paths):
    """Elimina archivos temporales después de ser procesados"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Archivo eliminado: {file_path}")
        except Exception as e:
            print(f"Error al eliminar {file_path}: {e}")

@router.get("/health")
async def health_check():
    """Endpoint para verificar que el backend está funcionando"""
    return {
        "status": "ok",
        "message": "Backend FastAPI está funcionando correctamente",
        "service": "baucher-match-backend"
    }


@router.post("/check-pdf-locked")
async def check_pdf_locked(file: UploadFile = File(...)):
    """
    Verifica si un PDF está protegido con contraseña usando pdftotext (Poppler).
    Retorna {"locked": true/false}.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    content = await file.read()
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            locked = _is_pdf_locked(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return {"locked": locked}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar el PDF: {str(e)}")


@router.post("/download-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        start_time = time.time()
        movimientos = process_pdf_file(temp_path)
        execution_time = time.time() - start_time
        
        file_name = temp_path[8:-4].strip().replace(" ", "_")
        
        # Leer JSON en memoria para evitar async file I/O de FileResponse
        with open(movimientos, "rb") as json_read:
            json_content = json_read.read()
        
        # Limpiar archivos temporales de forma sincrónica
        try:
            for fpath in [temp_path, movimientos]:
                if os.path.exists(fpath):
                    os.remove(fpath)
        except Exception:
            pass
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}.json"',
                "X-json": json.dumps({"execution_time": execution_time}),
            }
        )
    
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    

@router.post("/download-csv")
async def upload_csv(
    file: UploadFile = File(...),
    password: str = Form(default="")
):
    logger.info(f"[UPLOAD-CSV] Iniciando procesamiento de archivo: {file.filename}")
    
    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    logger.info(f"[UPLOAD-CSV] Directorio temporal creado: temp/")

    if not file.filename.endswith(".pdf"):
        logger.error(f"[UPLOAD-CSV] Archivo rechazado - no es PDF: {file.filename}")
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    try:
        logger.info(f"[UPLOAD-CSV] Guardando archivo en: {temp_path}")
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        file_size = os.path.getsize(temp_path)
        logger.info(f"[UPLOAD-CSV] Archivo guardado correctamente. Tamaño: {file_size} bytes")

        # Si se proporcionó contraseña, verificar que sea correcta con pdftotext -upw
        if password:
            ok = _check_pdf_password(temp_path, password)
            if not ok:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
                raise HTTPException(status_code=401, detail="Contraseña incorrecta para el PDF protegido.")
            logger.info(f"[UPLOAD-CSV] Contraseña verificada correctamente.")

        start_time = time.time()
        logger.info(f"[UPLOAD-CSV] Llamando a process_pdf_file() en thread pool...")
        loop = asyncio.get_event_loop()
        movimientos_json_path = await loop.run_in_executor(None, process_pdf_file, temp_path, password)
        logger.info(f"[UPLOAD-CSV] process_pdf_file() completado. JSON generado: {movimientos_json_path}")
        execution_time = time.time() - start_time
        logger.info(f"[UPLOAD-CSV] Tiempo de procesamiento PDF: {execution_time:.2f}s")

        # Read JSON data
        logger.info(f"[UPLOAD-CSV] Leyendo datos JSON desde: {movimientos_json_path}")
        with open(movimientos_json_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        logger.info(f"[UPLOAD-CSV] JSON cargado. Total de registros: {len(data) if isinstance(data, list) else 'N/A'}")

        # Prepare CSV path
        file_name = temp_path[8:-4].strip().replace(" ", "_")
        csv_path = f"temp/{file_name}.csv"
        logger.info(f"[UPLOAD-CSV] Ruta CSV preparada: {csv_path}")

        total_abonos = sum(float(item.get('ABONOS', 0)) for item in data if isinstance(item, dict))
        logger.info(f"[UPLOAD-CSV] Total ABONOS calculado: ${total_abonos}")
        
        # Write CSV
        logger.info(f"[UPLOAD-CSV] Escribiendo archivo CSV...")
        if isinstance(data, list) and data:
            keys = data[0].keys()
            logger.info(f"[UPLOAD-CSV] Columnas CSV: {list(keys)}")
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"[UPLOAD-CSV] CSV escrito exitosamente con {len(data)} registros")
        else:
            logger.error(f"[UPLOAD-CSV] Datos JSON inválidos. Tipo: {type(data)}, Contenido: {data}")
            raise HTTPException(status_code=422, detail="El archivo JSON no contiene datos válidos para CSV.")

        # Programar eliminación de archivos temporales DESPUES de leer el CSV
        logger.info(f"[UPLOAD-CSV] Leyendo CSV en memoria para enviar...")
        with open(csv_path, "rb") as csv_read:
            csv_content = csv_read.read()
        logger.info(f"[UPLOAD-CSV] CSV leido en memoria: {len(csv_content)} bytes")
        
        # Ahora sí podemos eliminar los archivos
        try:
            for fpath in [temp_path, movimientos_json_path, csv_path]:
                if os.path.exists(fpath):
                    os.remove(fpath)
                    logger.info(f"[UPLOAD-CSV] Archivo temporal eliminado: {fpath}")
        except Exception as cleanup_err:
            logger.warning(f"[UPLOAD-CSV] Error limpiando temporales: {cleanup_err}")

        po = json.dumps({"execution_time": execution_time, "total_count": len(data), "income_month": total_abonos})
        logger.info(f"[UPLOAD-CSV] Response metadata: {po}")

        # Devolver el CSV directamente como bytes (sin FileResponse que usa async file I/O)
        response = Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}.csv"',
                "X-json": po,
            }
        )
        logger.info(f"[UPLOAD-CSV] Procesamiento completado exitosamente. Enviando {len(csv_content)} bytes")
        return response
    
    except ValueError as ve:
        logger.error(f"[UPLOAD-CSV] ValueError: {ve}", exc_info=True)
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF: {ve}")
    except Exception as e:
        logger.error(f"[UPLOAD-CSV] Error inesperado: {str(e)}", exc_info=True)
        logger.error(f"[UPLOAD-CSV] Traceback completo:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")




@router.post("/extract-partial-json")
async def extract_transactions_json(
    file: UploadFile = File(...),
    output_format: str = Query("json", description="Formato de salida: ndjson o json", regex="^(ndjson|json)$")
):
    """
    Extrae transacciones de un PDF de estado de cuenta bancario.
    
    Formato esperado del PDF:
    - Línea 1: Concepto/Descripción
    - Línea 2: Fecha (dd-mm) + Montos ($ cargo $ abono $ saldo)
    - Línea 3: Información adicional (códigos, folios, etc.)
    """
    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        start_time = time.time()
        results = []

        # Expresiones regulares
        money_re = re.compile(r"\$\s?[\d,]+\.\d{2}")
        date_re = re.compile(r"^\s*\d{2}-\d{2}\b")
        folio_re = re.compile(r"FOLIO[:\s]*[:#\-]?\s*([0-9]+)", re.IGNORECASE)

        with open(temp_path, "rb") as f:
            pdf = PDF(f, physical=True)
            
            # Unificar todas las líneas de todas las páginas
            all_lines = []
            for page in pdf:
                all_lines.extend(page.split("\n"))
            
            # Procesar línea por línea
            i = 0
            while i < len(all_lines):
                line = all_lines[i].strip()
                
                # Ignorar líneas vacías o encabezados
                if not line or any(phrase in line for phrase in partial_phrases_to_ignore):
                    i += 1
                    continue
                
                # Buscar línea con fecha (indica una transacción)
                date_match = date_re.search(line)
                if not date_match:
                    i += 1
                    continue
                
                # === TRANSACCIÓN ENCONTRADA ===
                fecha = date_match.group(0).strip()
                
                # Extraer montos de esta línea
                amounts = [amt.replace(" ", "") for amt in money_re.findall(line)]
                
                # CONCEPTO: revisar línea ANTERIOR
                concepto = None
                if i > 0:
                    prev = all_lines[i-1].strip()
                    if prev and not date_re.search(prev) and not any(ph in prev for ph in partial_phrases_to_ignore):
                        # Si tiene montos, tomar solo la parte antes del $
                        concepto = prev.split('$')[0].strip() if '$' in prev else prev
                
                # Si no hay concepto anterior, buscar en la línea actual (después de fecha)
                if not concepto:
                    after_date = line[date_match.end():].strip()
                    if after_date and '$' in after_date:
                        concepto = after_date.split('$')[0].strip()
                
                # Limpiar uno o más prefijos de fecha al inicio del concepto (ej: "02/ENE 01/ENE") a
                if concepto:
                    concepto = re.sub(r"^(\d{1,2}/[A-Za-z]{3}\s+)+", "", concepto).strip() 
                
                # INFORMACIÓN ADICIONAL: revisar líneas SIGUIENTES (folios, códigos)
                folio = None
                next_info = []
                j = i + 1
                while j < len(all_lines) and len(next_info) < 2:
                    nxt = all_lines[j].strip()
                    if not nxt:
                        j += 1
                        continue
                    # Si encontramos otra fecha, detenemos
                    if date_re.search(nxt):
                        break
                    # Si no tiene montos, es información adicional
                    if not money_re.search(nxt):
                        next_info.append(nxt)
                        # Buscar FOLIO
                        fm = folio_re.search(nxt)
                        if fm:
                            folio = fm.group(1)
                    j += 1
                
                # ASIGNAR MONTOS
                cargo = abono = saldo = None
                if len(amounts) == 1:
                    abono = amounts[0]
                elif len(amounts) == 2:
                    # Determinar si es cargo o abono por palabras clave
                    if concepto and any(k in concepto.upper() for k in ["CHEQUE", "PAGADO", "COMPRA", "CARGO"]):
                        cargo, saldo = amounts
                    else:
                        abono, saldo = amounts
                elif len(amounts) >= 3:
                    cargo, abono, saldo = amounts[0], amounts[1], amounts[2]
                
                # Ajuste especial para cheques
                if concepto and "CHEQUE PAGADO" in concepto.upper() and abono and not cargo:
                    cargo = abono
                    abono = None
                
                # RAW LINES para debugging
                raw = []
                if i > 0 and all_lines[i-1].strip():
                    raw.append(all_lines[i-1].strip())
                raw.append(line)
                raw.extend(next_info)
                
                # Agregar transacción
                results.append({
                    "fecha": fecha,
                    "concepto": concepto,
                    "folio": folio,
                    "cargo": cargo,
                    "abono": abono,
                    "saldo": saldo,
                    "raw_lines": raw
                })
                
                i += 1

        # Guardar resultados según formato solicitado
        file_name = temp_path[5:-4].strip().replace(" ", "_")
        if output_format == "json":
            # Generar JSON directamente en memoria
            json_content = json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8")
            
            # Limpiar archivos temporales
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
            
            return Response(
                content=json_content,
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="{file_name}_transactions.json"',
                }
            )
        else:
            # Generar NDJSON directamente en memoria
            ndjson_lines = [json.dumps(obj, ensure_ascii=False) for obj in results]
            ndjson_content = ("\n".join(ndjson_lines) + "\n").encode("utf-8")
            
            # Limpiar archivos temporales
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
            
            return Response(
                content=ndjson_content,
                media_type="application/x-ndjson",
                headers={
                    "Content-Disposition": f'attachment; filename="{file_name}_transactions.json"',
                }
            )

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    


@router.post("/extract-partial-csv")
async def extract_transactions_csv(
    file: UploadFile = File(...),
    password: str = Form(default="")
):
    """
    Extrae transacciones de un PDF de estado de cuenta bancario y retorna un archivo CSV.
    Soporta PDFs protegidos con contraseña mediante el parámetro `password`.
    
    Formato esperado del PDF:
    - Línea 1: Concepto/Descripción
    - Línea 2: Fecha (dd-mm) + Montos ($ cargo $ abono $ saldo)
    - Línea 3: Información adicional (códigos, folios, etc.)
    """
    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Si se proporcionó contraseña, verificar que sea correcta con pdftotext -upw
        if password:
            ok = _check_pdf_password(temp_path, password)
            if not ok:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
                raise HTTPException(status_code=401, detail="Contraseña incorrecta para el PDF protegido.")
            # La contraseña es correcta: pdftotext la usará con -upw al procesar

        start_time = time.time()
        results = []

        # Expresiones regulares
        money_re = re.compile(r"\$\s?[\d,]+\.\d{2}")
        date_re = re.compile(r"^\s*\d{2}-\d{2}\b")
        folio_re = re.compile(r"FOLIO[:\s]*[:#\-]?\s*([0-9]+)", re.IGNORECASE)

        with open(temp_path, "rb") as f:
            pdf = PDF(f, physical=True, password=password)
            
            # Unificar todas las líneas de todas las páginas
            all_lines = []
            for page in pdf:
                all_lines.extend(page.split("\n"))
            
            # Procesar línea por línea
            i = 0
            while i < len(all_lines):
                line = all_lines[i].strip()
                
                # Ignorar líneas vacías o encabezados
                if not line or any(phrase in line for phrase in partial_phrases_to_ignore):
                    i += 1
                    continue
                
                # Buscar línea con fecha (indica una transacción)
                date_match = date_re.search(line)
                if not date_match:
                    i += 1
                    continue
                
                # === TRANSACCIÓN ENCONTRADA ===
                fecha = date_match.group(0).strip()
                
                # Extraer montos de esta línea
                amounts = [amt.replace(" ", "") for amt in money_re.findall(line)]
                
                # CONCEPTO: revisar línea ANTERIOR
                concepto = None
                numero_control = None
                
                if i > 0:
                    prev = all_lines[i-1].strip()
                    if prev and not date_re.search(prev) and not any(ph in prev for ph in partial_phrases_to_ignore):
                        # Si tiene montos, tomar solo la parte antes del $
                        concepto = prev.split('$')[0].strip() if '$' in prev else prev
                
                # Si no hay concepto anterior, buscar en la línea actual (después de fecha)
                if not concepto:
                    after_date = line[date_match.end():].strip()
                    if after_date and '$' in after_date:
                        concepto = after_date.split('$')[0].strip()
                        # Buscar número de control en la misma línea (formato: 000ITCV21690056)
                        nc_inline = re.search(r"(?:\d{3})?(?:ITCV)?(\d{2}69\d{4})", concepto)
                        if nc_inline:
                            numero_control = nc_inline.group(1)
                            # Limpiar el número de control del concepto
                            concepto = re.sub(r"/?\d{3}?ITCV?\d{2}69\d{4}", "", concepto).strip()
                
                # Limpiar uno o más prefijos de fecha al inicio del concepto (ej: "02/ENE 01/ENE")
                if concepto:
                    concepto = re.sub(r"^(\d{1,2}/[A-Za-z]{3}\s+)+", "", concepto).strip()
                
                # INFORMACIÓN ADICIONAL: revisar líneas SIGUIENTES (folios, códigos)
                folio = None
                next_info = []
                j = i + 1
                while j < len(all_lines) and len(next_info) < 2:
                    nxt = all_lines[j].strip()
                    
                    # Buscar número de control en las líneas siguientes
                    # Patrón 1: ITCV21690160 (con prefijo ITCV)
                    # Patrón 2: 23690586 (solo dígitos con 69 en medio)
                    if not numero_control:
                        nc = re.search(r"(?:ITCV)?(\d{2}69\d{4})", nxt)
                        if nc:
                            numero_control = nc.group(1)
                    
                    if not nxt:
                        j += 1
                        continue
                    # Si encontramos otra fecha, detenemos
                    if date_re.search(nxt):
                        break
                    # Si no tiene montos, es información adicional
                    if not money_re.search(nxt):
                        next_info.append(nxt)
                        # Buscar FOLIO
                        fm = folio_re.search(nxt)
                        if fm:
                            folio = fm.group(1)
                    j += 1
                
                # ASIGNAR MONTOS
                cargo = abono = saldo = None
                if len(amounts) == 1:
                    abono = amounts[0]
                elif len(amounts) == 2:
                    # Determinar si es cargo o abono por palabras clave
                    if concepto and any(k in concepto.upper() for k in ["CHEQUE", "PAGADO", "COMPRA", "CARGO"]):
                        cargo, saldo = amounts
                    else:
                        abono, saldo = amounts
                elif len(amounts) >= 3:
                    cargo, abono, saldo = amounts[0], amounts[1], amounts[2]
                
                # Ajuste especial para cheques
                if concepto and "CHEQUE PAGADO" in concepto.upper() and abono and not cargo:
                    cargo = abono
                    abono = None
                
                # Agregar transacción (sin raw_lines para CSV)
                results.append({
                    "fecha": fecha,
                    "concepto": concepto,
                    "folio": folio,
                    "cargo": cargo,
                    "abono": abono,
                    "saldo": saldo,
                    "numero_control": numero_control
                })
                
                i += 1

        # Guardar resultados en formato CSV
        file_name = temp_path[5:-4].strip().replace(" ", "_")
        csv_path = f"temp/{file_name}_transactions.csv"
        
        if results:
            keys = results[0].keys()
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
        else:
            raise HTTPException(status_code=422, detail="No se encontraron transacciones en el PDF.")
        
        execution_time = time.time() - start_time
        
        # Leer CSV en memoria para evitar async file I/O de FileResponse
        with open(csv_path, "rb") as csv_read:
            csv_content = csv_read.read()
        
        # Limpiar archivos temporales de forma sincrónica
        try:
            for fpath in [temp_path, csv_path]:
                if os.path.exists(fpath):
                    os.remove(fpath)
        except Exception:
            pass
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}_transactions.csv"',
                "X-Execution-Time": str(execution_time),
            }
        )

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
