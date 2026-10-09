#!/bin/bash
# pi-app-store: 1
# pi-app-store-category: apps
# pi-app-store-description: Webpages as fullscreen Unicode half-block screenshots with selectable HTTP/HTTPS links; no forms.
set -eu
cd -- "$(dirname -- "$0")"
case "${1:-}" in
 install)
  python3 -c 'from pathlib import Path;compile(Path("browser.py").read_bytes(),"browser.py","exec");import PIL,websocket;from browser import chromium;assert chromium(),"Install Chromium first"' ;;
 run) shift;exec python3 browser.py "$@" ;;
 *) echo 'Use: bash app-store.sh install OR bash app-store.sh run';exit 1 ;;
esac
