import subprocess

def remove_package(package_name, source):
    if source == "dnf":
        delete = subprocess.run(
            ["pkexec", "dnf", "-y", "remove", package_name],
            capture_output=True
        )
        autoremove = subprocess.run(
            ["pkexec", "dnf", "-y", "autoremove"],
            capture_output=True
        )
    elif source == "flatpak":
        delete = subprocess.run(
            ["flatpak", "remove", "-y", package_name],
            capture_output=True
        )
    elif source == "apt":
        delete = subprocess.run(
           ["pkexec", "apt", "remove", "-y", package_name],
           capture_output=True 
        )
        autoremove = subprocess.run(
            ["pkexec", "apt", "autoremove", "-y"],
            capture_output=True
        )       
    elif source == "zypper":
        delete = subprocess.run(
            ["pkexec", "zypper", "remove", "-y", package_name],
            capture_output=True
        )
        autoremove = subprocess.run(
            ["pkexec", "zypper", "packages", "--unneeded"],
            capture_output=True
        )
    elif source == "pacman":
        delete = subprocess.run(
            ["pkexec", "pacman", "-Rns", package_name, "--noconfirm"],
            capture_output=True
        )
    return delete.returncode == 0
