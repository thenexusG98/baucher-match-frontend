from app.utils.utils import pattern_date, phrases_to_ignore, partial_phrases_to_ignore
from app.utils.functions import clean_total_movements_line, extract_fields
from app.utils.pdf_extractor import PDF
 
import re 
import json
import logging

logger = logging.getLogger(__name__)
data = []

def extract_transactions_from_pdf(pdf_name):
    logger.info(f"[EXTRACT-TRANS] Iniciando extracción de transacciones desde: {pdf_name}")
    analyze = False
    data = []
    analyze = False
    data_line = []

    try:
        logger.info(f"[EXTRACT-TRANS] Abriendo archivo PDF...")
        with open(pdf_name, "rb") as file:
            logger.info(f"[EXTRACT-TRANS] Creando objeto PDF...")
            pdf = PDF(file, physical=True)
            total_pages = len(pdf)
            logger.info(f"[EXTRACT-TRANS] PDF cargado. Total de páginas: {total_pages}")
            
            for page_num, page in enumerate(pdf, 1):
                logger.debug(f"[EXTRACT-TRANS] Procesando página {page_num}/{total_pages}")
                lines = page.split("\n")
                logger.debug(f"[EXTRACT-TRANS] Página {page_num} tiene {len(lines)} líneas")

                for line_num, line in enumerate(lines, 1):
                    line = line.strip() 

                    if any(phrase in line for phrase in phrases_to_ignore):
                        continue

                    if "FECHA" in line:
                        logger.debug(f"[EXTRACT-TRANS] Encabezado FECHA encontrado en página {page_num}, línea {line_num}")
                        analyze = True
                        continue

                    if "TOTAL MOVIMIENTOS ABONOS" in line:
                        logger.debug(f"[EXTRACT-TRANS] TOTAL MOVIMIENTOS encontrado en página {page_num}, línea {line_num}")
                        analyze = True
                        movements = clean_total_movements_line(line)
                        break

                    if analyze:
                        line = line.replace(',', '') 
                        if re.match(pattern_date, line):  
                            if data_line: 
                                data.append(data_line)
                            data_line = line  
                        else:
                            if data_line: 
                                data_line += " " + line

        if data_line:
            data.append(data_line)
        
        logger.info(f"[EXTRACT-TRANS] Extracción completada. Total de transacciones: {len(data)}")

        if data:
            last_record = data[-1]
            match_last_ref = re.search(r"Ref\. \**\d+", last_record)
            if match_last_ref:
                text_cleaned = last_record[:match_last_ref.end()]
                data[-1] = text_cleaned
                logger.info(f"[EXTRACT-TRANS] Última transacción limpiada")
            else:
                text_cleaned = last_record
        
        return data
        
    except Exception as e:
        logger.error(f"[EXTRACT-TRANS] Error durante extracción: {str(e)}", exc_info=True)
        raise

def process_pdf_file(pdf_path):
    file_name = pdf_path[8:-4].strip().replace(" ", "_")
    logger.info(f"[PROCESS-PDF] Iniciando procesamiento: {pdf_path[8:-4]}")
    logger.info(f"[PROCESS-PDF] Nombre de archivo procesado: {file_name}")
    json_result = []

    try:
        logger.info(f"[PROCESS-PDF] Llamando a extract_transactions_from_pdf()...")
        extracted_data = extract_transactions_from_pdf(pdf_path)
        logger.info(f"[PROCESS-PDF] Datos extraídos: {len(extracted_data)} registros")
        
        if not extracted_data:
            logger.warning(f"[PROCESS-PDF] No se encontraron transacciones en el PDF")
        
        for idx, data in enumerate(extracted_data, 1):
            logger.debug(f"[PROCESS-PDF] Procesando registro {idx}/{len(extracted_data)}: {data[:100]}...")
            result = extract_fields(data)
            json_result.append(result)
            logger.debug(f"[PROCESS-PDF] Registro {idx} procesado: {result}")
        logger.info(f"[PROCESS-PDF] Todos los {len(extracted_data)} registros procesados exitosamente")

        json_file_path = f"{file_name}.json"
        logger.info(f"[PROCESS-PDF] Escribiendo JSON en: {json_file_path}")
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(json_result, json_file, ensure_ascii=False, indent=4)
        
        logger.info(f"[PROCESS-PDF] JSON escrito exitosamente con {len(json_result)} registros")
        return json_file_path
        
    except Exception as e:
        logger.error(f"[PROCESS-PDF] Error durante procesamiento: {str(e)}", exc_info=True)
        raise




def extract_transactions_partial_from_pdf(pdf_name):
    analyze = False
    data = []
    analyze = False
    data_line = []

    with open(pdf_name, "rb") as file:
        pdf = PDF(file)
        for page in pdf:
            
            lines = page.split("\n")
            data.append(lines)
            print(lines)

            #for line in lines:
                
                #line = line.strip() 

                #if any(phrase in line for phrase in partial_phrases_to_ignore):
                #        continue
                
                # Detect table-like structures in the PDF lines
                #if re.search(r"\b\d{2}/\d{2}/\d{4}\b", line):  # Example: date pattern at start of table row
                    
                 #   analyze = True

                #if analyze:
                #if "Fecha" in line:
                #    analyze = True
                 #   continue

                #if analyze:
                 #   line = line.replace(',', '') 
                  #  print(line)
                
                #print(line)  # Debugging line to see the content being processed
