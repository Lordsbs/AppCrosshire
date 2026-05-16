@echo off
echo ============================================
echo  Crosshair Overlay - Build ejecutable
echo ============================================
echo.

echo Instalando dependencias...
pip install pyinstaller PyQt5 --quiet
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias.
    pause
    exit /b 1
)

echo Compilando ejecutable portable...
python -m PyInstaller --clean crosshair.spec
if errorlevel 1 (
    echo ERROR: Fallo al compilar.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Listo! El ejecutable esta en:
echo  dist\CrosshairOverlay.exe
echo ============================================
echo.
echo Copia CrosshairOverlay.exe a cualquier carpeta
echo y ejecutalo directamente sin instalacion.
pause
