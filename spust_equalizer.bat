@echo off
title KLADYX Audio Analyzer
REM Pockej 60s az se Windows plne nastartuje a sit je pripravena
timeout /t 60 /nobreak
cd C:\Users\klady\Desktop
python audio_analyzer.py
