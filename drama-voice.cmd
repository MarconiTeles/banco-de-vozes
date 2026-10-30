@echo off
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%~dp0banco_vozes.py" run %*
exit /b %ERRORLEVEL%
