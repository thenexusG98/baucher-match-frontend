#!/bin/bash

# Script para incluir librerías de Poppler en el bundle de Tauri
# Esto permite que pdftotext funcione sin que el usuario instale Poppler

set -e

echo "📦 Copiando librerías de Poppler para el bundle..."

# Detectar el sistema operativo
OS=$(uname -s)
ARCH=$(uname -m)

# Directorio destino para las librerías
LIBS_DIR="src-tauri/libs"
mkdir -p "$LIBS_DIR"

if [[ "$OS" == "Darwin" ]]; then
    echo "🍎 Sistema: macOS"
    
    # Verificar si Homebrew está instalado
    if ! command -v brew &> /dev/null; then
        echo "❌ Error: Homebrew no está instalado"
        echo "   Instala Homebrew desde: https://brew.sh"
        exit 1
    fi
    
    # Verificar si poppler está instalado
    if ! brew list poppler &> /dev/null; then
        echo "📥 Instalando poppler..."
        brew install poppler
    fi
    
    # Obtener la ruta de instalación de poppler
    POPPLER_PREFIX=$(brew --prefix poppler)
    
    # Copiar las librerías dinámicas necesarias
    echo "📋 Copiando librerías de $POPPLER_PREFIX/lib/"
    
    # Limpiar directorio anterior
    rm -rf "$LIBS_DIR"/*.dylib 2>/dev/null || true
    
    # Copiar librerías principales de poppler
    cp "$POPPLER_PREFIX/lib/libpoppler.dylib" "$LIBS_DIR/" 2>/dev/null || \
    cp "$POPPLER_PREFIX/lib/libpoppler."*.dylib "$LIBS_DIR/" 2>/dev/null || true
    
    cp "$POPPLER_PREFIX/lib/libpoppler-cpp.dylib" "$LIBS_DIR/" 2>/dev/null || \
    cp "$POPPLER_PREFIX/lib/libpoppler-cpp."*.dylib "$LIBS_DIR/" 2>/dev/null || true
    
    # Copiar dependencias adicionales si existen
    for lib in "$POPPLER_PREFIX/lib"/libpoppler*.dylib; do
        if [ -f "$lib" ]; then
            cp "$lib" "$LIBS_DIR/" 2>/dev/null || true
        fi
    done
    
    echo "✅ Librerías de macOS copiadas"
    
elif [[ "$OS" == "Linux" ]]; then
    echo "🐧 Sistema: Linux"
    
    # Verificar si poppler está instalado
    if ! ldconfig -p | grep -q libpoppler-cpp; then
        echo "⚠️  Poppler no está instalado. Intenta:"
        echo "   Ubuntu/Debian: sudo apt-get install libpoppler-cpp-dev"
        echo "   Fedora/RHEL: sudo dnf install poppler-cpp-devel"
        echo "   Arch: sudo pacman -S poppler"
        exit 1
    fi
    
    # Limpiar directorio anterior
    rm -rf "$LIBS_DIR"/*.so* 2>/dev/null || true
    
    # Encontrar y copiar las librerías
    POPPLER_LIB=$(ldconfig -p | grep libpoppler-cpp.so | awk '{print $NF}' | head -1)
    POPPLER_BASE=$(ldconfig -p | grep 'libpoppler.so ' | awk '{print $NF}' | head -1)
    
    if [ -f "$POPPLER_LIB" ]; then
        cp "$POPPLER_LIB"* "$LIBS_DIR/" 2>/dev/null || true
        echo "✅ Copiada: $(basename $POPPLER_LIB)"
    fi
    
    if [ -f "$POPPLER_BASE" ]; then
        cp "$POPPLER_BASE"* "$LIBS_DIR/" 2>/dev/null || true
        echo "✅ Copiada: $(basename $POPPLER_BASE)"
    fi
    
    echo "✅ Librerías de Linux copiadas"
    
elif [[ "$OS" == MINGW* ]] || [[ "$OS" == MSYS* ]] || [[ "$OS" == CYGWIN* ]]; then
    echo "🪟 Sistema: Windows"
    echo "⚠️  Para Windows, descarga los binarios de Poppler desde:"
    echo "   https://github.com/oschwartz10612/poppler-windows/releases"
    echo ""
    echo "Luego copia las DLLs necesarias a: $LIBS_DIR/"
    echo "  - libpoppler.dll"
    echo "  - libpoppler-cpp.dll"
    echo "  - Todas las dependencias (freetype, jpeg, png, etc.)"
    exit 1
    
else
    echo "❌ Sistema operativo no soportado: $OS"
    exit 1
fi

# Mostrar las librerías copiadas
echo ""
echo "📚 Librerías incluidas en el bundle:"
ls -lh "$LIBS_DIR"

echo ""
echo "✅ Proceso completado"
echo "💡 Ahora puedes ejecutar: npm run build:all"
