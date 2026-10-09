#!/bin/bash
set -eu
cd -- "$(dirname -- "$0")"
PYTHON=python3
if ! command -v python3 >/dev/null; then echo 'Python3 is required.' >&2;exit 1;fi
if command -v apt-get >/dev/null; then
 if [ "$(id -u)" = 0 ];then ROOT=();elif command -v sudo >/dev/null;then ROOT=(sudo);else echo 'Package installation needs root or sudo.' >&2;exit 1;fi
 packages=()
 python3 -c 'import PIL' >/dev/null 2>&1 || packages+=(python3-pil)
 python3 -c 'import websocket' >/dev/null 2>&1 || packages+=(python3-websocket)
 if ! command -v chromium >/dev/null && ! command -v chromium-browser >/dev/null;then packages+=(chromium);fi
 if [ "${#packages[@]}" -gt 0 ];then
  printf 'Installing required Debian packages: %s\n' "${packages[*]}"
  "${ROOT[@]}" apt-get update
  "${ROOT[@]}" apt-get install -y "${packages[@]}"
 fi
else
 echo 'Automatic package installation supports Debian/DietPi apt-get only. Install Pillow, websocket-client and Chromium using your OS package manager.' >&2
 exit 1
fi
python3 -c 'import PIL,websocket;from browser import chromium;assert chromium(),"Chromium executable not found after package installation"'
echo 'Browser dependencies ready.'
