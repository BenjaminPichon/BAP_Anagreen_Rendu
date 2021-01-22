@echo off

start launch_server.bat

timeout /t 5 /nobreak > NUL

start http://127.0.0.1:50007/

exit