#!/bin/bash

INSTALL_DIR="$HOME/.local/lib/"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps/"
LAUNCHER_DIR="$HOME/.local/bin"

mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$HOME/.local/share/icons/"
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.local/share/icons/hicolor/512x512/apps/"

cp -r program_uninstaller $INSTALL_DIR
cp program-uninstaller.desktop $DESKTOP_DIR
cp program-uninstaller.png $ICON_DIR
cp pu_launcher.sh $LAUNCHER_DIR
cd $LAUNCHER_DIR
chmod +x pu_launcher.sh

if command -v dnf &>/dev/null; then
    sudo dnf install -y python3
    python3 -m venv ~/.local/lib/program_uninstaller/venv
    ~/.local/lib/program_uninstaller/venv/bin/pip install textual
elif command -v pacman &>/dev/null; then
    sudo pacman -S python3 --noconfirm
    python3 -m venv ~/.local/lib/program_uninstaller/venv
    ~/.local/lib/program_uninstaller/venv/bin/pip install textual
elif command -v apt &>/dev/null; then
    sudo apt install -y python3 python3-venv
    python3 -m venv ~/.local/lib/program_uninstaller/venv
    ~/.local/lib/program_uninstaller/venv/bin/pip install textual
elif command -v zypper &>/dev/null; then
    sudo zypper install -y python3
    python3 -m venv ~/.local/lib/program_uninstaller/venv
    ~/.local/lib/program_uninstaller/venv/bin/pip install textual
fi
