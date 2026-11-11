@echo off
:: Personal Life Vault - Firewall & ADB Setup (Run as Administrator)
echo =========================================
echo  Personal Life Vault - Setup Script
echo =========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Please run this script as Administrator!
    echo Right-click setup_firewall.bat and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/3] Opening Windows Firewall port 8088 for inbound connections...
netsh advfirewall firewall delete rule name="PersonalLifeVault-8088-Inbound" >nul 2>&1
netsh advfirewall firewall add rule name="PersonalLifeVault-8088-Inbound" dir=in action=allow protocol=TCP localport=8088 profile=any description="Personal Life Vault sync server"
if %errorlevel% equ 0 (
    echo     [OK] Port 8088 inbound rule added.
) else (
    echo     [WARN] Could not add firewall rule. Check manually.
)

echo.
echo [2/3] Checking ADB for USB connection...
set ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe
if exist "%ADB%" (
    echo     Found ADB at: %ADB%
    "%ADB%" devices
    echo.
    echo     Setting up adb reverse tcp:8088...
    "%ADB%" reverse tcp:8088 tcp:8088
    if %errorlevel% equ 0 (
        echo     [OK] adb reverse configured. Phone can now reach server via 127.0.0.1:8088
    ) else (
        echo     [WARN] adb reverse failed. Phone may not be connected via USB.
        echo           Use your LAN IP instead: run 'ipconfig' and look for your Wi-Fi or Ethernet IP.
    )
) else (
    echo     [WARN] ADB not found. Skipping adb reverse.
)

echo.
echo [3/3] Printing your laptop network addresses...
echo     Phone should use one of these IPs to reach the server on port 8088:
ipconfig | findstr /i "IPv4"
echo.
echo =========================================
echo  Setup Complete.
echo  Start server with: npm start
echo  In the Android app, set Server URL to:
echo    http://YOUR_LAN_IP:8088
echo    (e.g., http://10.49.230.52:8088)
echo  OR connect USB and use:
echo    http://127.0.0.1:8088  (via adb reverse)
echo =========================================
pause
