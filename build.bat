@echo off
cd c:\Users\Administrator\Desktop\app\python-miniblink
if not exist "dist" mkdir "dist"
python -m nuitka --standalone --onefile --windows-console-mode=disable --windows-icon-from-ico=app_icon.ico --output-dir="dist" --company="Python MiniBlink" --product-name="Python MiniBlink Browser" --file-version=1.0.0.0 --product-version=1.0.0.0 --include-package=app --include-package=app.core --include-package=app.components --include-data-files="dll/mb132_x64.dll=dll/mb132_x64.dll" --include-data-files="font/Roboto-Light.woff2=font/Roboto-Light.woff2" --include-data-files="font/Roboto-Regular.woff2=font/Roboto-Regular.woff2" --include-data-files="font/Roboto-Medium.woff2=font/Roboto-Medium.woff2" --include-data-files="html/index.html=html/index.html" --include-data-files="app_icon.ico=app_icon.ico" --include-data-files="config/settings.yaml=config/settings.yaml" main.py
pause
