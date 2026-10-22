@echo off
title Building Gulshan AI Passport Studio Executable...
echo ============================================================
echo   Building Standalone Windows Executable (.exe)
echo ============================================================

python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconsole --onefile --name "Gulshan_AI_Passport_Studio" --hidden-import="rembg" --hidden-import="onnxruntime" --hidden-import="PIL" --hidden-import="timm" removeBG.py

echo.
echo ============================================================
echo   Build finished! Check folder: dist\Gulshan_AI_Passport_Studio.exe
echo ============================================================
pause
