@echo off
rem stop_capture.bat
rem 恢复设置并尝试停止 mitmdump 与本地 http.server

:: 切换到脚本所在目录
cd /d %~dp0

echo === Restoring system proxy settings ===
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v AutoConfigURL /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul

echo === Attempting to stop mitmdump and python servers ===
echo Note: taskkill will terminate all running mitmdump.exe and python.exe processes.
echo If you have other python programs running, consider closing windows manually instead of using taskkill.

taskkill /IM mitmdump.exe /F >nul 2>&1
taskkill /IM python.exe /F >nul 2>&1

echo Done. AutoConfigURL removed and ProxyEnable set to 0.
echo If any capture windows remain, close them manually.
@REM pause
