@echo off
title NTL-SysToolbox Launcher
color 07

echo ========================================
echo    NTL-SysToolbox - Lanceur
echo ========================================
echo.
echo Demarrage du systeme...
echo.

:: Lancement du script Python
python ntl_systoolbox.py

:: Si le script se termine, afficher un message
echo.
echo ========================================
echo Programme termine
echo ========================================
pause
