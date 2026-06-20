import urllib.request
import urllib.parse
import json
import base64
import os
import time

DB_URL = "https://kladyxland-default-rtdb.europe-west1.firebasedatabase.app"
TRANSFER_PATH = "/nextsync/transfer"
DOWNLOAD_DIR = "/home/pi/nextsync/prijate"
CHECK_INTERVAL = 10

def play_sound():
    pass

def get_pending():
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
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        name = info.get("name", safe_name)
        data_b64 = info.get("data", "")
        if not data_b64:
            return False
        raw = base64.b64decode(data_b64)
        out_path = os.path.join(DOWNLOAD_DIR, name)
        with open(out_path, "wb") as f:
            f.write(raw)
        print("  -> ULOZENO:", name, "->", out_path)
        return True
    except Exception as e:
        print("  -> Chyba ukladani:", e)
        return False

def delete_rtdb_entry(safe_name):
    url = DB_URL + TRANSFER_PATH + "/" + urllib.parse.quote(safe_name, safe="") + ".json"
    try:
        req = urllib.request.Request(url, method="DELETE")
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print("  -> Chyba mazani RTDB:", e)

def main():
    print("KladyxTransfer Watcher v3 (Pi4 Linux)")
    print("Stahuji do:", DOWNLOAD_DIR)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    while True:
        pending = get_pending()
        if pending:
            for safe_name, info in pending.items():
                if save_file(safe_name, info):
                    delete_rtdb_entry(safe_name)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()