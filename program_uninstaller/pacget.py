import os
import sys
import subprocess
import pathlib
import shutil

def detect_package_managers():
    managers = []
    
    if shutil.which("pacman"):
        managers.append("pacman")
    if shutil.which("dnf"):
        managers.append("dnf")
    if shutil.which("apt"):
        managers.append("apt")
    if shutil.which("zypper"):
        managers.append("zypper")
    if shutil.which("flatpak"):
        managers.append("flatpak")
    if not managers:
        print("None of the package managers found on your system")
    
    return managers


def get_packages(manager):
    packages = []
    
    if manager == "pacman":
        result = subprocess.run(
            ["pacman", "-Qq"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                packages.append({"name": line, "source": "pacman"})
    
    elif manager == "flatpak":
        result = subprocess.run(
            ["flatpak", "list", "--app", "--columns=name,application"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("\t")
                if len(parts) == 2:
                    packages.append({
                        "name": parts[0],
                        "app_id": parts[1],
                        "source": "flatpak"
                    })
    elif manager == "dnf":
        result = subprocess.run(
            ["rpm", "-qa", "--queryformat", "%{NAME}\n"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                packages.append({"name": line, "source": "dnf"})
    elif manager == "zypper":
        result = subprocess.run(
            ["rpm", "-qa", "--queryformat", "%{NAME}\n"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                packages.append({"name": line, "source": "zypper"})
    elif manager == "apt":
        result = subprocess.run(
            ["apt-mark", "showmanual"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                packages.append({"name": line, "source": "apt"})
    
    return packages


def get_all_packages() -> list[dict]:
    managers = detect_package_managers()
    all_packages = []
    
    for manager in managers:
        all_packages.extend(get_packages(manager))
    
    return all_packages
    
