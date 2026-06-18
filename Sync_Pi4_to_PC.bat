@echo off
REM Sync_Pi4_to_PC.bat - automaticka synchronizace souboru z Pi4 do PC pri startu
REM Spousti se z autostartu Windows
REM Stahne vse z /home/pi/nextsync/prijate/ -> C:\nextsync\prijate\ a smaze z Pi4

REM Pockame 30s na pripojeni site po startu
timeout /t 30 /nobreak >nul

REM Vytvor cilovou slozku pokud neexistuje
if not exist "C:\nextsync\prijate" mkdir "C:\nextsync\prijate"

REM Stahni vsechny soubory z Pi4 do PC
scp -o StrictHostKeyChecking=no pi@192.168.0.50:/home/pi/nextsync/prijate/* "C:\nextsync\prijate\" 2>nul

REM Smaz vse z Pi4 (pouze pokud bylo stahnuti uspesne)
if %errorlevel% equ 0 (
    ssh -o StrictHostKeyChecking=no pi@192.168.0.50 "rm -f /home/pi/nextsync/prijate/*" 2>nul
)

REM Pipni 3x ze je hotovo
powershell -c "[console]::beep(800,200); Start-Sleep -m 100; [console]::beep(800,200); Start-Sleep -m 100; [console]::beep(800,200)"

exit
