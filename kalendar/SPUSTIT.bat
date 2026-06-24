@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Plánovač aktivít

echo.
echo  ================================================
echo   PLANOVAC PRACOVNYCH AKTIVIT
echo  ================================================
echo.

:: Skontroluj Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [CHYBA] Python nie je nainstalovany!
    echo.
    echo  Stiahni ho z: https://www.python.org/downloads/
    echo  Pri instalacii zaskrtni "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Nainštaluj Flask ak chýba
echo  Kontrolujem Flask...
python -m pip install flask --quiet 2>nul

:: Zisti lokálnu IP adresu
echo.
echo  Adresa pre kolegov (skopiruj a posli im):
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=* delims= " %%b in ("%%a") do (
        echo     http://%%b:5050
    )
)
echo.
echo  ================================================
echo  Posli kolegom adresu - otvoria v prehliadaci
echo  Server NESMIE byt vypnuty kym kolegovia pracuju
echo  ================================================
echo.
echo  Server bezi... zatvor toto okno = vypnes server
echo.

:: Spusti server
cd /d "%~dp0"
python app.py
pause
