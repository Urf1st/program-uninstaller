# Program Uninstaller

TUI application for removing packages and searching for leftovers on Linux.

> [!WARNING]
> This is an alpha version and has not been thoroughly tested. Use at your own risk. Read carefully what exactly you are removing from your device.

## Features
- Remove packages via pacman, dnf, apt, zypper, flatpak.
- Search for leftover files in ~/.config, ~/.local, ~/.cache
- Clean TUI interface.

## Supported Package Managers
- Arch Linux (pacman)
- Fedora/RHEL (dnf)
- Debian/Ubuntu/Mint (apt)
- openSUSE (zypper)

## Requirements
Python 3
PIP
Textual

## Installation
You can install app and dependencies using installation script `install-pu.sh`. It includes all required packages.
```
git clone https://github.com/Urf1st/program-uninstaller
cd program-uninstaller
bash install_pu.sh
```
## Usage
```bash
yourhomedir/.local/lib/program_uninstaller/venv/bin/python3 yourhomedir/.local/lib/program_uninstaller/tui_app.py
```
or through app menu of your DE.

## Contributing
- Contributions to improve the TUI design are welcome.
- If you are able to do it would be great to have fully functional GUI.

## Roadmap
- Uninstalling script.
- Flatpak version.
- "Hunter mode".
- pip version.
- More search paths for leftovers.
- Better search logic (lower and upper case).

## Acknowledgements
TUI was developed with assistance from Claude (Anthropic). Inspired by Revo Uninstaller.

## LICENSE
MIT
