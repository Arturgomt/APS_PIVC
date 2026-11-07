@echo off
rem Inicia MySQL, API e front-end do IRIS. Para encerrar, feche as janelas abertas.
set MYSQL=C:\mysql\mysql-8.0.42-winx64\bin
cd /d "%~dp0"

tasklist /fi "imagename eq mysqld.exe" | find /i "mysqld.exe" >nul || start "MySQL" /min "%MYSQL%\mysqld.exe" --defaults-file=C:\mysql\my.ini --console
echo Aguardando o MySQL...
:espera
"%MYSQL%\mysqladmin.exe" -uroot -h127.0.0.1 ping >nul 2>&1 || (timeout /t 1 /nobreak >nul & goto espera)

start "API IRIS" cmd /k ".venv\Scripts\python.exe api.py"
start "Site IRIS" cmd /k "cd frontend && npm run dev"
timeout /t 6 /nobreak >nul
start http://localhost:5173
