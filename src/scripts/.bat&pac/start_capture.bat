echo === Starting mitmdump (127.0.0.1:8080) ===
start "mitmdump" cmd /k "mitmdump -v -q --listen-host 127.0.0.1 --listen-port 8080 -s "%~dp0mitm_filter.py""

echo.
echo Capture started.
echo - PAC: %PAC_URL%
echo - mitmdump: http://127.0.0.1:8080
echo
echo To stop and restore settings, run stop_capture.bat
pause