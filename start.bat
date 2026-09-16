@echo off
cd /d "%~dp0"
echo.
echo  Komp:   http://127.0.0.1:8000
echo  Telefon (odin Wi-Fi):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do echo           http://%%a:8000
echo.
".venv\Scripts\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8000
pause
