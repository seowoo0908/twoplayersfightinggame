@echo off
set PYTHONPATH=C:\Users\user\AppData\Local\Programs\Python\Python312\Lib\site-packages
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" main.py
if errorlevel 1 (
    echo Error running the game
    pause
)
