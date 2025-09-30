@echo off
:: MAC Changer Windows Launcher
:: This batch file runs the MAC changer with administrator privileges

echo MAC Address Changer - Windows Launcher
echo ==========================================

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges...
    echo.
    goto :run_script
) else (
    echo This script requires Administrator privileges.
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:run_script
:: Change to script directory
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

:: If no arguments provided, show interface list
if "%1"=="" (
    echo No arguments provided. Showing available interfaces...
    echo.
    python mac_changer.py --list
    echo.
    echo Usage examples:
    echo   %0 --interface "Wi-Fi" --random
    echo   %0 --interface "Ethernet" --mac "00:11:22:33:44:55"
    echo   %0 --help
    pause
    exit /b 0
)

:: Run the script with provided arguments
python mac_changer.py %*
echo.
pause