#!/bin/bash
# panel_update.sh - Stahuje Panel.html z GitHubu pokud je novejsi
# Umisti do /home/pi/nextsync/panel_update.sh

URL="https://kladyx.github.io/panel/Panel.html"
DEST="/home/pi/nextsync/Panel.html"
TMP="/tmp/Panel_new.html"
LOG="/home/pi/nextsync/panel_update.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') Kontroluji GitHub..." >> "$LOG"

# Stahni do tmp
wget -q -O "$TMP" "$URL"

if [ $? -ne 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') CHYBA: wget selhal" >> "$LOG"
  exit 1
fi

# Porovnej s aktualnim souborem
if cmp -s "$TMP" "$DEST"; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') Beze zmeny, preskakuji" >> "$LOG"
  rm -f "$TMP"
  exit 0
fi

# Je rozdil - aktualizuj
cp "$TMP" "$DEST"
rm -f "$TMP"
echo "$(date '+%Y-%m-%d %H:%M:%S') AKTUALIZOVANO - restartuji service" >> "$LOG"

# Restart service
systemctl restart kladyx-uploadserver.service
echo "$(date '+%Y-%m-%d %H:%M:%S') Service restartovana OK" >> "$LOG"

# Drz log max 100 radku
tail -100 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
