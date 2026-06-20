@echo off
REM Sync_Pi4_to_PC.bat v7 - synchronizace souboru z Pi4 do PC
REM Stahne z /home/pi/nextsync/prijate/ -> C:\nextsync\prijate\ a smaze z Pi4
REM Pipne 1x slabe (600Hz, 100ms) JEN kdyz neco stahl

setlocal enabledelayedexpansion

REM Vytvor cilovou slozku pokud neexistuje
if not exist C:\nextsync\prijate mkdir C:\nextsync\prijate

REM Zjisti pocet souboru na Pi4 - spocitej radky z ls primo v BAT
set FCOUNT=0
for /f "delims=" %%L in ('ssh pi@192.168.0.50 "ls /home/pi/nextsync/prijate/"') do (
    set /a FCOUNT+=1
)

if !FCOUNT! equ 0 (
    echo Pi4 nema zadne soubory k prenosu.
    exit /b 0
)

echo Pi4 ma !FCOUNT! souboru, stahuji...

REM Stahni vsechny soubory z Pi4 do PC
scp pi@192.168.0.50:/home/pi/nextsync/prijate/* C:\nextsync\prijate\

if !errorlevel! neq 0 (
    echo CHYBA: SCP stahovani selhalo, soubory na Pi4 zustavaji.
    exit /b 1
)

echo Stahovani OK, mazu soubory z Pi4...

REM Smaz vse z Pi4 (pouze pokud bylo stahnuti uspesne)
ssh pi@192.168.0.50 "rm -f /home/pi/nextsync/prijate/*"

REM Pipni 1x slabe (600Hz, 100ms)
powershell -c "[console]::beep(600,100)"

echo Hotovo.
exit /b 0
