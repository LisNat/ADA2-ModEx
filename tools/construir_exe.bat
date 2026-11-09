@echo off
rem Genera dist\ModEx.exe a partir de src\gui.py. Ejecutar desde cualquier carpeta.
cd /d "%~dp0\.."
python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name ModEx --paths src src\gui.py
echo.
echo Listo: dist\ModEx.exe
pause
