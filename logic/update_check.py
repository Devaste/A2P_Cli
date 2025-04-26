import requests
import os
import sys

LATEST_VERSION_URL = "https://raw.githubusercontent.com/Devaste/A2P_Cli/main/VERSION"
RELEASES_URL = "https://github.com/Devaste/A2P_Cli/releases/latest"

def resource_path(relative_path):
    # Handles PyInstaller's _MEIPASS for bundled data files
    # PyInstaller sets _MEIPASS for bundled data files. Access is required and documented by PyInstaller (safe to ignore protected member warning).
    if hasattr(sys, '_MEIPASS'):  # noqa: SLF001
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), '..', relative_path)

def get_local_version():
    try:
        with open(resource_path('VERSION'), encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return None

def get_latest_version():
    try:
        resp = requests.get(LATEST_VERSION_URL, timeout=5)
        if resp.ok:
            return resp.text.strip()
    except Exception:
        pass
    return None

def check_for_update():
    local_version = get_local_version()
    latest_version = get_latest_version()
    if not local_version or not latest_version:
        return  # Silently skip if cannot check
    if latest_version != local_version:
        print(f"\nUpdate available: {latest_version} (You have {local_version})")
        print(f"Visit {RELEASES_URL} to download the latest version.\n")
