#!/usr/bin/env python3
"""KLADYX Pi Transfer Watcher v1.0.Kl
Sleduje nextsync/transfer_to_pi a stahuje soubory na Pi4.
Uklada do /home/pi/prijate/
"""
import os,json,time,base64,urllib.request

VERSION="1.0.Kl"
FB_URL="https://kladyxland-default-rtdb.europe-west1.firebasedatabase.app"
NODE="nextsync/transfer_to_pi"
SAVE_DIR="/home/pi/prijate"
POLL_SEC=30

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}",flush=True)

def fb_get(path):
    r=urllib.request.urlopen(f"{FB_URL}/{path}.json")
    return json.loads(r.read().decode())

def fb_delete(path):
    req=urllib.request.Request(f"{FB_URL}/{path}.json",method='DELETE')
    urllib.request.urlopen(req)

def fb_put(path,val):
    data=json.dumps(val).encode()
    req=urllib.request.Request(f"{FB_URL}/{path}.json",data=data,method='PUT',headers={'Content-Type':'application/json'})
    urllib.request.urlopen(req)

def process():
    try:
        shallow=fb_get(f"{NODE}?shallow=true")
        if not shallow:
            return
        for key in shallow:
            try:
                entry=fb_get(f"{NODE}/{key}")
                if not entry:
                    continue
                name=entry.get("name","unknown")
                data=entry.get("data","")
                if "," in data:
                    data=data.split(",")[1]
                raw=base64.b64decode(data)
                os.makedirs(SAVE_DIR,exist_ok=True)
                fpath=os.path.join(SAVE_DIR,name)
                with open(fpath,"wb") as f:
                    f.write(raw)
                log(f"SAVED: {name} ({len(raw)} B)")
                fb_delete(f"{NODE}/{key}")
                fb_put("piTransfer/lastReceived",{"name":name,"ts":int(time.time()*1000),"size":len(raw)})
            except Exception as e:
                log(f"ERR file {key}: {e}")
    except Exception as e:
        if "null" not in str(e).lower():
            log(f"ERR poll: {e}")

def main():
    log(f"KLADYX Pi Transfer Watcher v{VERSION}")
    log(f"Dir: {SAVE_DIR} | Poll: {POLL_SEC}s")
    os.makedirs(SAVE_DIR,exist_ok=True)
    while True:
        process()
        time.sleep(POLL_SEC)

if __name__=="__main__":
    main()
