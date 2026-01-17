@echo off
cd /d %~dp0
if not exist "dist" mkdir "dist"

python -m nuitka --standalone --onefile ^
--windows-console-mode=attach ^
--windows-icon-from-ico=app_icon.ico ^
--output-dir="dist" ^
--company="Python MiniBlink" ^
--product-name="Python MiniBlink Browser" ^
--file-version=1.0.0.0 ^
--product-version=1.0.0.0 ^
--include-package=app ^
--include-package=app.core ^
--include-package=app.components ^
--include-data-files="dll/mb132_x64.dll=dll/mb132_x64.dll" ^
--include-data-dir="font=font" ^
--include-data-dir="html=html" ^
--include-data-dir="config=config" ^
--include-data-files="app_icon.ico=app_icon.ico" ^
main.py

pause
