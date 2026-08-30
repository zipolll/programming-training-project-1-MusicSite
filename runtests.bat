@echo off
cd /d "%~dp0"

echo 1. Catalog test
echo 2. Analysis test
echo 3. Crawler test
set /p choice=Please enter 1, 2 or 3: 

if "%choice%"=="1" goto catalog
if "%choice%"=="2" goto analysis
if "%choice%"=="3" goto crawler

echo Invalid choice.
goto end

:catalog
".venv\Scripts\python.exe" manage.py test catalog
goto end

:analysis
".venv\Scripts\python.exe" -m unittest analysis.tests
goto end

:crawler
".venv\Scripts\python.exe" -m unittest crawler.tests

:end
pause
