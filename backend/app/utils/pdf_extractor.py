"""
PDF Text Extractor con fallback automático
Intenta usar pdftotext, si no está disponible usa PyMuPDF
"""

try:
    import pdftotext
    USE_PDFTOTEXT = True
except ImportError:
    import fitz  # PyMuPDF
    USE_PDFTOTEXT = False
    print("[INFO] pdftotext no disponible, usando PyMuPDF como alternativa")


class PDF:
    """
    Wrapper que proporciona la misma interfaz que pdftotext.PDF
    pero funciona con PyMuPDF si pdftotext no está disponible
    """
    
    def __init__(self, file, physical=False):
        """
        Args:
            file: file object opened in binary mode
            physical: bool - usar layout físico (mantiene posiciones)
        """
        self.physical = physical
        self.pages = []
        
        if USE_PDFTOTEXT:
            # Usar pdftotext original
            pdf_obj = pdftotext.PDF(file, physical=physical)
            self.pages = [page for page in pdf_obj]
        else:
            # Usar PyMuPDF como alternativa
            pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                if physical:
                    # Extraer texto manteniendo layout físico (similar a pdftotext physical=True)
                    # Usar "blocks" para mantener posiciones relativas
                    text = page.get_text("text", sort=True)
                else:
                    # Extraer texto simple
                    text = page.get_text()
                
                self.pages.append(text)
            
            pdf_doc.close()
    
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
    return "pdftotext" if USE_PDFTOTEXT else "PyMuPDF"
