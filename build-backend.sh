#!/bin/bash

# Script para compilar el backend Python con PyInstaller
# Este script genera ejecutables para la plataforma actual

set -e  # Salir si hay algún error

echo "🔨 Compilando backend FastAPI..."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navegar al directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/backend"

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 no está instalado${NC}"
    exit 1
fi

# Verificar que PyInstaller esté instalado
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo -e "${BLUE}📦 Instalando PyInstaller...${NC}"
    pip3 install pyinstaller
fi

# Crear directorio de binarios si no existe
mkdir -p ../src-tauri/binaries

# Detectar el sistema operativo y arquitectura
OS=$(uname -s)
ARCH=$(uname -m)

# Determinar el nombre del binario según la plataforma
if [[ "$OS" == "Darwin" ]]; then
    if [[ "$ARCH" == "arm64" ]]; then
        BINARY_NAME="backend-api-aarch64-apple-darwin"
    else
        BINARY_NAME="backend-api-x86_64-apple-darwin"
    fi
elif [[ "$OS" == "Linux" ]]; then
    BINARY_NAME="backend-api-x86_64-unknown-linux-gnu"
elif [[ "$OS" == MINGW* ]] || [[ "$OS" == MSYS* ]] || [[ "$OS" == CYGWIN* ]]; then
    BINARY_NAME="backend-api-x86_64-pc-windows-msvc.exe"
else
    echo -e "${RED}❌ Sistema operativo no soportado: $OS${NC}"
    exit 1
fi

echo -e "${BLUE}🔧 Plataforma detectada: $OS ($ARCH)${NC}"
echo -e "${BLUE}📝 Generando binario: $BINARY_NAME${NC}"

# Limpiar builds anteriores
echo -e "${BLUE}🧹 Limpiando builds anteriores...${NC}"
rm -rf build dist

# Compilar con PyInstaller usando el spec file
echo -e "${BLUE}⚙️  Compilando con PyInstaller...${NC}"
python3 -m PyInstaller backend.spec --clean

# Verificar que se haya generado el ejecutable
if [ ! -f "dist/backend-api" ] && [ ! -f "dist/backend-api.exe" ]; then
    echo -e "${RED}❌ Error: No se pudo generar el ejecutable${NC}"
    exit 1
fi

# Copiar el binario al directorio de Tauri con el nombre correcto
if [ -f "dist/backend-api.exe" ]; then
    cp "dist/backend-api.exe" "../src-tauri/binaries/$BINARY_NAME"
    # También copiar con el nombre base para desarrollo
    cp "dist/backend-api.exe" "../src-tauri/binaries/backend-api.exe"
else
    cp "dist/backend-api" "../src-tauri/binaries/$BINARY_NAME"
    chmod +x "../src-tauri/binaries/$BINARY_NAME"
    # También copiar con el nombre base para desarrollo
    cp "dist/backend-api" "../src-tauri/binaries/backend-api"
    chmod +x "../src-tauri/binaries/backend-api"
fi

echo -e "${GREEN}✅ Backend compilado exitosamente${NC}"
echo -e "${GREEN}📦 Binario guardado en: src-tauri/binaries/$BINARY_NAME${NC}"
echo -e "${GREEN}📦 También copiado como: src-tauri/binaries/backend-api${NC}"

# Mostrar tamaño del archivo
FILE_SIZE=$(du -h "../src-tauri/binaries/$BINARY_NAME" | cut -f1)
echo -e "${BLUE}📊 Tamaño del binario: $FILE_SIZE${NC}"

# Limpiar archivos temporales (opcional)
# rm -rf build dist

echo -e "${GREEN}🎉 ¡Proceso completado!${NC}"
