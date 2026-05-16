#!/bin/bash
echo "============================================"
echo " Crosshair Overlay - Build ejecutable"
echo "============================================"
echo

echo "Instalando dependencias..."
pip install pyinstaller PyQt5 --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo al instalar dependencias."
    exit 1
fi

echo "Compilando ejecutable portable..."
pyinstaller --clean crosshair.spec
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo al compilar."
    exit 1
fi

echo
echo "============================================"
echo " Listo! El ejecutable esta en:"
echo " dist/CrosshairOverlay"
echo "============================================"
echo
echo "Copia CrosshairOverlay a cualquier carpeta"
echo "y ejecutalo directamente sin instalacion."
