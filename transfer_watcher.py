#!/usr/bin/env python3
# KladyxTransfer Watcher v3 - Pi4
# Sleduje Firebase RTDB nextsync/transfer/
# Stahuje soubory do /home/pi/nextsync/prijate
# Hraje zvukovy signal po doruceni

import urllib.request
import urllib.parse
import json
import base64
import os
import time
import subprocess

DB_URL = "https://kladyxland-default-rtdb.europe-west1.firebasedatabase.app"
TRANSFER_PATH = "/nextsync/transfer"
DOWNLOAD_DIR = "/home/pi/nextsync/prijate"
CHECK_INTERVAL = 10  # sekund

def play_sound():
    """Zahraje 3x beep pres speaker-test nebo aplay"""
    try:
        # Generuje 3x kratky beep pres Python - nevyzaduje zadny soubor
        for _ in range(3):
            subprocess.run(
                ["speaker-test", "-t", "sine", "-f", "800", "-l", "1", "-s", "1"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=1
            )
            time.sleep(0.2)
    except Exception:
        try:
            # Zaloha - beep pres /dev/tty (konzolovy bell)
            subprocess.run(["bash", "-c", "echo -ne '\\007'"], timeout=1)
        except Exception:
            pass

def get_pending():
    """Nacte vsechny cekajici soubory z Firebase"""
    url = DB_URL + TRANSFER_PATH + ".json"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if data is None:
                return {}
            return data
    except Exception as e:
        print("  -> chyba cteni RTDB:", e)
        return {}

def save_file(safe_name, info):
    """Dekoduje base64 a ulozi soubor"""
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        name = info.get("name", safe_name)
        data_b64 = info.get("data", "")
        if not data_b64:
            print("  -> prazdna data pro:", name)
            return False
        raw = base64.b64decode(data_b64)
        out_path = os.path.join(DOWNLOAD_DIR, name)
        with open(out_path, "wb") as f:
            f.write(raw)
        size_kb = len(raw) // 1024
        print(f"  -> ULOZENO: {name} ({size_kb} KB) -> {out_path}")
        return True
    except Exception as e:
        print("  -> chyba ukladani:", e)
        return False

def delete_rtdb_entry(safe_name):
    """Smaze zaznam z Firebase po uspesnem ulozeni"""
    url = DB_URL + TRANSFER_PATH + "/" + urllib.parse.quote(safe_name, safe="") + ".json"
    try:
        req = urllib.request.Request(url, method="DELETE")
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print("  -> chyba mazani RTDB:", e)

def main():
    print("=" * 50)
    print("KladyxTransfer Watcher v3")
    print("Sleduji RTDB:", DB_URL)
    print("Stahuji do:", DOWNLOAD_DIR)
    print("Interval:", CHECK_INTERVAL, "s")
    print("=" * 50)

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    while True:
        pending = get_pending()
        if pending:
            count = len(pending)
            print(f"\n[+] Nalezeno {count} souboru k doruceni")
            ok_count = 0
            for safe_name, info in pending.items():
                ok = save_file(safe_name, info)
                if ok:
                    delete_rtdb_entry(safe_name)
                    ok_count += 1
            if ok_count > 0:
                print(f"[✓] Doruceno {ok_count} souboru - prehravam signal")
                play_sound()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
