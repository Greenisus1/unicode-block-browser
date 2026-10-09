# Unicode block browser 1.1.0

Standalone fullscreen visual browser. HTTP/HTTPS pages render in a local sandboxed headless Chromium session; pixels become colored Unicode half-blocks. Layouts, images and JavaScript are visible, not HTML-to-text. U enters a URL, arrows/PgUp/PgDn scroll, L opens a selectable list of ordinary HTTP/HTTPS links, Enter follows the chosen link, R reloads, Esc/Q exits. Each manual action makes a normal website request; no automatic refresh loop.

Link navigation is supported, but forms, login, downloads, video controls, arbitrary mouse clicks and JavaScript-only button actions are not. Link text in the chooser is readable text; small webpage text in the screenshot is pixelated and may be unreadable. Screenshots cover a960x2400 viewport, not the entire page. Scroll moves through those captured pixels only. Error pages remain Chromium output, not proof a URL succeeded. A redirect URL is displayed when available.

Python3+curses, Pillow, websocket-client and Chromium required. On Pi/DietPi the distribution packages are chromium, python3-pil and python3-websocket. Installer checks dependencies and compiles source; it does not silently install packages or require root. Missing dependencies stop with their actual import/error message. Chromium sandbox is never disabled; run as non-root.

One temporary profile lasts until quit, so the page can set ordinary temporary cookies while navigating. No owner's saved cookies/passwords, persistent history or account integration. The profile is deleted on quit. Chrome's automation socket binds to loopback; do not use this app on an untrusted shared machine. Pages execute JavaScript inside Chromium's sandbox; this is not a network isolation tool. Sites can log your IP. HTTP is not encrypted. Never put secrets in URLs. File/data/javascript/FTP URLs and embedded credentials are rejected by the address entry and link chooser.

    bash app-store.sh install
    bash app-store.sh run
    python3 browser.py https://example.com
    python3 browser.py --version
    python3 -m unittest -v

Minimum40x12, Unicode monospace terminal recommended;8-color half-blocks, monochrome fallback. View scales to terminal width up to240 columns. Linux6 unit tests and actual sandboxed Chrome local HTTP/JavaScript/link navigation, unsupported-link filtering, temporary-profile cleanup, fullscreen PTY link-selection/resize/exit/restoration checked. Physical Pi and non-Linux untested. MIT license. Not a replacement for a desktop browser.

## 1.1.1 dependency repair

Store installation now checks and installs missing Debian/DietPi packages python3-pil, python3-websocket and chromium using apt-get. It uses root or normal sudo authentication, refreshes apt indexes only when packages are missing, and verifies imports and the Chromium executable afterward. This can download packages and requires network/package-manager access. Unsupported package managers stop with an explicit instruction rather than changing the system Python through pip. Actual DietPi install needs hardware retest; installer branches tested with mock package commands only.
