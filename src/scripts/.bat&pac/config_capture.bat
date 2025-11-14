@echo off
rem start_capture.bat
rem 一键：启动本地 PAC 服务、设置系统使用 PAC、启动 mitmdump 进行拦截

:: 切换到脚本所在目录
cd /d %~dp0

echo === Starting PAC HTTP server (port 8000) ===
start "PAC Server" cmd /k "python -m http.server 8000 --bind 127.0.0.1"

echo Waiting 1 second for server to start...
ping -n 2 127.0.0.1 >nul

:: 设置系统 AutoConfigURL 指向本地 PAC
set PAC_URL=http://127.0.0.1:8000/proxy.pac
echo Setting AutoConfigURL to %PAC_URL%
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v AutoConfigURL /t REG_SZ /d "%PAC_URL%" /f >nul

:: 确保全局 ProxyEnable 为 0（禁用传统全局代理）
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul

